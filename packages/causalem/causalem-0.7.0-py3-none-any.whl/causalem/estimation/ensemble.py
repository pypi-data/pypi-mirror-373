"""
Ensemble-matching TE estimator
===============================

Features
--------
* **Deterministic reproducibility** with a single `random_state_master`.
  Every source of randomness (CV shuffling, stochastic
  matching, Random-Forest, bootstrap) is driven by integers drawn from a
  master NumPy Generator, so results are bit-identical across platforms
  and parallel runs.
* Optional **bootstrap percentile CIs** (`nboot`, `alpha`, `n_jobs`,
  `random_state_boot`).  During bootstrap the *same* reproducibility
  logic is applied inside each worker.
* When `niter==1` and the outcome is not survival the meta-learner is
  bypassed automatically.

!!!  When `nboot>0` the `groups` argument is ignored (row-level resampling).

---------------------------------------------------------------------------
"""

from __future__ import annotations

import math
import warnings
from typing import Any, Optional

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator, clone
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import GroupKFold, KFold, cross_val_predict
from sklearn.preprocessing import OneHotEncoder
from sksurv.ensemble import RandomSurvivalForest
from sksurv.functions import StepFunction
from sksurv.linear_model import CoxPHSurvivalAnalysis

from causalem import stochastic_match
from causalem.utils._survival import fit_cox_marginal_weighted
from causalem.utils._weights import appearance_weights, fit_with_appearance_weights


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _make_splitter(
    *,
    n_splits: int,
    shuffle: bool,
    seed: int,
    groups: Optional[np.ndarray],
):
    """Return a cross-validation splitter.

    When ``groups`` is ``None`` a :class:`~sklearn.model_selection.KFold`
    instance seeded with ``seed`` is returned.  Otherwise a
    :class:`~sklearn.model_selection.GroupKFold` is used.  Newer versions of
    scikit-learn allow ``shuffle`` and ``random_state`` for ``GroupKFold`` but
    older ones do not, so those arguments are ignored when unsupported.
    """
    if groups is None:
        return KFold(n_splits=n_splits, shuffle=shuffle, random_state=seed)

    try:
        return GroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=seed)
    except TypeError:  # older scikit-learn
        return GroupKFold(n_splits=n_splits)


# --------------------------------------------------------------------------- #
# Numerical utilities                                                         #
# --------------------------------------------------------------------------- #
def clip_logit(
    p: np.ndarray,
    eps: float,
) -> np.ndarray:
    """
    Clip probabilities to [eps, 1-eps], then return log(p / (1-p)).
    """
    p_clipped = np.clip(p, eps, 1 - eps)
    return np.log(p_clipped / (1 - p_clipped))


# --------------------------------------------------------------------------- #
# Survival helpers                                                            #
# --------------------------------------------------------------------------- #
def _simulate_from_sf(
    sf: StepFunction,
    n_draws: int,
    tau: float,
    rng: np.random.Generator,
):
    """
    Draw (time, event) samples from a survival curve.

    Parameters
    ----------
    sf       : sksurv.functions.StepFunction – survival curve S(t)
    n_draws  : int                          – # Monte-Carlo draws
    tau      : float                        – admin-censoring horizon (inf → none)
    rng      : np.random.Generator          – RNG

    Returns
    -------
    times  : ndarray (n_draws,)  – observed follow-up times
    events : ndarray (n_draws,)  – event indicators {0,1}
    """
    u = rng.random(n_draws)
    S = sf.y
    t_knots = sf.x
    rev_idx = np.searchsorted(S[::-1], u, side="right")
    idx = len(S) - rev_idx

    times = np.full(n_draws, np.inf)
    valid = idx < len(t_knots)
    times[valid] = t_knots[idx[valid]]

    if math.isfinite(tau):
        events = times <= tau
        times = np.minimum(times, tau)
    else:
        events = np.isfinite(times)
    return times, events


def _hr_dict_to_df(hr_dict: dict[tuple[str, str], float]) -> pd.DataFrame:
    """Convert pairwise HR dictionary to DataFrame with ``te`` column."""
    rows = [(k[0], k[1], v) for k, v in hr_dict.items()]
    return pd.DataFrame(rows, columns=["treatment_1", "treatment_2", "te"])


# --------------------------------------------------------------------------- #
# Stage-1 single iteration                                                    #
# --------------------------------------------------------------------------- #
def stage_1_single_iter(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng: np.random.Generator,
    outcome_is_binary: bool,
    groups: Optional[np.ndarray] = None,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    model_outcome=RandomForestRegressor(n_estimators=100),
    matching_is_stochastic: bool = True,
    prob_clip_eps: float = 1e-6,
):
    """One iteration of outcome modelling with matching.

    Parameters
    ----------
    Xraw, treatment, y : arrays
        Raw covariates, treatment indicator and outcome.
    rng : numpy.random.Generator
        Source of randomness for CV splits and matching.
    outcome_is_binary : bool
        ``True`` for binary outcomes in which case class probabilities are
        predicted.
    groups : ndarray or None, optional
        Group labels for cross-validation, triggering ``GroupKFold`` when not
        ``None``.

    Returns
    -------
    cluster_ids : ndarray
        Cluster identifiers for the matching draw (``-1`` for unmatched).
    y_pred, y_pred_cf : ndarray
        Out-of-sample predictions for factual and counterfactual outcomes.
    """

    # Provide a default learner when none is supplied
    if model_outcome is None:
        model_outcome = RandomForestRegressor(n_estimators=100)

    # No feature subsetting
    X = Xraw

    X_t = np.hstack((X, treatment.reshape(-1, 1)))
    X_t_cf = np.hstack((X, (1 - treatment).reshape(-1, 1)))

    # --- propensity CV -----------------------------------------------------
    splitter_prop = _make_splitter(
        n_splits=n_splits_propensity,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )

    # --- propensity CV & logit --------------------------------------------
    oos_proba = cross_val_predict(
        clone(model_propensity),
        X,
        treatment,
        cv=splitter_prop,
        method="predict_proba",
        groups=groups,
    )[:, 1]
    oos_scores = clip_logit(oos_proba, eps=prob_clip_eps)

    # --- matching ----------------------------------------------------------
    cluster_ids = stochastic_match(
        treatment=treatment,
        score=oos_scores,
        scale=matching_scale,
        caliper=matching_caliper,
        nsmp=1 if matching_is_stochastic else 0,
        random_state=int(rng.integers(2**32)),
    ).ravel()
    matched_idx = np.where(cluster_ids != -1)[0]

    # --- outcome cross-fitting --------------------------------------------
    splitter_out = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )
    y_pred = np.full(X_t.shape[0], np.nan)
    y_pred_cf = np.full(X_t.shape[0], np.nan)

    for tr_idx, te_idx in splitter_out.split(X_t, groups=groups):
        matched_tr = np.intersect1d(matched_idx, tr_idx)
        if matched_tr.size == 0:
            continue
        rf = clone(model_outcome)
        if "random_state" in rf.get_params(deep=False):
            rf.set_params(random_state=int(rng.integers(2**32)))
        rf.fit(X_t[matched_tr], y[matched_tr])

        if outcome_is_binary and hasattr(rf, "predict_proba"):
            y_pred[te_idx] = rf.predict_proba(X_t[te_idx])[:, 1]
            y_pred_cf[te_idx] = rf.predict_proba(X_t_cf[te_idx])[:, 1]
        else:
            y_pred[te_idx] = rf.predict(X_t[te_idx])
            y_pred_cf[te_idx] = rf.predict(X_t_cf[te_idx])

    return cluster_ids, y_pred, y_pred_cf


# ------------------------------------------------------------------ #
# Outcome-model templating                                           #
# ------------------------------------------------------------------ #


def _setup_outcome_models(model_outcome, niter: int):
    """
    Expand *model_outcome* into a list of length `niter`.

    Accepts
    -------
    • single estimator ........................ cloned `niter` times
    • list / tuple of estimators .............. must have ≥ niter items
    • generator / iterator yielding estimators  first `niter` are consumed

    Returns
    -------
    list[BaseEstimator]
    """
    # single estimator -------------------------------------------------
    if isinstance(model_outcome, BaseEstimator):
        return [clone(model_outcome) for _ in range(niter)]

    # list / tuple -----------------------------------------------------
    if isinstance(model_outcome, (list, tuple)):
        if len(model_outcome) < niter:
            raise ValueError("`model_outcome` list shorter than niter.")
        return [clone(m) for m in model_outcome[:niter]]

    # generator / iterator --------------------------------------------
    if hasattr(model_outcome, "__iter__"):
        templates = []
        it = iter(model_outcome)
        for _ in range(niter):
            try:
                templates.append(clone(next(it)))
            except StopIteration:
                raise ValueError(
                    "Generator for model_outcome yielded fewer than niter estimators."
                )
        return templates

    raise TypeError(
        "`model_outcome` must be an estimator, a list/tuple of estimators, "
        "or a generator yielding estimators."
    )


# --------------------------------------------------------------------------- #
# Stage-1 single iteration – SURVIVAL (cross-fit, covariate-adjusted HR)      #
# --------------------------------------------------------------------------- #
def _estimate_te_survival_single_iter(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng: np.random.Generator,
    # ---- design & matching -------------------------------------------------
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    groups: Optional[np.ndarray] = None,
    matching_is_stochastic: bool = True,
    # ---- outcome modelling -------------------------------------------------
    n_splits_outcome: int = 5,
    model_outcome: Optional[BaseEstimator] = None,
    n_mc: int = 1,
    administrative_censoring: bool = True,
    **kwargs,
) -> tuple[float, np.ndarray]:
    """Single iteration survival TE on that iteration's matched set.

    Cross-fits a survival outcome model on the matched units, simulates
    ``n_mc`` draws from the factual and counterfactual survival curves and
    fits a marginal Cox model on those rows to obtain a hazard ratio.
    """
    # No feature subsetting
    X = Xraw

    # ------------ 1. Propensity CV  ----------------------------------------
    splitter_prop = _make_splitter(
        n_splits=n_splits_propensity,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )
    oos_scores = cross_val_predict(
        clone(model_propensity),
        X,
        treatment,
        cv=splitter_prop,
        method="predict_proba",
        groups=groups,
    )
    eps = 1e-6
    p1 = np.clip(oos_scores[:, 1], eps, 1 - eps)
    logit_ps = np.log(p1 / (1 - p1))

    # ------------ 2. Matching ----------------------------------------------
    cluster_ids = stochastic_match(
        treatment=treatment,
        score=logit_ps,
        scale=matching_scale,
        caliper=matching_caliper,
        nsmp=1 if matching_is_stochastic else 0,
        random_state=int(rng.integers(2**32)),
    ).ravel()
    matched_idx = np.where(cluster_ids != -1)[0]
    if matched_idx.size == 0:
        raise ValueError("No matches found – relax caliper/scale.")

    # ------------ 3. Cross-fit outcome model -------------------------------

    # ---- choose survival learner -------------------------------------
    if model_outcome is None:
        model_outcome = RandomSurvivalForest(
            n_estimators=200,
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=1,
        )

    X_t = np.hstack((X, treatment.reshape(-1, 1)))
    X_t_cf = np.hstack((X, (1 - treatment).reshape(-1, 1)))

    # containers for predicted survival functions
    sf_factual = [None] * X.shape[0]
    sf_counter = [None] * X.shape[0]

    surv_y = np.array(
        list(zip(y[:, 1] == 1, y[:, 0])),
        dtype=[("event", "bool"), ("time", "f8")],
    )

    splitter_out = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )

    for fold, (tr_idx, te_idx) in enumerate(splitter_out.split(X_t, groups=groups)):
        matched_tr = np.intersect1d(matched_idx, tr_idx)
        if matched_tr.size == 0:
            # No matched data in training part of this fold – skip
            continue

        mdl = clone(model_outcome)
        if "random_state" in mdl.get_params(deep=False):
            mdl.set_params(random_state=int(rng.integers(2**32)))
        mdl.fit(X_t[matched_tr], surv_y[matched_tr])

        sf_te_f = mdl.predict_survival_function(X_t[te_idx], return_array=False)
        sf_te_cf = mdl.predict_survival_function(X_t_cf[te_idx], return_array=False)
        for pos, idx in enumerate(te_idx):
            sf_factual[idx] = sf_te_f[pos]
            sf_counter[idx] = sf_te_cf[pos]

    # ensure every matched observation received predictions
    if any(sf_factual[i] is None or sf_counter[i] is None for i in matched_idx):
        raise ValueError(
            "Some matched units lack survival predictions – "
            "increase n_splits_outcome or review data."
        )
    idx = matched_idx

    # ------------ 4. Monte-Carlo simulation --------------------------------
    t_f = np.empty((len(idx), n_mc))
    e_f = np.empty((len(idx), n_mc), dtype=bool)
    t_cf = np.empty_like(t_f)
    e_cf = np.empty_like(e_f)

    tau = float(y[:, 0].max()) if administrative_censoring else math.inf
    for pos, i in enumerate(idx):
        if sf_factual[i] is None or sf_counter[i] is None:
            raise ValueError("Missing survival prediction for a matched row.")
        rng_i = np.random.default_rng(int(rng.integers(2**32)))
        t_f[pos], e_f[pos] = _simulate_from_sf(sf_factual[i], n_mc, tau, rng_i)
        t_cf[pos], e_cf[pos] = _simulate_from_sf(sf_counter[i], n_mc, tau, rng_i)

    times = np.concatenate([t_f.ravel(), t_cf.ravel()])
    events = np.concatenate([e_f.ravel(), e_cf.ravel()])
    d = np.concatenate([np.ones_like(t_f).ravel(), np.zeros_like(t_cf).ravel()])

    synth = np.array(
        list(zip(events == 1, times)), dtype=[("event", "bool"), ("time", "f8")]
    )
    cox = CoxPHSurvivalAnalysis().fit(pd.DataFrame({"d": d}), synth)
    hr = float(np.exp(cox.coef_[0]))
    return hr, cluster_ids


def stage_1_meta_survival(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng_master: np.random.Generator,
    outcome_templates: list[BaseEstimator],
    niter: int,
    model_meta: Optional[BaseEstimator] = None,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    matching_is_stochastic: bool = True,
    groups: Optional[np.ndarray] = None,
    prob_clip_eps: float = 1e-6,
) -> tuple[
    np.ndarray,
    list[StepFunction | None],
    list[StepFunction | None],
    np.ndarray,
]:
    """Cross-fit a survival meta-learner with appearance weights.

    Base survival models are fitted ``niter`` times. Their predictions form the
    design for a Cox meta-learner that is trained on the **matched union** and
    weighted by each row's appearance count.  Returns the matched-union indices,
    lists of factual and counterfactual survival functions and the cluster
    matrix of matches.
    """

    surv_y = np.array(
        list(zip(y[:, 1] == 1, y[:, 0])),
        dtype=[("event", "bool"), ("time", "f8")],
    )

    results = []
    cluster_list = []
    for i in range(niter):
        rng_iter = np.random.default_rng(int(rng_master.integers(2**32)))
        res = stage_1_single_iter(
            Xraw,
            treatment,
            surv_y,
            rng=rng_iter,
            outcome_is_binary=False,
            groups=groups,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            model_outcome=outcome_templates[i],
            matching_is_stochastic=matching_is_stochastic,
            prob_clip_eps=prob_clip_eps,
        )
        results.append(res)
        cluster_list.append(res[0])
    cluster_mat = np.column_stack(cluster_list)
    weights = appearance_weights(cluster_mat).astype(float)
    matched_union = np.where(weights > 0)[0]

    pred_mat = np.column_stack([r[1] for r in results])
    pred_cf_mat = np.column_stack([r[2] for r in results])

    X_meta = np.hstack((pred_mat, treatment.reshape(-1, 1)))
    X_meta_cf = np.hstack((pred_cf_mat, (1 - treatment).reshape(-1, 1)))

    if model_meta is None:
        model_meta = CoxPHSurvivalAnalysis()

    splitter_meta = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng_master.integers(2**32)),
        groups=groups,
    )

    sf_factual = [None] * Xraw.shape[0]
    sf_counter = [None] * Xraw.shape[0]

    for tr_idx, te_idx in splitter_meta.split(X_meta, groups=groups):
        matched_tr = np.intersect1d(matched_union, tr_idx)
        if matched_tr.size == 0:
            raise ValueError(
                "No matched units in training set. "
                "Try increasing `matching_scale` or `matching_caliper`."
            )
        mdl = clone(model_meta)
        if "random_state" in mdl.get_params(deep=False):
            mdl.set_params(random_state=int(rng_master.integers(2**32)))
        fit_with_appearance_weights(
            mdl,
            X_meta[matched_tr],
            surv_y[matched_tr],
            sample_weight=weights[matched_tr],
        )

        sf_te = mdl.predict_survival_function(X_meta[te_idx], return_array=False)
        sf_te_cf = mdl.predict_survival_function(X_meta_cf[te_idx], return_array=False)
        for pos, idx in enumerate(te_idx):
            sf_factual[idx] = sf_te[pos]
            sf_counter[idx] = sf_te_cf[pos]

    return matched_union, sf_factual, sf_counter, cluster_mat


def stage_1_meta_survival_multi(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng_master: np.random.Generator,
    outcome_templates: list[BaseEstimator],
    niter: int,
    model_meta: Optional[BaseEstimator] = None,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    matching_is_stochastic: bool = True,
    groups: Optional[np.ndarray] = None,
    prob_clip_eps: float = 1e-6,
    ref_group: int | str | None = None,
) -> tuple[np.ndarray, list[list[StepFunction | None]], np.ndarray, np.ndarray,]:
    """Cross-fit a survival meta-learner for multiple treatments.

    Iterative base learners supply survival predictions for each arm. A Cox
    meta-learner is fitted on the **matched union** with appearance weights and
    produces survival functions per treatment. Returns matched-union indices,
    survival-function lists for all arms, treatment names and the cluster
    matrix.
    """

    surv_y = np.array(
        list(zip(y[:, 1] == 1, y[:, 0])), dtype=[("event", "bool"), ("time", "f8")]
    )

    results = []
    cluster_list = []
    for i in range(niter):
        rng_iter = np.random.default_rng(int(rng_master.integers(2**32)))
        res = stage_1_single_iter_multi(
            Xraw,
            treatment,
            surv_y,
            rng=rng_iter,
            outcome_is_binary=False,
            groups=groups,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            model_outcome=outcome_templates[i],
            matching_is_stochastic=matching_is_stochastic,
            prob_clip_eps=prob_clip_eps,
            ref_group=ref_group,
        )
        results.append(res)
        cluster_list.append(res[0])

    treatment_names = results[0][3]
    cluster_mat = np.column_stack(cluster_list)
    weights = appearance_weights(cluster_mat).astype(float)
    matched_union = np.where(weights > 0)[0]

    pred_mat = np.column_stack([r[1] for r in results])
    pred_all_arms = []
    for j in range(len(treatment_names)):
        pred_all_arms.append(np.column_stack([r[2][j] for r in results]))

    enc = OneHotEncoder(sparse_output=False, handle_unknown="error")
    enc.fit(treatment.reshape(-1, 1))
    X_meta = np.hstack((pred_mat, enc.transform(treatment.reshape(-1, 1))))

    X_meta_all_arms = []
    for name in treatment_names:
        X_meta_all_arms.append(
            np.hstack(
                (
                    pred_all_arms[treatment_names.tolist().index(name)],
                    enc.transform(np.full(treatment.shape, name).reshape(-1, 1)),
                )
            )
        )

    if model_meta is None:
        model_meta = CoxPHSurvivalAnalysis()

    splitter_meta = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng_master.integers(2**32)),
        groups=groups,
    )

    sf_all_arms = [[None] * Xraw.shape[0] for _ in treatment_names]

    for tr_idx, te_idx in splitter_meta.split(X_meta, groups=groups):
        matched_tr = np.intersect1d(matched_union, tr_idx)
        if matched_tr.size == 0:
            raise ValueError(
                "No matched units in training set. "
                "Try increasing `matching_scale` or `matching_caliper`."
            )
        mdl = clone(model_meta)
        if "random_state" in mdl.get_params(deep=False):
            mdl.set_params(random_state=int(rng_master.integers(2**32)))
        fit_with_appearance_weights(
            mdl,
            X_meta[matched_tr],
            surv_y[matched_tr],
            sample_weight=weights[matched_tr],
        )

        for k, X_meta_single_arm in enumerate(X_meta_all_arms):
            sf_tmp = mdl.predict_survival_function(
                X_meta_single_arm[te_idx], return_array=False
            )
            for pos, idx in enumerate(te_idx):
                sf_all_arms[k][idx] = sf_tmp[pos]

    return matched_union, sf_all_arms, treatment_names, cluster_mat


# --------------------------------------------------------------------------- #
# Survival-path placeholder (multi-iter loop)                                 #
# --------------------------------------------------------------------------- #
def _estimate_te_survival(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng_master: np.random.Generator,
    outcome_templates: list[BaseEstimator],
    niter: int,
    model_meta: Optional[BaseEstimator] = None,
    n_mc: int = 1,
    administrative_censoring: bool = True,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    matching_is_stochastic: bool = True,
    groups: Optional[np.ndarray] = None,
    prob_clip_eps: float = 1e-6,
    do_stacking: bool = True,
) -> dict:
    """Estimate TE for survival outcomes.

    When ``do_stacking`` is ``True`` a Cox meta-learner is fitted on stacked
    predictions from ``niter`` base learners.  The meta-learner and final
    marginal hazard ratio are **appearance-weighted** over the matched union.
    When ``do_stacking`` is ``False`` each iteration produces an HR on that
    iteration's matched set and the geometric mean (unweighted) is returned.
    """
    if niter == 1:
        do_stacking = False

    if not do_stacking:
        hr_list = []
        cluster_list = []
        for i in range(niter):
            rng_iter = np.random.default_rng(int(rng_master.integers(2**32)))
            hr_i, cid = _estimate_te_survival_single_iter(
                Xraw,
                treatment,
                y,
                rng=rng_iter,
                n_splits_propensity=n_splits_propensity,
                model_propensity=model_propensity,
                matching_scale=matching_scale,
                matching_caliper=matching_caliper,
                n_splits_outcome=n_splits_outcome,
                model_outcome=outcome_templates[i],
                matching_is_stochastic=matching_is_stochastic,
                n_mc=n_mc,
                administrative_censoring=administrative_censoring,
            )
            hr_list.append(math.log(hr_i))
            cluster_list.append(cid)

        hr = float(np.exp(np.mean(hr_list)))
        cluster_mat = np.column_stack(cluster_list)
        return {"te": hr, "matching": cluster_mat}

    matched_union, sf_fact, sf_cf, cluster_mat = stage_1_meta_survival(
        Xraw,
        treatment,
        y,
        rng_master=rng_master,
        outcome_templates=outcome_templates,
        niter=niter,
        model_meta=model_meta,
        n_splits_propensity=n_splits_propensity,
        model_propensity=model_propensity,
        matching_scale=matching_scale,
        matching_caliper=matching_caliper,
        n_splits_outcome=n_splits_outcome,
        matching_is_stochastic=matching_is_stochastic,
        groups=groups,
        prob_clip_eps=prob_clip_eps,
    )

    idx = matched_union
    t_f = np.empty((len(idx), n_mc))
    e_f = np.empty((len(idx), n_mc), dtype=bool)
    t_cf = np.empty_like(t_f)
    e_cf = np.empty_like(e_f)

    tau = float(y[:, 0].max()) if administrative_censoring else math.inf
    for pos, i in enumerate(idx):
        if sf_fact[i] is None or sf_cf[i] is None:
            raise ValueError("Missing survival prediction for a matched row.")
        rng_i = np.random.default_rng(int(rng_master.integers(2**32)))
        t_f[pos], e_f[pos] = _simulate_from_sf(sf_fact[i], n_mc, tau, rng_i)
        t_cf[pos], e_cf[pos] = _simulate_from_sf(sf_cf[i], n_mc, tau, rng_i)

    times = np.concatenate([t_f.ravel(), t_cf.ravel()])
    events = np.concatenate([e_f.ravel(), e_cf.ravel()])
    d = np.concatenate([np.ones_like(t_f).ravel(), np.zeros_like(t_cf).ravel()])

    synth = np.array(
        list(zip(events == 1, times)), dtype=[("event", "bool"), ("time", "f8")]
    )
    w_all = appearance_weights(cluster_mat)
    w_rows = np.concatenate([np.repeat(w_all[idx], n_mc), np.repeat(w_all[idx], n_mc)])
    hr = fit_cox_marginal_weighted(d, synth, w_rows)
    return {"te": hr, "matching": cluster_mat}


# --------------------------------------------------------------------------- #
# Full estimator (bootstrap + fast-path)                                      #
# --------------------------------------------------------------------------- #
def estimate_te(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    groups: Optional[np.ndarray] = None,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    model_outcome=None,
    outcome_type: Optional[str] = None,  # "continuous" | "binary" | "survival"
    niter: int = 10,
    matching_is_stochastic: bool = True,
    do_stacking: bool = True,
    prob_clip_eps: float = 1e-6,
    n_mc: int = 1,
    # --- RNG control ------------------------------------------------------
    random_state_master: Optional[int] = None,
    # --- bootstrap options -----------------------------------------------
    nboot: int = 0,
    alpha: float = 0.05,
    n_jobs: int = -1,
    random_state_boot: Optional[int] = None,
    model_meta: Optional[object] = None,
    ref_group: int | str | None = None,
):
    """Estimate the average treatment effect via ensemble matching.

    The estimator performs cross-fitted propensity modelling, stochastic (or
    deterministic) matching, outcome modelling and optionally bootstrap
    resampling.  When ``niter`` is ``1`` and ``outcome_type`` is not
    ``"survival"`` the meta-learner is bypassed automatically.

    Parameters
    ----------
    Xraw : ndarray of shape (n, p)
        Raw covariate matrix.
    treatment : ndarray of shape (n,)
        Binary or multi-level treatment indicator.
    y : ndarray
        Outcome.  For survival outcomes pass a ``(time, event)`` pair per
        observation.
    groups : ndarray or None, optional
        Group labels used for cross-validation splits.
    n_splits_propensity : int, default ``5``
        Number of folds for propensity-score cross-fitting.
    model_propensity : estimator, default ``LogisticRegression``
        Classifier used to estimate propensity scores.
    matching_scale : float, default ``1.0``
        Scale parameter passed to :func:`stochastic_match`.
    matching_caliper : float or None, default ``None``
        Maximum allowable matching distance.
    n_splits_outcome : int, default ``5``
        Number of folds for outcome-model cross-fitting.
    model_outcome : estimator, optional
        Base learner for outcome prediction.  Defaults depend on
        ``outcome_type``.
    outcome_type : {"continuous", "binary", "survival"} or None, optional
        Type of ``y``.  ``None`` triggers automatic detection.
    niter : int, default ``10``
        Number of stage‑1 iterations before meta-learning.
    matching_is_stochastic : bool, default ``True``
        Use stochastic matching when ``True`` otherwise deterministic.
    do_stacking : bool, default ``True``
        When ``False`` bypass the meta-learner and average treatment effects
        across iterations.
    prob_clip_eps : float, default ``1e-6``
        Epsilon for probability clipping before taking logits.
    n_mc : int, default ``1``
        Number of Monte Carlo draws per matched unit for survival outcomes.
    random_state_master : int or None, optional
        Seed controlling all stochastic elements except the bootstrap.
    nboot : int, default ``0``
        Number of bootstrap resamples.  ``0`` disables bootstrapping.
    alpha : float, default ``0.05``
        Significance level for percentile confidence intervals.
    n_jobs : int, default ``-1``
        Parallel jobs for the bootstrap.
    random_state_boot : int or None, optional
        Seed for bootstrap resampling.
    model_meta : object, optional
        Meta-learner fitted on stacked predictions.
    ref_group : int or str or None, optional
        Reference treatment arm when more than two levels are present.

    Returns
    -------
    dict
        Dictionary containing the key ``"te"`` with the estimated effect and a
        ``"matching"`` matrix of cluster identifiers with shape ``(n, niter)``.
        When ``nboot`` is greater than zero an additional ``"ci"`` tuple with
        percentile bounds and ``"boot"`` array of bootstrap estimates are
        included.

    Notes
    -----
    * **Two-arm designs** – the result is ``{"te": float}`` (always with a
    ``"matching"`` matrix) plus optional keys ``"ci"`` and ``"boot"`` when
    bootstrapping is requested.
    * **Multi-arm designs** – the result is
    ``{"pairwise": pandas.DataFrame, ...}`` (again with ``"matching"``)
    where each row holds one treatment comparison (and optional ``"boot"``
    dict).
    * Use :pyfunc:`causalem.as_pairwise` to obtain a uniform pairwise dataframe
    from either form.
    * **Estimands:**
      - **No-stacking:** Each iteration yields a treatment effect on that
        iteration's matched set. Results are averaged across iterations with no
        appearance weighting (geometric mean for survival HRs).
      - **Stacking:** Base predictions are combined via a meta-learner fitted
        with appearance weights. Final non-survival averages and survival
        hazard ratios are appearance-weighted over the matched union.
    """
    # Quick branch: multi-treatment → dedicated pipeline
    if _is_multi_treatment(treatment):
        return estimate_te_multi(  # defined further down in this file
            Xraw=Xraw,
            treatment=treatment,
            y=y,
            groups=groups,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            model_outcome=model_outcome,
            outcome_type=outcome_type,
            niter=niter,
            matching_is_stochastic=matching_is_stochastic,
            do_stacking=do_stacking,
            prob_clip_eps=prob_clip_eps,
            n_mc=n_mc,
            random_state_master=random_state_master,
            nboot=nboot,
            alpha=alpha,
            n_jobs=n_jobs,
            random_state_boot=random_state_boot,
            model_meta=model_meta,
            ref_group=ref_group,
        )

    # -------------------------------------------------------------- #
    # Determine outcome_type  ("continuous" | "binary" | "survival") #
    # -------------------------------------------------------------- #
    if outcome_type is None:
        # crude auto-detection
        if isinstance(y, np.ndarray) and y.ndim == 2 and y.shape[1] == 2:
            outcome_type = "survival"
        elif np.array_equal(np.unique(y), [0, 1]) or np.array_equal(
            np.unique(y), [0.0, 1.0]
        ):
            outcome_type = "binary"
        else:
            outcome_type = "continuous"
    else:
        allowed = {"continuous", "binary", "survival"}
        if outcome_type not in allowed:
            raise ValueError(f"`outcome_type` must be one of {allowed}.")
        if outcome_type == "binary" and not np.array_equal(np.unique(y), [0, 1]):
            raise ValueError("`outcome_type='binary'` but y is not {0,1}.")

    is_binary = outcome_type == "binary"

    if niter == 1 and outcome_type != "survival":
        do_stacking = False

    # ------------------------------------------------------------------ #
    # Global RNG for this call                                           #
    # ------------------------------------------------------------------ #
    rng_master = np.random.default_rng(random_state_master)

    # ------------------------------------------------------------------ #
    # Default learner, then build templates for *all* outcome types      #
    # ------------------------------------------------------------------ #
    if model_outcome is None:
        if outcome_type == "survival":
            model_outcome = RandomSurvivalForest(n_estimators=100)
        elif outcome_type == "continuous":
            model_outcome = RandomForestRegressor(n_estimators=100)
        else:
            model_outcome = RandomForestClassifier(n_estimators=100)

    outcome_templates = _setup_outcome_models(model_outcome, niter)

    # ------------------------------------------------------------------ #
    # 1. Bootstrap wrapper (recursion)                                   #
    # ------------------------------------------------------------------ #
    if nboot > 0:
        if groups is not None:
            warnings.warn("`groups` ignored when bootstrapping.", stacklevel=2)

        rng_boot = np.random.default_rng(random_state_boot)
        seeds_worker = rng_boot.integers(0, 2**32, size=nboot)

        def _single_boot(seed: int) -> float:
            rng_local = np.random.default_rng(seed)
            idx = rng_local.integers(0, Xraw.shape[0], size=Xraw.shape[0])
            te = estimate_te(
                Xraw[idx],
                treatment[idx],
                y[idx],
                groups=np.asarray(idx),
                n_splits_propensity=n_splits_propensity,
                model_propensity=model_propensity,
                matching_scale=matching_scale,
                matching_caliper=matching_caliper,
                n_splits_outcome=n_splits_outcome,
                model_outcome=model_outcome,
                outcome_type=outcome_type,
                niter=niter,
                matching_is_stochastic=matching_is_stochastic,
                do_stacking=do_stacking,
                prob_clip_eps=prob_clip_eps,
                n_mc=n_mc,
                random_state_master=seed,
                nboot=0,
                model_meta=model_meta,
                ref_group=ref_group,
            )["te"]
            return te

        boot_stats = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(_single_boot)(int(s)) for s in seeds_worker
        )
        boot_stats = np.asarray(boot_stats)

        theta_res = estimate_te(
            Xraw,
            treatment,
            y,
            groups=None,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            model_outcome=model_outcome,
            outcome_type=outcome_type,
            niter=niter,
            matching_is_stochastic=matching_is_stochastic,
            do_stacking=do_stacking,
            prob_clip_eps=prob_clip_eps,
            n_mc=n_mc,
            random_state_master=random_state_master,
            nboot=0,
            model_meta=model_meta,
            ref_group=ref_group,
        )
        theta_hat = theta_res["te"]
        cluster_mat = theta_res["matching"]

        lo, hi = np.percentile(boot_stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        return {
            "te": theta_hat,
            "ci": (lo, hi),
            "boot": boot_stats,
            "matching": cluster_mat,
        }

    # ------------------------------------------------------------------ #
    # Survival pathway (placeholder)                                     #
    # ------------------------------------------------------------------ #
    if outcome_type == "survival":
        return _estimate_te_survival(
            Xraw,
            treatment,
            y,
            rng_master=rng_master,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            outcome_templates=outcome_templates,
            niter=niter,
            matching_is_stochastic=matching_is_stochastic,
            model_meta=model_meta,
            do_stacking=do_stacking,
            groups=groups,
            n_mc=n_mc,
        )

    # ------------------------------------------------------------------ #
    # 2. Multi-iteration pipeline                                        #
    # ------------------------------------------------------------------ #
    results = []
    cluster_list = []
    te_list = []
    for _ in range(niter):
        rng_iter = np.random.default_rng(int(rng_master.integers(2**32)))
        res = stage_1_single_iter(
            Xraw,
            treatment,
            y,
            rng=rng_iter,
            outcome_is_binary=is_binary,
            groups=groups,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            model_outcome=outcome_templates[_],  # <-- heterogeneous!
            matching_is_stochastic=matching_is_stochastic,
            prob_clip_eps=prob_clip_eps,
        )
        results.append(res)
        cluster_list.append(res[0])
        if not do_stacking:
            cid, yp, yp_cf = res
            matched_idx = np.where(cid != -1)[0]
            yp_treat = np.where(treatment == 1, yp, yp_cf)
            yp_ctrl = np.where(treatment == 1, yp_cf, yp)
            te_list.append(
                np.mean(yp_treat[matched_idx]) - np.mean(yp_ctrl[matched_idx])
            )

    cluster_mat = np.column_stack(cluster_list)
    if not do_stacking:
        te_hat = float(np.mean(te_list))
        return {"te": te_hat, "matching": cluster_mat}

    weights = appearance_weights(cluster_mat)
    matched_union = np.where(weights > 0)[0]

    y_pred_mat = np.column_stack([r[1] for r in results])
    y_pred_cf_mat = np.column_stack([r[2] for r in results])

    # for binary outcomes, clip+logit each column of the predictions
    if is_binary:
        y_pred_mat = clip_logit(y_pred_mat, eps=prob_clip_eps)
        y_pred_cf_mat = clip_logit(y_pred_cf_mat, eps=prob_clip_eps)

    # add treatment indicator to y_pred_mat and y_pred_cf_mat
    y_pred_mat = np.hstack((y_pred_mat, treatment.reshape(-1, 1)))
    y_pred_cf_mat = np.hstack((y_pred_cf_mat, (1 - treatment).reshape(-1, 1)))

    splitter_meta = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng_master.integers(2**32)),
        groups=groups,
    )
    if model_meta is None:
        if is_binary:
            model_meta = LogisticRegression(solver="newton-cg")
        else:
            model_meta = LinearRegression()
    assert isinstance(model_meta, BaseEstimator)

    y_final = np.full(Xraw.shape[0], np.nan)
    y_final_cf = np.full(Xraw.shape[0], np.nan)

    for tr_idx, te_idx in splitter_meta.split(Xraw, groups=groups):
        matched_tr = np.intersect1d(matched_union, tr_idx)
        if matched_tr.size == 0:
            raise ValueError(
                "No matched units in training set. "
                "Try increasing `matching_scale` or `matching_caliper`."
            )
        fit_with_appearance_weights(
            model_meta,
            y_pred_mat[matched_tr],
            y[matched_tr],
            sample_weight=weights[matched_tr],
        )
        if is_binary and hasattr(model_meta, "predict_proba"):
            y_final[te_idx] = model_meta.predict_proba(y_pred_mat[te_idx])[:, 1]
            y_final_cf[te_idx] = model_meta.predict_proba(y_pred_cf_mat[te_idx])[:, 1]
        else:
            y_final[te_idx] = model_meta.predict(y_pred_mat[te_idx])
            y_final_cf[te_idx] = model_meta.predict(y_pred_cf_mat[te_idx])

    y_final_treat = np.where(treatment == 1, y_final, y_final_cf)
    y_final_ctrl = np.where(treatment == 1, y_final_cf, y_final)
    te_hat = np.average(
        y_final_treat[matched_union], weights=weights[matched_union]
    ) - np.average(y_final_ctrl[matched_union], weights=weights[matched_union])
    return {"te": te_hat, "matching": cluster_mat}


def _is_multi_treatment(t):
    """Return True if *t* has more than two unique, non-nan values."""
    u = np.unique(t[~pd.isna(t)])
    return len(u) > 2


def stage_1_single_iter_multi(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng: np.random.Generator,
    outcome_is_binary: bool,
    groups: Optional[np.ndarray] = None,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    model_outcome=RandomForestRegressor(n_estimators=100),
    matching_is_stochastic: bool = True,
    prob_clip_eps: float = 1e-6,
    ref_group: int | str | None = None,
):
    """Single iteration for multi-arm treatment matching.

    Parameters are analogous to :func:`stage_1_single_iter` with the addition of
    ``ref_group`` which specifies the reference treatment arm when more than two
    levels are present.

    Returns
    -------
    cluster_ids : ndarray
        Cluster identifiers for the matching draw (``-1`` for unmatched).
    y_pred : ndarray
        Out-of-sample predictions for the factual outcome.
    y_pred_all_arms : list of ndarray
        Per-arm predictions for every unit with the treatment code clamped to each arm (including the observed arm).
    treatment_names : ndarray
        Names of the treatment levels in the order corresponding to
        ``y_pred_all_arms``.
    """

    # Provide a default learner when none is supplied
    if model_outcome is None:
        model_outcome = RandomForestRegressor(n_estimators=100)

    # No feature subsetting
    X = Xraw

    # --- propensity CV -----------------------------------------------------
    splitter_prop = _make_splitter(
        n_splits=n_splits_propensity,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )

    # --- propensity CV & logit --------------------------------------------
    oos_proba = cross_val_predict(
        clone(model_propensity),
        X,
        treatment,
        cv=splitter_prop,
        method="predict_proba",
        groups=groups,
    )
    oos_scores = clip_logit(oos_proba, eps=prob_clip_eps)

    # --- matching ----------------------------------------------------------
    cluster_ids = stochastic_match(
        treatment=treatment,
        score=oos_scores,
        scale=matching_scale,
        caliper=matching_caliper,
        nsmp=1 if matching_is_stochastic else 0,
        random_state=int(rng.integers(2**32)),
        ref_group=ref_group,
    ).ravel()
    # return cluster_ids
    matched_idx = np.where(cluster_ids != -1)[0]

    # --- outcome cross-fitting --------------------------------------------
    splitter_out = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )

    enc = OneHotEncoder(sparse_output=False, handle_unknown="error")
    enc.fit(treatment.reshape(-1, 1))
    treatment_names = enc.categories_[0].astype(str)

    X_t_actual = np.hstack((X, enc.transform(treatment.reshape(-1, 1))))
    X_t_all_arms = []
    for treatment_value in treatment_names:
        X_t_single_arm = np.hstack(
            (X, enc.transform(np.full(treatment.shape, treatment_value).reshape(-1, 1)))
        )
        X_t_all_arms.append(X_t_single_arm)

    y_pred = np.full(X_t_actual.shape[0], np.nan)
    y_pred_all_arms = []
    for X_t_single_arm in X_t_all_arms:
        y_pred_all_arms.append(np.full(X_t_single_arm.shape[0], np.nan))

    for tr_idx, te_idx in splitter_out.split(X_t_actual, groups=groups):
        matched_tr = np.intersect1d(matched_idx, tr_idx)
        if matched_tr.size == 0:
            continue
        rf = clone(model_outcome)
        if "random_state" in rf.get_params(deep=False):
            rf.set_params(random_state=int(rng.integers(2**32)))
        rf.fit(X_t_actual[matched_tr], y[matched_tr])

        if outcome_is_binary and hasattr(rf, "predict_proba"):
            y_pred[te_idx] = rf.predict_proba(X_t_actual[te_idx])[:, 1]
            for i, X_t_single_arm in enumerate(X_t_all_arms):
                y_pred_all_arms[i][te_idx] = rf.predict_proba(X_t_single_arm[te_idx])[
                    :, 1
                ]
        else:
            y_pred[te_idx] = rf.predict(X_t_actual[te_idx])
            for i, X_t_single_arm in enumerate(X_t_all_arms):
                y_pred_all_arms[i][te_idx] = rf.predict(X_t_single_arm[te_idx])

    return cluster_ids, y_pred, y_pred_all_arms, treatment_names


def estimate_te_multi(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    groups: Optional[np.ndarray] = None,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    model_outcome=None,
    outcome_type: Optional[str] = None,  # "continuous" | "binary" | "survival"
    niter: int = 10,
    matching_is_stochastic: bool = True,
    do_stacking: bool = True,
    prob_clip_eps: float = 1e-6,
    n_mc: int = 1,
    # --- RNG control ------------------------------------------------------
    random_state_master: Optional[int] = None,
    # --- bootstrap options -----------------------------------------------
    nboot: int = 0,
    alpha: float = 0.05,
    n_jobs: int = -1,
    random_state_boot: Optional[int] = None,
    model_meta: Optional[object] = None,
    ref_group: int | str | None = None,
) -> dict:
    """Estimate treatment effects for multi-arm designs.

    ``n_mc`` controls the number of Monte Carlo draws per matched unit when the
    outcome is survival.

    Returns
    -------
    dict
        Always returns the keys ``"per_treatment"``, ``"pairwise"``, ``"boot"``
        and ``"matching"``.

    ``per_treatment``
        DataFrame with columns ``["treatment", "mean"]`` and optional
        confidence interval columns ``"lo"`` and ``"hi"`` when bootstrapping.
        For survival outcomes this dataframe is empty.

    ``pairwise``
        DataFrame with columns ``["treatment_1", "treatment_2", "te"]`` and
        optional ``"lo"``/``"hi"`` when bootstrapping.

    ``boot``
        Dictionary of bootstrap draws.  For non-survival outcomes the keys are
        treatment names; for survival outcomes the keys are treatment pairs.

    ``matching``
        Matrix of cluster identifiers with shape ``(n, niter)``.

    When ``do_stacking`` is ``False`` predictions from each iteration are
    averaged instead of fitted via a meta-learner.

    See :pyfunc:`causalem.as_pairwise` for a helper that extracts/standardises
    the pairwise table.

    Notes
    -----
    ``"matching"`` is always present in the returned dictionary.
    * **Estimands:**
      - **No-stacking:** Each iteration produces per-arm means or pairwise HRs
        on that iteration's matched set. Results are averaged across iterations
        without appearance weighting.
      - **Stacking:** The meta-learner is fitted with appearance weights and
        final per-arm averages or marginal Cox HRs are appearance-weighted over
        the matched union.
    """
    # -------------------------------------------------------------- #
    # Determine outcome_type  ("continuous" | "binary" | "survival") #
    # -------------------------------------------------------------- #
    if outcome_type is None:
        # crude auto-detection
        if isinstance(y, np.ndarray) and y.ndim == 2 and y.shape[1] == 2:
            outcome_type = "survival"
        elif np.array_equal(np.unique(y), [0, 1]) or np.array_equal(
            np.unique(y), [0.0, 1.0]
        ):
            outcome_type = "binary"
        else:
            outcome_type = "continuous"
    else:
        allowed = {"continuous", "binary", "survival"}
        if outcome_type not in allowed:
            raise ValueError(f"`outcome_type` must be one of {allowed}.")
        if outcome_type == "binary" and not np.array_equal(np.unique(y), [0, 1]):
            raise ValueError("`outcome_type='binary'` but y is not {0,1}.")
    if niter == 1:
        do_stacking = False

    is_binary = outcome_type == "binary"

    # ------------------------------------------------------------------ #
    # Global RNG for this call                                           #
    # ------------------------------------------------------------------ #
    rng_master = np.random.default_rng(random_state_master)

    # ------------------------------------------------------------------ #
    # Default learner, then build templates for *all* outcome types      #
    # ------------------------------------------------------------------ #
    if model_outcome is None:
        if outcome_type == "survival":
            model_outcome = RandomSurvivalForest(n_estimators=100)
        elif outcome_type == "continuous":
            model_outcome = RandomForestRegressor(n_estimators=100)
        else:
            model_outcome = RandomForestClassifier(n_estimators=100)

    outcome_templates = _setup_outcome_models(model_outcome, niter)

    # ------------------------------------------------------------------ #
    # 1. Bootstrap wrapper (recursion)                                   #
    # ------------------------------------------------------------------ #
    if nboot > 0:
        if groups is not None:
            warnings.warn("`groups` is ignored when bootstrapping.", stacklevel=2)

        # --- RNG for bootstrap resampling --------------------------------
        rng_boot = np.random.default_rng(random_state_boot)
        seeds_worker = rng_boot.integers(0, 2**32, size=nboot)

        # --- helper run on each worker -----------------------------------
        def _single_boot(seed: int):
            rng_local = np.random.default_rng(seed)
            idx = rng_local.integers(0, Xraw.shape[0], size=Xraw.shape[0])
            return estimate_te_multi(
                Xraw[idx],
                treatment[idx],
                y[idx],
                groups=np.asarray(idx),
                n_splits_propensity=n_splits_propensity,
                model_propensity=model_propensity,
                matching_scale=matching_scale,
                matching_caliper=matching_caliper,
                n_splits_outcome=n_splits_outcome,
                model_outcome=model_outcome,
                outcome_type=outcome_type,
                niter=niter,
                matching_is_stochastic=matching_is_stochastic,
                do_stacking=do_stacking,
                prob_clip_eps=prob_clip_eps,
                n_mc=n_mc,
                random_state_master=int(seed),
                nboot=0,  # terminate recursion
                model_meta=model_meta,
                ref_group=ref_group,
            )

        # --- run bootstrap in parallel -----------------------------------
        boot_list = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(_single_boot)(int(s)) for s in seeds_worker
        )

        # --- collate bootstrap draws -------------------------------------
        if outcome_type == "survival":
            pairs = [
                tuple(x)
                for x in boot_list[0]["pairwise"][
                    ["treatment_1", "treatment_2"]
                ].to_numpy()
            ]
            boot_mat = np.vstack([d["pairwise"]["te"].to_numpy() for d in boot_list])
        else:
            trt_names = boot_list[0]["per_treatment"]["treatment"].tolist()
            boot_mat = np.vstack(
                [d["per_treatment"]["mean"].to_numpy() for d in boot_list]
            )

        pct_lo = 100 * alpha / 2
        pct_hi = 100 * (1 - alpha / 2)

        # --- point estimate on original data -----------------------------
        theta_hat_res = estimate_te_multi(
            Xraw,
            treatment,
            y,
            groups=None,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            model_outcome=model_outcome,
            outcome_type=outcome_type,
            niter=niter,
            matching_is_stochastic=matching_is_stochastic,
            do_stacking=do_stacking,
            prob_clip_eps=prob_clip_eps,
            n_mc=n_mc,
            random_state_master=random_state_master,
            nboot=0,
            model_meta=model_meta,
            ref_group=ref_group,
        )
        theta_hat = theta_hat_res
        cluster_mat = theta_hat_res.get("matching")
        if outcome_type == "survival":
            est_vec = theta_hat["pairwise"]["te"].to_numpy()
            lo_vec, hi_vec = np.percentile(boot_mat, [pct_lo, pct_hi], axis=0)
            df_pairs = theta_hat["pairwise"].copy()
            df_pairs["lo"] = lo_vec
            df_pairs["hi"] = hi_vec
            boot_dict = {pair: boot_mat[:, i] for i, pair in enumerate(pairs)}
            return {
                "per_treatment": pd.DataFrame(
                    columns=["treatment", "mean", "lo", "hi"]
                ),
                "pairwise": df_pairs,
                "boot": boot_dict,
                "matching": cluster_mat,
            }
        else:
            boot_dict = {k: boot_mat[:, i] for i, k in enumerate(trt_names)}

            est_vec = theta_hat["per_treatment"]["mean"].to_numpy()
            lo_vec, hi_vec = np.percentile(boot_mat, [pct_lo, pct_hi], axis=0)

            df_means = pd.DataFrame(
                {
                    "treatment": trt_names,
                    "mean": est_vec,
                    "lo": lo_vec,
                    "hi": hi_vec,
                }
            )

            pair_rows = []
            pair_boot: list[np.ndarray] = []
            for i, a in enumerate(trt_names):
                for j in range(i + 1, len(trt_names)):
                    b = trt_names[j]
                    pair_rows.append((a, b, est_vec[i] - est_vec[j]))
                    pair_boot.append(boot_mat[:, i] - boot_mat[:, j])
            df_pairs = pd.DataFrame(
                pair_rows, columns=["treatment_1", "treatment_2", "te"]
            )
            if pair_boot:
                pair_boot_mat = np.column_stack(pair_boot)
                lo_p, hi_p = np.percentile(pair_boot_mat, [pct_lo, pct_hi], axis=0)
                df_pairs["lo"] = lo_p
                df_pairs["hi"] = hi_p

            boot_dict = {k: v for k, v in boot_dict.items()}

            return {
                "per_treatment": df_means,
                "pairwise": df_pairs,
                "boot": boot_dict,
                "matching": cluster_mat,
            }

    # ------------------------------------------------------------------ #
    # Survival pathway (placeholder)                                     #
    # ------------------------------------------------------------------ #
    if outcome_type == "survival":
        df_pairs, cluster_mat = _estimate_te_survival_multi(
            Xraw=Xraw,
            treatment=treatment,
            y=y,
            rng_master=rng_master,
            outcome_templates=outcome_templates,
            niter=niter,
            model_meta=model_meta,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            groups=groups,
            matching_is_stochastic=matching_is_stochastic,
            n_splits_outcome=n_splits_outcome,
            n_mc=n_mc,
            administrative_censoring=True,
            prob_clip_eps=prob_clip_eps,
            do_stacking=do_stacking,
            ref_group=ref_group,
        )
        return {
            "per_treatment": pd.DataFrame(columns=["treatment", "mean"]),
            "pairwise": df_pairs,
            "boot": {},
            "matching": cluster_mat,
        }

    # ------------------------------------------------------------------ #
    # 2. Iterative pipeline                                              #
    # ------------------------------------------------------------------ #
    results = []
    cluster_list = []
    avg_list = []
    for i in range(niter):
        rng_iter = np.random.default_rng(int(rng_master.integers(2**32)))
        res = stage_1_single_iter_multi(
            Xraw,
            treatment,
            y,
            rng=rng_iter,
            outcome_is_binary=is_binary,
            groups=groups,
            n_splits_propensity=n_splits_propensity,
            model_propensity=model_propensity,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            n_splits_outcome=n_splits_outcome,
            model_outcome=outcome_templates[i],  # <-- heterogeneous!
            matching_is_stochastic=matching_is_stochastic,
            prob_clip_eps=prob_clip_eps,
            ref_group=ref_group,
        )
        results.append(res)
        cluster_list.append(res[0])
        if not do_stacking:
            matched_idx = np.where(res[0] != -1)[0]
            avg_list.append(
                [float(np.mean(res[2][j][matched_idx])) for j in range(len(res[2]))]
            )

    cluster_mat = np.column_stack(cluster_list)

    if not do_stacking:
        avg_arr = np.mean(np.vstack(avg_list), axis=0)
        treatment_names = results[0][3]
        df_means = pd.DataFrame({"treatment": treatment_names, "mean": avg_arr})
        pair_rows = []
        for i, a in enumerate(treatment_names):
            for j in range(i + 1, len(treatment_names)):
                b = treatment_names[j]
                pair_rows.append((a, b, avg_arr[i] - avg_arr[j]))
        df_pairs = pd.DataFrame(pair_rows, columns=["treatment_1", "treatment_2", "te"])
        return {
            "per_treatment": df_means,
            "pairwise": df_pairs,
            "boot": {},
            "matching": cluster_mat,
        }

    weights = appearance_weights(cluster_mat)
    matched_union = np.where(weights > 0)[0]

    y_pred_mat = np.column_stack([r[1] for r in results])
    y_pred_all_arms = []
    for i in range(len(results[0][2])):
        y_pred_all_arms.append(np.column_stack([r[2][i] for r in results]))

    # for binary outcomes, clip+logit each column of the predictions
    if is_binary:
        y_pred_mat = clip_logit(y_pred_mat, eps=prob_clip_eps)
        for i in range(len(y_pred_all_arms)):
            y_pred_all_arms[i] = clip_logit(y_pred_all_arms[i], eps=prob_clip_eps)

    # add treatment indicators to the predictions
    enc = OneHotEncoder(sparse_output=False, handle_unknown="error")
    enc.fit(treatment.reshape(-1, 1))
    treatment_names = enc.categories_[0].astype(str)
    y_pred_mat = np.hstack((y_pred_mat, enc.transform(treatment.reshape(-1, 1))))
    for i in range(len(y_pred_all_arms)):
        y_pred_all_arms[i] = np.hstack(
            (
                y_pred_all_arms[i],
                enc.transform(
                    np.full(treatment.shape, treatment_names[i]).reshape(-1, 1)
                ),
            )
        )

    splitter_meta = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng_master.integers(2**32)),
        groups=groups,
    )
    if model_meta is None:
        if is_binary:
            model_meta = LogisticRegression(solver="newton-cg")
        else:
            model_meta = LinearRegression()

    y_final_all_arms = []
    for i in range(len(y_pred_all_arms)):
        y_final_all_arms.append(np.full(Xraw.shape[0], np.nan))

    for tr_idx, te_idx in splitter_meta.split(Xraw, groups=groups):
        model_meta_clone = clone(model_meta)
        matched_tr = np.intersect1d(matched_union, tr_idx)
        if matched_tr.size == 0:
            raise ValueError(
                "No matched units in training set. "
                "Try increasing `matching_scale` or `matching_caliper`."
            )
        fit_with_appearance_weights(
            model_meta_clone,
            y_pred_mat[matched_tr],
            y[matched_tr],
            sample_weight=weights[matched_tr],
        )
        if is_binary and hasattr(model_meta_clone, "predict_proba"):
            for i in range(len(y_pred_all_arms)):
                y_final_all_arms[i][te_idx] = model_meta_clone.predict_proba(
                    y_pred_all_arms[i][te_idx]
                )[:, 1]
        else:
            for i in range(len(y_pred_all_arms)):
                y_final_all_arms[i][te_idx] = model_meta_clone.predict(
                    y_pred_all_arms[i][te_idx]
                )
    means = []
    for i, treatment_name in enumerate(treatment_names):
        means.append(
            (
                treatment_name,
                float(
                    np.average(
                        y_final_all_arms[i][matched_union],
                        weights=weights[matched_union],
                    )
                ),
            )
        )

    df_means = pd.DataFrame(means, columns=["treatment", "mean"])

    pair_rows = []
    for i, a in enumerate(treatment_names):
        for j in range(i + 1, len(treatment_names)):
            b = treatment_names[j]
            pair_rows.append((a, b, df_means.loc[i, "mean"] - df_means.loc[j, "mean"]))
    df_pairs = pd.DataFrame(pair_rows, columns=["treatment_1", "treatment_2", "te"])

    return {
        "per_treatment": df_means,
        "pairwise": df_pairs,
        "boot": {},
        "matching": cluster_mat,
    }


def stage_1_single_iter_survival_multi(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng: np.random.Generator,
    # ---- design & matching -------------------------------------------------
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    groups: Optional[np.ndarray] = None,
    matching_is_stochastic: bool = True,
    # ---- outcome modelling -------------------------------------------------
    n_splits_outcome: int = 5,
    model_outcome: Optional[BaseEstimator] = None,
    n_mc: int = 1,
    administrative_censoring: bool = True,
    prob_clip_eps: float = 1e-6,
    ref_group: int | str | None = None,
    **kwargs,
) -> tuple[list[tuple[tuple[Any, Any], float]], np.ndarray]:
    """Single survival iteration for multi-arm no-stacking.

    Fits a survival model on the matched units, simulates ``n_mc`` draws for
    every treatment arm and computes pairwise hazard ratios on that iteration's
    matched set.
    """

    # No feature subsetting
    X = Xraw

    # ------------ 1. Propensity CV  ----------------------------------------
    splitter_prop = _make_splitter(
        n_splits=n_splits_propensity,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )

    # --- propensity CV & logit --------------------------------------------
    oos_proba = cross_val_predict(
        clone(model_propensity),
        X,
        treatment,
        cv=splitter_prop,
        method="predict_proba",
        groups=groups,
    )
    oos_scores = clip_logit(oos_proba, eps=prob_clip_eps)

    # --- matching ----------------------------------------------------------
    cluster_ids = stochastic_match(
        treatment=treatment,
        score=oos_scores,
        scale=matching_scale,
        caliper=matching_caliper,
        nsmp=1 if matching_is_stochastic else 0,
        random_state=int(rng.integers(2**32)),
        ref_group=ref_group,
    ).ravel()
    # return cluster_ids
    matched_idx = np.where(cluster_ids != -1)[0]
    if matched_idx.size == 0:
        raise ValueError("No matches found – relax caliper/scale.")

    # --- outcome cross-fitting --------------------------------------------
    splitter_out = _make_splitter(
        n_splits=n_splits_outcome,
        shuffle=True,
        seed=int(rng.integers(2**32)),
        groups=groups,
    )

    # ---- choose survival learner -------------------------------------
    if model_outcome is None:
        model_outcome = RandomSurvivalForest(
            n_estimators=200,
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=1,
        )

    enc = OneHotEncoder(sparse_output=False, handle_unknown="error")
    enc.fit(treatment.reshape(-1, 1))
    treatment_names = enc.categories_[0].astype(str)

    X_t_actual = np.hstack((X, enc.transform(treatment.reshape(-1, 1))))
    X_t_all_arms = []
    for treatment_value in treatment_names:
        X_t_single_arm = np.hstack(
            (X, enc.transform(np.full(treatment.shape, treatment_value).reshape(-1, 1)))
        )
        X_t_all_arms.append(X_t_single_arm)

    # containers for predicted survival functions
    sf_all_arms = [[None] * x.shape[0] for x in X_t_all_arms]

    surv_y = np.array(
        list(zip(y[:, 1] == 1, y[:, 0])),
        dtype=[("event", "bool"), ("time", "f8")],
    )

    for tr_idx, te_idx in splitter_out.split(X_t_actual, groups=groups):
        matched_tr = np.intersect1d(matched_idx, tr_idx)
        if matched_tr.size == 0:
            continue

        mdl = clone(model_outcome)
        if "random_state" in mdl.get_params(deep=False):
            mdl.set_params(random_state=int(rng.integers(2**32)))
        mdl.fit(X_t_actual[matched_tr], surv_y[matched_tr])

        for i, X_t_single_arm in enumerate(X_t_all_arms):
            sf_tmp = mdl.predict_survival_function(
                X_t_single_arm[te_idx], return_array=False
            )
            for pos, idx in enumerate(te_idx):
                sf_all_arms[i][idx] = sf_tmp[pos]

    # ------------ 4. Monte-Carlo simulation of (time, event) tuples --------------------------------
    tau = float(y[:, 0].max()) if administrative_censoring else math.inf
    idx = matched_idx
    t_list = [np.empty((len(idx), n_mc)) for _ in X_t_all_arms]
    e_list = [np.empty((len(idx), n_mc), dtype=bool) for _ in X_t_all_arms]
    for i, sf_single_arm in enumerate(sf_all_arms):
        for pos, j in enumerate(idx):
            if sf_single_arm[j] is None:
                raise ValueError("Missing survival prediction for a matched row.")
            rng_tmp = np.random.default_rng(int(rng.integers(2**32)))
            t_list[i][pos], e_list[i][pos] = _simulate_from_sf(
                sf=sf_single_arm[j],
                tau=tau,
                n_draws=n_mc,
                rng=rng_tmp,
            )

    # loop over pairs of treatment values, fit Cox and extract HR from fitted model
    hr_list = []
    for i, treatment_value in enumerate(treatment_names):
        for j in range(i + 1, len(treatment_names)):
            if i == j:
                continue
            times = np.concatenate([t_list[i].ravel(), t_list[j].ravel()])
            events = np.concatenate([e_list[i].ravel(), e_list[j].ravel()])
            treatment_combined = np.concatenate(
                [
                    np.zeros_like(t_list[i].ravel()),
                    np.ones_like(t_list[j].ravel()),
                ]
            )
            synth = np.array(
                list(zip(events == 1, times)), dtype=[("event", "bool"), ("time", "f8")]
            )
            df = pd.DataFrame({"d": treatment_combined})
            cox = CoxPHSurvivalAnalysis().fit(df, synth)
            hr = float(np.exp(cox.coef_[0]))
            hr_list.append(((treatment_value, treatment_names[j]), hr))

    return hr_list, cluster_ids


def _estimate_te_survival_multi(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    y: np.ndarray,
    *,
    rng_master: np.random.Generator,
    outcome_templates: list[BaseEstimator],
    niter: int,
    model_meta: Optional[BaseEstimator] = None,
    n_mc: int = 1,
    administrative_censoring: bool = True,
    n_splits_propensity: int = 5,
    model_propensity=LogisticRegression(solver="newton-cg"),
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    n_splits_outcome: int = 5,
    matching_is_stochastic: bool = True,
    groups: Optional[np.ndarray] = None,
    prob_clip_eps: float = 1e-6,
    do_stacking: bool = True,
    ref_group: int | str | None = None,
) -> tuple[pd.DataFrame, np.ndarray]:
    """Estimate HRs for all treatment pairs via survival meta-learning.

    When ``do_stacking`` is ``True`` a Cox meta-learner is fitted on stacked
    predictions using appearance weights, and pairwise contrasts are computed
    on the **matched union**.  When ``do_stacking`` is ``False`` each iteration
    yields HRs on that iteration's matched set and geometric means (without
    appearance weighting) are returned.  ``niter == 1`` disables stacking
    automatically.
    """

    if niter == 1:
        do_stacking = False
    if not do_stacking:
        hr_log: dict[tuple[str, str], list[float]] = {}
        cluster_list = []
        for i in range(niter):
            rng_iter = np.random.default_rng(int(rng_master.integers(2**32)))
            hr_iter, cid = stage_1_single_iter_survival_multi(
                Xraw,
                treatment,
                y,
                rng=rng_iter,
                n_splits_propensity=n_splits_propensity,
                model_propensity=model_propensity,
                matching_scale=matching_scale,
                matching_caliper=matching_caliper,
                n_splits_outcome=n_splits_outcome,
                model_outcome=outcome_templates[i],
                matching_is_stochastic=matching_is_stochastic,
                groups=groups,
                n_mc=n_mc,
                administrative_censoring=administrative_censoring,
                prob_clip_eps=prob_clip_eps,
                ref_group=ref_group,
            )
            for pair, hr in hr_iter:
                hr_log.setdefault(pair, []).append(math.log(hr))
            cluster_list.append(cid)
        hr_dict = {pair: float(np.exp(np.mean(vals))) for pair, vals in hr_log.items()}
        cluster_mat = np.column_stack(cluster_list)
        return _hr_dict_to_df(hr_dict), cluster_mat

    (
        matched_idx,
        sf_all_arms,
        treatment_names,
        cluster_mat,
    ) = stage_1_meta_survival_multi(
        Xraw,
        treatment,
        y,
        rng_master=rng_master,
        outcome_templates=outcome_templates,
        niter=niter,
        model_meta=model_meta,
        n_splits_propensity=n_splits_propensity,
        model_propensity=model_propensity,
        matching_scale=matching_scale,
        matching_caliper=matching_caliper,
        n_splits_outcome=n_splits_outcome,
        matching_is_stochastic=matching_is_stochastic,
        groups=groups,
        prob_clip_eps=prob_clip_eps,
        ref_group=ref_group,
    )

    tau = float(y[:, 0].max()) if administrative_censoring else math.inf
    idx = matched_idx
    t_list = [np.empty((len(idx), n_mc)) for _ in treatment_names]
    e_list = [np.empty((len(idx), n_mc), dtype=bool) for _ in treatment_names]

    for i, sf_arm in enumerate(sf_all_arms):
        for pos, j in enumerate(idx):
            if sf_arm[j] is None:
                raise ValueError("Missing survival prediction for a matched row.")
            rng_tmp = np.random.default_rng(int(rng_master.integers(2**32)))
            t_list[i][pos], e_list[i][pos] = _simulate_from_sf(
                sf_arm[j], n_mc, tau, rng_tmp
            )

    w_all = appearance_weights(cluster_mat)
    w_idx = w_all[idx]
    hr_dict = {}
    for i, name_i in enumerate(treatment_names):
        for j in range(i + 1, len(treatment_names)):
            times = np.concatenate([t_list[i].ravel(), t_list[j].ravel()])
            events = np.concatenate([e_list[i].ravel(), e_list[j].ravel()])
            trt_combined = np.concatenate(
                [
                    np.zeros_like(t_list[i].ravel()),
                    np.ones_like(t_list[j].ravel()),
                ]
            )
            synth = np.array(
                list(zip(events == 1, times)), dtype=[("event", "bool"), ("time", "f8")]
            )
            w_rows = np.concatenate([np.repeat(w_idx, n_mc), np.repeat(w_idx, n_mc)])
            hr_dict[(name_i, treatment_names[j])] = fit_cox_marginal_weighted(
                trt_combined, synth, w_rows
            )

    return _hr_dict_to_df(hr_dict), cluster_mat
