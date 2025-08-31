"""
Mediation analysis implementation.

This module contains the implementation of mediation analysis using 
plug-in G-computation for binary treatment, binary/continuous mediators,
and binary/continuous outcomes.
"""

from __future__ import annotations

import warnings
from typing import Optional, Tuple, Union, Iterable, Any

import numpy as np
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator, clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, KFold, cross_val_predict
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from causalem.design.matchers import stochastic_match
from causalem.estimation.ensemble import clip_logit

try:
    from scipy.stats import ks_2samp
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


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


def _validate_binary(name: str, arr: np.ndarray):
    """Validate that array contains only binary {0,1} values."""
    u = np.unique(arr)
    # Check if all values are in {0, 1} (allowing float representation)
    if not all(val in [0, 1, 0.0, 1.0] for val in u):
        raise ValueError(f"{name} must be binary in {{0,1}}; got unique values {u}.")


def _detect_mediator_type(mediator: np.ndarray) -> str:
    """
    Auto-detect whether mediator is binary or continuous.

    Parameters
    ----------
    mediator : np.ndarray
        The mediator variable

    Returns
    -------
    str
        Either "binary" or "continuous"
    """
    u = np.unique(mediator)
    # Check if all values are in {0, 1} (allowing float representation)
    if len(u) == 2 and all(val in [0, 1, 0.0, 1.0] for val in u):
        return "binary"
    elif len(u) == 1 and u[0] in [0, 1, 0.0, 1.0]:
        return "binary"  # Constant binary mediator
    else:
        return "continuous"


def _detect_outcome_type(outcome: np.ndarray) -> str:
    """
    Auto-detect whether outcome is binary or continuous.

    Parameters
    ----------
    outcome : np.ndarray
        The outcome variable

    Returns
    -------
    str
        Either "binary" or "continuous"
    """
    u = np.unique(outcome)
    # Check if all values are in {0, 1} (allowing float representation)
    if len(u) == 2 and all(val in [0, 1, 0.0, 1.0] for val in u):
        return "binary"
    elif len(u) == 1 and u[0] in [0, 1, 0.0, 1.0]:
        return "binary"  # Constant binary outcome
    else:
        return "continuous"


def _setup_mediator_models(model_mediator, niter: int):
    """
    Expand *model_mediator* into a list of length `niter`.

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
    if isinstance(model_mediator, BaseEstimator):
        return [clone(model_mediator) for _ in range(niter)]

    # list / tuple -----------------------------------------------------
    if isinstance(model_mediator, (list, tuple)):
        if len(model_mediator) < niter:
            raise ValueError("`model_mediator` list shorter than niter.")
        return [clone(m) for m in model_mediator[:niter]]

    # generator / iterator --------------------------------------------
    if hasattr(model_mediator, "__iter__"):
        templates = []
        it = iter(model_mediator)
        for _ in range(niter):
            try:
                templates.append(clone(next(it)))
            except StopIteration:
                raise ValueError(
                    "Generator for model_mediator yielded fewer than niter estimators."
                )
        return templates

    raise TypeError(
        "`model_mediator` must be an estimator, a list/tuple of estimators, "
        "or a generator yielding estimators."
    )


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


def estimate_mediation(
    Xraw: np.ndarray,
    treatment: np.ndarray,
    mediator: np.ndarray,
    y: np.ndarray,
    *,
    model_mediator: Optional[Union[BaseEstimator, Iterable[BaseEstimator]]] = None,
    model_outcome: Optional[Union[BaseEstimator, Iterable[BaseEstimator]]] = None,
    n_splits_mediator: int = 5,
    n_splits_outcome: int = 5,
    groups: Optional[np.ndarray] = None,
    random_state_master: Optional[int] = None,
    # Matching options
    niter: int = 1,
    matching_is_stochastic: bool = False,
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    model_propensity = None,  # Will default to LogisticRegression
    # Continuous-mediator residual-bootstrap knobs
    n_mc_mediator: int = 50,
    residual_pool: str = "knn",
    residual_knn: int = 50,
    standardize_X_for_knn: bool = True,
    clip_m_support: Optional[Tuple[float, float]] = None,
    quantile_bounds: Tuple[float, float] = (0.01, 0.99),
    max_truncation_warn: float = 0.10,
    # Binary-mediator specific (legacy)
    prob_clip_eps: float = 1e-6,
    # Binary-outcome specific
    prob_clip_eps_outcome: float = 1e-6,
    effect_type: str = "interventional",
    return_detail: bool = False,
    # Bootstrap options
    nboot: int = 0,
    alpha: float = 0.05,
    n_jobs: int = -1,
    random_state_boot: Optional[int] = None,
) -> dict:
    """
    Plug-in mediation estimator for binary A, binary/continuous M, binary/continuous Y.

    This function estimates mediation effects using plug-in G-computation with optional
    stochastic matching for design-aware estimation. It supports both binary and continuous
    mediators, with residual-bootstrap sampling for the continuous case. Both
    interventional and natural direct/indirect effects are supported.

    When matching is enabled (niter>1 or matching_is_stochastic=True), propensity scores are
    computed and stochastic matching is performed. Mediation effects are computed within each
    matched set and averaged across iterations, following the same pattern as treatment effect estimation.

    For binary outcomes, effects are estimated on the risk-difference (RD) scale to
    preserve additivity: TE = DE + IE.

    Parameters
    ----------
    Xraw : np.ndarray of shape (n, p)
        Raw covariate matrix.
    treatment : np.ndarray of shape (n,)
        Binary treatment indicator, must be in {0, 1}.
    mediator : np.ndarray of shape (n,)
        Mediator variable, either binary {0, 1} or continuous (auto-detected).
    y : np.ndarray of shape (n,)
        Outcome variable, either binary {0, 1} or continuous (auto-detected).
    model_mediator : BaseEstimator, list of BaseEstimator, or iterable, optional
        Model(s) for mediator. For binary M: classifier with predict_proba.
        For continuous M: regressor with predict method.
        Can be:
        • Single estimator (cloned for each iteration when matching enabled)
        • List/tuple of estimators (must have ≥ niter items when matching enabled)  
        • Generator/iterator yielding estimators (consumed for each iteration)
        Default: LogisticRegression for binary, RandomForestRegressor for continuous.
    model_outcome : BaseEstimator, list of BaseEstimator, or iterable, optional
        Model(s) for outcome. For binary Y: classifier with predict_proba.
        For continuous Y: regressor with predict method.
        Can be:
        • Single estimator (cloned for each iteration when matching enabled)
        • List/tuple of estimators (must have ≥ niter items when matching enabled)
        • Generator/iterator yielding estimators (consumed for each iteration)
        Default: LogisticRegression for binary Y, RandomForestRegressor for continuous Y.
    n_splits_mediator : int, default 5
        Number of cross-validation folds for mediator model cross-fitting.
    n_splits_outcome : int, default 5
        Number of cross-validation folds for outcome model cross-fitting.
        Outcome cross-fitting is mandatory (no bypass option).
    groups : np.ndarray, optional
        Group labels for grouped cross-validation.
    random_state_master : int, optional
        Master random state for reproducible results.
    niter : int, default 1
        Number of stochastic matching iterations. When niter=1 and matching_is_stochastic=False,
        no matching is performed (current behavior). When niter>1 or matching_is_stochastic=True,
        stochastic matching is applied and effects are averaged across matched-set iterations.
    matching_is_stochastic : bool, default False
        Use stochastic matching when True, deterministic matching when False.
        When False and niter=1, no matching is performed (backward compatibility).
    matching_scale : float, default 1.0
        Scale parameter for stochastic matching. Larger values increase randomness in matching.
    matching_caliper : float, optional
        Maximum allowable propensity score distance for matching. Units beyond this distance
        are excluded from matched sets.
    model_propensity : BaseEstimator, optional
        Model for propensity score estimation. Default: LogisticRegression(solver="newton-cg").
        Only used when matching is enabled (niter>1 or matching_is_stochastic=True).
    n_mc_mediator : int, default 50
        Monte Carlo draws per unit per counterfactual mediator law (continuous M only).
    residual_pool : {"knn", "global"}, default "knn"
        Pool for residual draws in continuous mediator bootstrap.
    residual_knn : int, default 50
        K for KNN pools when residual_pool="knn".
    standardize_X_for_knn : bool, default True
        Whether to z-score X before KNN search.
    clip_m_support : tuple of (float, float), optional
        Explicit bounds for mediator values applied to both treatment arms. 
        If None, uses per-arm quantile_bounds for automatic clipping.
    quantile_bounds : tuple of (float, float), default (0.01, 0.99)
        Quantiles for automatic mediator clipping bounds when clip_m_support is None.
    max_truncation_warn : float, default 0.10
        Warn if fraction of clipped mediator draws exceeds this threshold.
    prob_clip_eps : float, default 1e-6
        Epsilon for probability clipping (binary mediator only).
    prob_clip_eps_outcome : float, default 1e-6
        Epsilon for probability clipping for binary outcome models.
    effect_type : {"interventional", "natural"}, default "interventional"
        Type of mediation effects to compute:
        - "interventional": IDE (interventional direct effect) and IIE (interventional indirect effect)
        - "natural": NDE (natural direct effect) and NIE (natural indirect effect)
    return_detail : bool, default False
        Whether to return detailed unit-level estimates and intermediate quantities.
    nboot : int, default 0
        Number of bootstrap resamples for confidence intervals. If 0, no bootstrap is performed.
        When nboot > 0, bootstrap-induced groups are automatically created to ensure
        cross-validation folds respect resampled duplicates.
    alpha : float, default 0.05
        Significance level for confidence intervals. CIs are computed at (alpha/2, 1-alpha/2).
    n_jobs : int, default -1
        Number of parallel jobs for bootstrap resampling. -1 uses all available cores.
    random_state_boot : int, optional
        Random seed for bootstrap resampling. Ensures reproducible bootstrap results.

    Returns
    -------
    dict
        Dictionary containing:
        - 'te' : float, total effect
        - 'ide'/'nde' : float, direct effect (interventional or natural)
        - 'iie'/'nie' : float, indirect effect (interventional or natural)
        - 'prop_mediated' : float, proportion mediated (indirect/total)
        - 'scale' : str, effect scale ("risk_difference" for binary Y, "mean_difference" for continuous Y)
        - 'detail' : dict, optional, detailed unit-level results if return_detail=True
        - 'ci' : dict, optional, confidence intervals when nboot > 0
        - 'boot' : dict, optional, bootstrap resamples when nboot > 0

        When nboot > 0, additional keys are included:
        - 'ci' contains (lower, upper) confidence intervals for each effect
        - 'boot' contains arrays of bootstrap resamples for each effect

    Notes
    -----
    **Assumptions:**
    - No unmeasured confounding of A→Y and M→Y given X
    - Positivity: 0 < P(A=1|X) < 1 and overlap for P(M|A,X)
    - For natural effects: additional cross-world assumption

    **Mediator Types:**
    - Binary: Uses cross-fitted logistic regression with plug-in G-computation
    - Continuous: Uses cross-fitted regression with residual-bootstrap sampling

    **Outcome Types:**
    - Binary: Uses cross-fitted logistic regression, effects on risk-difference scale
    - Continuous: Uses cross-fitted regression, effects on mean-difference scale

    **Estimands:**
    Let μ̂(a,m) = Ê[Y|A=a,M=m,X] (or P̂(Y=1|A=a,M=m,X) for binary Y) and p̂(m|a) = P̂(M=m|A=a,X).

    - TE = Ê[Y(1,M₁)] - Ê[Y(0,M₀)]
    - IDE = Ê[Y(1,M₀)] - Ê[Y(0,M₀)] (interventional direct)
    - IIE = TE - IDE (interventional indirect)

    Natural effects use the same algebra but different interpretation.

    Examples
    --------
    **Binary mediator + binary outcome:**

    >>> import numpy as np
    >>> from causalem.mediation import estimate_mediation
    >>>
    >>> # Simulate data
    >>> np.random.seed(42)
    >>> n = 1000
    >>> X = np.random.randn(n, 3)
    >>> A = np.random.binomial(1, 0.5, n)
    >>> M = np.random.binomial(1, 1/(1 + np.exp(-(X.sum(1) + A))))
    >>> Y = np.random.binomial(1, 1/(1 + np.exp(-(X.sum(1) + 2*A + 3*M))))
    >>>
    >>> result = estimate_mediation(X, A, M, Y, random_state_master=42)
    >>> print(f"Total Effect: {result['te']:.3f}")
    >>> print(f"Direct Effect: {result['ide']:.3f}")
    >>> print(f"Indirect Effect: {result['iie']:.3f}")

    **Continuous mediator + binary outcome:**

    >>> # Continuous mediator, binary outcome case
    >>> M_cont = 0.7*A + 0.5*X[:,0] + np.random.randn(n)  # continuous mediator
    >>> Y_bin = np.random.binomial(1, 1/(1 + np.exp(-(1.5*A + 2.0*M_cont + 0.4*X[:,2]))))
    >>>
    >>> result = estimate_mediation(
    ...     X, A, M_cont, Y_bin,
    ...     random_state_master=42,
    ...     n_mc_mediator=100,
    ...     residual_pool="knn",
    ...     residual_knn=50
    ... )
    """
    # Input validation and conversion
    A = np.asarray(treatment).ravel()
    M = np.asarray(mediator).ravel()
    Y = np.asarray(y).ravel()
    X = np.asarray(Xraw)

    if X.shape[0] != A.shape[0] or A.shape[0] != M.shape[0] or M.shape[0] != Y.shape[0]:
        raise ValueError("X, treatment, mediator, y must have the same number of rows.")

    # Validate treatment is binary
    _validate_binary("treatment", A)
    A = A.astype(int)
    
    # Validate both treatment arms exist (required to model p(M|A=a,X) for a=0,1)
    ux = np.unique(A)
    if not (len(ux) == 2 and set(ux) == {0, 1}):
        raise ValueError("treatment must contain both 0 and 1 to estimate counterfactual mediator laws for both arms.")

    # Set default propensity model
    if model_propensity is None:
        model_propensity = LogisticRegression(solver="newton-cg", max_iter=1000)

    # Validate n_mc_mediator
    if n_mc_mediator < 1:
        raise ValueError("n_mc_mediator must be >= 1.")

    # Validate quantile_bounds
    ql, qh = quantile_bounds
    if not (0.0 < ql < qh < 1.0):
        raise ValueError("quantile_bounds must satisfy 0 < low < high < 1.")

    # Validate clip_m_support if provided
    if clip_m_support is not None:
        lo, hi = clip_m_support
        if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
            raise ValueError("clip_m_support must be (lo, hi) with finite lo < hi.")

    # Bootstrap wrapper
    if nboot > 0:
        if groups is not None:
            warnings.warn("`groups` ignored when bootstrapping.", stacklevel=2)

        rng_boot = np.random.default_rng(random_state_boot)
        seeds_worker = rng_boot.integers(0, 2**32, size=nboot)

        def _single_boot(seed: int) -> dict:
            rng_local = np.random.default_rng(seed)
            idx = rng_local.integers(0, X.shape[0], size=X.shape[0])
            
            result = _mediation_point_estimate(
                X[idx],
                A[idx],
                M[idx],
                Y[idx],
                model_mediator=model_mediator,
                model_outcome=model_outcome,
                n_splits_mediator=n_splits_mediator,
                n_splits_outcome=n_splits_outcome,
                groups=np.asarray(idx),  # Bootstrap-induced groups
                random_state_master=seed,
                # Matching parameters
                niter=niter,
                matching_is_stochastic=matching_is_stochastic,
                matching_scale=matching_scale,
                matching_caliper=matching_caliper,
                model_propensity=model_propensity,
                n_mc_mediator=n_mc_mediator,
                residual_pool=residual_pool,
                residual_knn=residual_knn,
                standardize_X_for_knn=standardize_X_for_knn,
                clip_m_support=clip_m_support,
                quantile_bounds=quantile_bounds,
                max_truncation_warn=max_truncation_warn,
                prob_clip_eps=prob_clip_eps,
                prob_clip_eps_outcome=prob_clip_eps_outcome,
                effect_type=effect_type,
                return_detail=False,  # No details in bootstrap
            )
            return result

        boot_results = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(_single_boot)(int(s)) for s in seeds_worker
        )

        # Extract bootstrap statistics
        boot_te = np.array([r["te"] for r in boot_results])
        direct_key = "ide" if effect_type == "interventional" else "nde"
        indirect_key = "iie" if effect_type == "interventional" else "nie"
        boot_direct = np.array([r[direct_key] for r in boot_results])
        boot_indirect = np.array([r[indirect_key] for r in boot_results])
        boot_prop = np.array([r["prop_mediated"] for r in boot_results])

        # Compute point estimate on original data
        point_result = _mediation_point_estimate(
            X, A, M, Y,
            model_mediator=model_mediator,
            model_outcome=model_outcome,
            n_splits_mediator=n_splits_mediator,
            n_splits_outcome=n_splits_outcome,
            groups=None,  # No bootstrap-induced groups for point estimate
            random_state_master=random_state_master,
            # Matching parameters
            niter=niter,
            matching_is_stochastic=matching_is_stochastic,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            model_propensity=model_propensity,
            n_mc_mediator=n_mc_mediator,
            residual_pool=residual_pool,
            residual_knn=residual_knn,
            standardize_X_for_knn=standardize_X_for_knn,
            clip_m_support=clip_m_support,
            quantile_bounds=quantile_bounds,
            max_truncation_warn=max_truncation_warn,
            prob_clip_eps=prob_clip_eps,
            prob_clip_eps_outcome=prob_clip_eps_outcome,
            effect_type=effect_type,
            return_detail=return_detail,
        )

        # Compute percentile confidence intervals
        lo_percentile = 100 * alpha / 2
        hi_percentile = 100 * (1 - alpha / 2)
        
        ci_te = tuple(np.percentile(boot_te, [lo_percentile, hi_percentile]))
        ci_direct = tuple(np.percentile(boot_direct, [lo_percentile, hi_percentile]))
        ci_indirect = tuple(np.percentile(boot_indirect, [lo_percentile, hi_percentile]))
        ci_prop = tuple(np.percentile(boot_prop, [lo_percentile, hi_percentile]))

        # Build result with bootstrap information
        point_result["ci"] = {
            "te": ci_te,
            direct_key: ci_direct,
            indirect_key: ci_indirect,
            "prop_mediated": ci_prop,
        }
        point_result["boot"] = {
            "te": boot_te,
            direct_key: boot_direct,
            indirect_key: boot_indirect,
            "prop_mediated": boot_prop,
        }

        return point_result

    # No bootstrap: delegate to point estimation
    return _mediation_point_estimate(
        X, A, M, Y,
        model_mediator=model_mediator,
        model_outcome=model_outcome,
        n_splits_mediator=n_splits_mediator,
        n_splits_outcome=n_splits_outcome,
        groups=groups,
        random_state_master=random_state_master,
        # Matching parameters
        niter=niter,
        matching_is_stochastic=matching_is_stochastic,
        matching_scale=matching_scale,
        matching_caliper=matching_caliper,
        model_propensity=model_propensity,
        n_mc_mediator=n_mc_mediator,
        residual_pool=residual_pool,
        residual_knn=residual_knn,
        standardize_X_for_knn=standardize_X_for_knn,
        clip_m_support=clip_m_support,
        quantile_bounds=quantile_bounds,
        max_truncation_warn=max_truncation_warn,
        prob_clip_eps=prob_clip_eps,
        prob_clip_eps_outcome=prob_clip_eps_outcome,
        effect_type=effect_type,
        return_detail=return_detail,
    )


def _mediation_point_estimate(
    X: np.ndarray,
    A: np.ndarray,
    M: np.ndarray,
    Y: np.ndarray,
    model_mediator: Optional[Union[BaseEstimator, Iterable[BaseEstimator]]] = None,
    model_outcome: Optional[Union[BaseEstimator, Iterable[BaseEstimator]]] = None,
    n_splits_mediator: int = 5,
    n_splits_outcome: int = 5,
    groups: Optional[np.ndarray] = None,
    random_state_master: Optional[int] = None,
    # Matching parameters
    niter: int = 1,
    matching_is_stochastic: bool = False,
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    model_propensity = None,
    n_mc_mediator: int = 50,
    residual_pool: str = "knn",
    residual_knn: int = 50,
    standardize_X_for_knn: bool = True,
    clip_m_support: Optional[Tuple[float, float]] = None,
    quantile_bounds: Tuple[float, float] = (0.01, 0.99),
    max_truncation_warn: float = 0.10,
    prob_clip_eps: float = 1e-6,
    prob_clip_eps_outcome: float = 1e-6,
    effect_type: str = "interventional",
    return_detail: bool = False,
) -> dict:
    """
    Point estimation helper for mediation analysis.
    
    This function performs the core mediation analysis computation with optional matching.
    It is called both for point estimation and within bootstrap workers.
    """

    # Determine if matching should be used
    use_matching = niter > 1 or matching_is_stochastic
    
    # Set up reproducible random number generation
    rng = np.random.default_rng(random_state_master)
    
    # Set up models for single or multiple iterations
    if use_matching:
        # For matching, prepare models for each iteration
        mediator_models = _setup_mediator_models(model_mediator, niter) if model_mediator is not None else [None] * niter
        outcome_models = _setup_outcome_models(model_outcome, niter) if model_outcome is not None else [None] * niter
    else:
        # For single iteration, handle list input by taking first model
        if model_mediator is not None:
            if isinstance(model_mediator, (list, tuple)):
                if len(model_mediator) == 0:
                    raise ValueError("model_mediator list cannot be empty")
                single_mediator_model = model_mediator[0]
            elif hasattr(model_mediator, "__iter__") and not isinstance(model_mediator, BaseEstimator):
                # Handle generator/iterator
                try:
                    single_mediator_model = next(iter(model_mediator))
                except StopIteration:
                    raise ValueError("model_mediator iterator is empty")
            else:
                single_mediator_model = model_mediator
        else:
            single_mediator_model = None
            
        if model_outcome is not None:
            if isinstance(model_outcome, (list, tuple)):
                if len(model_outcome) == 0:
                    raise ValueError("model_outcome list cannot be empty")
                single_outcome_model = model_outcome[0]
            elif hasattr(model_outcome, "__iter__") and not isinstance(model_outcome, BaseEstimator):
                # Handle generator/iterator
                try:
                    single_outcome_model = next(iter(model_outcome))
                except StopIteration:
                    raise ValueError("model_outcome iterator is empty")
            else:
                single_outcome_model = model_outcome
        else:
            single_outcome_model = None
    
    if use_matching:
        # Multiple iterations with stochastic matching
        return _estimate_mediation_with_matching(
            X, A, M, Y,
            mediator_models=mediator_models,
            outcome_models=outcome_models,
            n_splits_mediator=n_splits_mediator,
            n_splits_outcome=n_splits_outcome,
            groups=groups,
            rng_master=rng,
            niter=niter,
            matching_is_stochastic=matching_is_stochastic,
            matching_scale=matching_scale,
            matching_caliper=matching_caliper,
            model_propensity=model_propensity,
            n_mc_mediator=n_mc_mediator,
            residual_pool=residual_pool,
            residual_knn=residual_knn,
            standardize_X_for_knn=standardize_X_for_knn,
            clip_m_support=clip_m_support,
            quantile_bounds=quantile_bounds,
            max_truncation_warn=max_truncation_warn,
            prob_clip_eps=prob_clip_eps,
            prob_clip_eps_outcome=prob_clip_eps_outcome,
            effect_type=effect_type,
            return_detail=return_detail,
        )
    else:
        # Single iteration without matching (original behavior)
        return _estimate_mediation_single_iter(
            X, A, M, Y,
            model_mediator=single_mediator_model,
            model_outcome=single_outcome_model,
            n_splits_mediator=n_splits_mediator,
            n_splits_outcome=n_splits_outcome,
            groups=groups,
            rng=rng,
            n_mc_mediator=n_mc_mediator,
            residual_pool=residual_pool,
            residual_knn=residual_knn,
            standardize_X_for_knn=standardize_X_for_knn,
            clip_m_support=clip_m_support,
            quantile_bounds=quantile_bounds,
            max_truncation_warn=max_truncation_warn,
            prob_clip_eps=prob_clip_eps,
            prob_clip_eps_outcome=prob_clip_eps_outcome,
            effect_type=effect_type,
            return_detail=return_detail,
        )


def _estimate_mediation_single_iter(
    X: np.ndarray,
    A: np.ndarray,
    M: np.ndarray,
    Y: np.ndarray,
    model_mediator: Optional[BaseEstimator] = None,
    model_outcome: Optional[BaseEstimator] = None,
    n_splits_mediator: int = 5,
    n_splits_outcome: int = 5,
    groups: Optional[np.ndarray] = None,
    rng: np.random.Generator = None,
    n_mc_mediator: int = 50,
    residual_pool: str = "knn",
    residual_knn: int = 50,
    standardize_X_for_knn: bool = True,
    clip_m_support: Optional[Tuple[float, float]] = None,
    quantile_bounds: Tuple[float, float] = (0.01, 0.99),
    max_truncation_warn: float = 0.10,
    prob_clip_eps: float = 1e-6,
    prob_clip_eps_outcome: float = 1e-6,
    effect_type: str = "interventional",
    return_detail: bool = False,
) -> dict:
    """
    Single iteration mediation analysis without matching (original behavior).
    """

    # Auto-detect mediator and outcome types
    mediator_type = _detect_mediator_type(M)
    outcome_type = _detect_outcome_type(Y)

    # For binary mediator, validate and convert to int
    if mediator_type == "binary":
        _validate_binary("mediator", M)
        M = M.astype(int)

    # For binary outcome, validate and convert to int
    if outcome_type == "binary":
        _validate_binary("outcome", Y)
        Y = Y.astype(int)
    else:
        # Continuous outcomes must be real-valued
        if not np.isrealobj(Y):
            raise ValueError("Outcome y must be real-valued.")

    # Set up models with defaults based on mediator and outcome types
    if model_mediator is None:
        if mediator_type == "binary":
            model_mediator = LogisticRegression(solver="newton-cg", max_iter=1000)
        else:  # continuous
            model_mediator = RandomForestRegressor(n_estimators=200)
    if model_outcome is None:
        if outcome_type == "binary":
            model_outcome = LogisticRegression(solver="lbfgs", max_iter=1000)
        else:  # continuous
            model_outcome = RandomForestRegressor(n_estimators=400)

    # Set up reproducible random number generation
    seed_med = int(rng.integers(2**31 - 1))
    seed_out = int(rng.integers(2**31 - 1))
    seed_mc = int(rng.integers(2**31 - 1))  # For Monte Carlo sampling

    # Branch on mediator type
    if mediator_type == "binary":
        return _estimate_mediation_binary(
            X,
            A,
            M,
            Y,
            model_mediator,
            model_outcome,
            n_splits_mediator,
            n_splits_outcome,
            groups,
            seed_med,
            seed_out,
            prob_clip_eps,
            prob_clip_eps_outcome,
            outcome_type,
            effect_type,
            return_detail,
        )
    else:  # continuous
        return _estimate_mediation_continuous(
            X,
            A,
            M,
            Y,
            model_mediator,
            model_outcome,
            n_splits_mediator,
            n_splits_outcome,
            groups,
            seed_med,
            seed_out,
            seed_mc,
            n_mc_mediator,
            residual_pool,
            residual_knn,
            standardize_X_for_knn,
            clip_m_support,
            quantile_bounds,
            max_truncation_warn,
            prob_clip_eps_outcome,
            outcome_type,
            effect_type,
            return_detail,
        )


def _estimate_mediation_with_matching(
    X: np.ndarray,
    A: np.ndarray,
    M: np.ndarray,
    Y: np.ndarray,
    mediator_models: list[Optional[BaseEstimator]] = None,
    outcome_models: list[Optional[BaseEstimator]] = None,
    n_splits_mediator: int = 5,
    n_splits_outcome: int = 5,
    groups: Optional[np.ndarray] = None,
    rng_master: np.random.Generator = None,
    niter: int = 1,
    matching_is_stochastic: bool = False,
    matching_scale: float = 1.0,
    matching_caliper: Optional[float] = None,
    model_propensity = None,
    n_mc_mediator: int = 50,
    residual_pool: str = "knn",
    residual_knn: int = 50,
    standardize_X_for_knn: bool = True,
    clip_m_support: Optional[Tuple[float, float]] = None,
    quantile_bounds: Tuple[float, float] = (0.01, 0.99),
    max_truncation_warn: float = 0.10,
    prob_clip_eps: float = 1e-6,
    prob_clip_eps_outcome: float = 1e-6,
    effect_type: str = "interventional",
    return_detail: bool = False,
) -> dict:
    """
    Multi-iteration mediation analysis with stochastic matching.
    
    This function performs multiple iterations of mediation analysis,
    computing effects within each matched set and averaging across iterations.
    """
    
    # Collect results across iterations
    results = []
    cluster_list = []
    te_list = []
    direct_list = []
    indirect_list = []
    prop_list = []
    
    # Run multiple iterations
    for i in range(niter):
        # Get iteration-specific RNG
        rng_iter = np.random.default_rng(int(rng_master.integers(2**32)))
        
        # Compute propensity scores via cross-fitting
        splitter_prop = _make_splitter(
            n_splits=5,  # Fixed number of splits for propensity
            shuffle=True,
            seed=int(rng_iter.integers(2**32)),
            groups=groups,
        )
        
        # Cross-fitted propensity scores
        oos_proba = cross_val_predict(
            clone(model_propensity),
            X,
            A,
            cv=splitter_prop,
            method="predict_proba",
            groups=groups,
        )[:, 1]
        
        # Clip and convert to logits
        oos_scores = clip_logit(oos_proba, eps=prob_clip_eps)
        
        # Perform stochastic matching
        cluster_ids = stochastic_match(
            treatment=A,
            score=oos_scores,
            scale=matching_scale,
            caliper=matching_caliper,
            nsmp=1 if matching_is_stochastic else 0,
            random_state=int(rng_iter.integers(2**32)),
        ).ravel()
        
        cluster_list.append(cluster_ids)
        matched_idx = np.where(cluster_ids != -1)[0]
        
        if matched_idx.size == 0:
            raise ValueError(f"No matches found in iteration {i+1}. Try relaxing matching_caliper or matching_scale.")
        
        # Run mediation analysis on matched subset using iteration-specific models
        result = _estimate_mediation_single_iter(
            X[matched_idx],
            A[matched_idx],
            M[matched_idx],
            Y[matched_idx],
            model_mediator=mediator_models[i] if mediator_models else None,
            model_outcome=outcome_models[i] if outcome_models else None,
            n_splits_mediator=n_splits_mediator,
            n_splits_outcome=n_splits_outcome,
            groups=groups[matched_idx] if groups is not None else None,
            rng=rng_iter,
            n_mc_mediator=n_mc_mediator,
            residual_pool=residual_pool,
            residual_knn=residual_knn,
            standardize_X_for_knn=standardize_X_for_knn,
            clip_m_support=clip_m_support,
            quantile_bounds=quantile_bounds,
            max_truncation_warn=max_truncation_warn,
            prob_clip_eps=prob_clip_eps,
            prob_clip_eps_outcome=prob_clip_eps_outcome,
            effect_type=effect_type,
            return_detail=False,  # Don't return details for individual iterations
        )
        
        results.append(result)
        te_list.append(result["te"])
        
        # Extract direct and indirect effects based on effect type
        if effect_type == "interventional":
            direct_list.append(result["ide"])
            indirect_list.append(result["iie"])
        else:  # natural
            direct_list.append(result["nde"])
            indirect_list.append(result["nie"])
            
        prop_list.append(result["prop_mediated"])
    
    # Average across iterations
    te_avg = float(np.mean(te_list))
    direct_avg = float(np.mean(direct_list))
    indirect_avg = float(np.mean(indirect_list))
    
    # Handle proportion mediated (may contain NaNs)
    prop_finite = [p for p in prop_list if np.isfinite(p)]
    prop_avg = float(np.mean(prop_finite)) if prop_finite else float(np.nan)
    
    # Create cluster matrix for diagnostics
    cluster_mat = np.column_stack(cluster_list)
    
    # Get mediator and outcome type from first iteration
    mediator_type = results[0]["mediator_type"]
    scale = results[0]["scale"]
    
    # Build return dict based on effect type
    if effect_type == "interventional":
        return_dict = {
            "te": te_avg,
            "ide": direct_avg,
            "iie": indirect_avg,
            "prop_mediated": prop_avg,
            "mediator_type": mediator_type,
            "scale": scale,
            "detail": None,  # No detailed output for multi-iteration
            "matching": cluster_mat,
        }
    else:  # natural
        return_dict = {
            "te": te_avg,
            "nde": direct_avg,
            "nie": indirect_avg,
            "prop_mediated": prop_avg,
            "mediator_type": mediator_type,
            "scale": scale,
            "detail": None,  # No detailed output for multi-iteration
            "matching": cluster_mat,
        }
    
    if return_detail:
        # For multi-iteration, provide summary statistics instead of unit-level details
        return_dict["detail"] = {
            "niter": niter,
            "te_by_iter": te_list,
            "direct_by_iter": direct_list,
            "indirect_by_iter": indirect_list,
            "prop_by_iter": prop_list,
            "n_matched_by_iter": [np.sum(cids != -1) for cids in cluster_list],
        }
    
    return return_dict


def _estimate_mediation_binary(
    X: np.ndarray,
    A: np.ndarray,
    M: np.ndarray,
    Y: np.ndarray,
    model_mediator: BaseEstimator,
    model_outcome: BaseEstimator,
    n_splits_mediator: int,
    n_splits_outcome: int,
    groups: Optional[np.ndarray],
    seed_med: int,
    seed_out: int,
    prob_clip_eps: float,
    prob_clip_eps_outcome: float,
    outcome_type: str,
    effect_type: str,
    return_detail: bool,
) -> dict:
    """Handle binary mediator case for both binary and continuous outcomes."""

    # Check that mediator model supports predict_proba
    if not hasattr(model_mediator, "predict_proba"):
        raise TypeError(
            "model_mediator must implement predict_proba for binary mediator."
        )

    # For binary outcomes, check that outcome model supports predict_proba
    if outcome_type == "binary" and not hasattr(model_outcome, "predict_proba"):
        raise TypeError(
            "model_outcome must implement predict_proba for binary outcome."
        )

    # ---- Mediator model: P(M=1 | A, X) with cross-fitting ----
    X_med = np.hstack([X, A.reshape(-1, 1)])
    splitter_med = _make_splitter(
        n_splits=n_splits_mediator, shuffle=True, seed=seed_med, groups=groups
    )

    # Check for constant mediator (special case)
    if len(np.unique(M)) == 1:
        warnings.warn(
            "Mediator is constant (all 0 or all 1). Mediation effects may not be identifiable.",
            UserWarning,
        )
        # For constant mediator, cross-validation will fail, so we use simple predictions
        p_hat = np.full(len(M), float(M[0]))
    else:
        # Cross-validated predictions for training risk control
        p_hat = cross_val_predict(
            clone(model_mediator),
            X_med,
            M,
            cv=splitter_med,
            method="predict_proba",
            groups=groups,
        )[:, 1]
    p_hat = np.clip(p_hat, prob_clip_eps, 1 - prob_clip_eps)

    # Check for potential positivity violations
    median_p = np.median(p_hat)
    if median_p < prob_clip_eps or median_p > (1 - prob_clip_eps):
        warnings.warn(
            f"Potential positivity violation: median predicted mediator probability is {median_p:.6f}. "
            f"Consider larger prob_clip_eps or check for extreme imbalance.",
            UserWarning,
        )

    # Fit mediator model on full data and obtain p(M=1|A=0,X) and p(M=1|A=1,X)
    if len(np.unique(M)) == 1:
        # Constant mediator case - use constant predictions
        constant_prob = float(M[0])
        pm1_a0 = np.full(len(A), constant_prob)
        pm1_a1 = np.full(len(A), constant_prob)
    else:
        med_fit = clone(model_mediator).fit(X_med, M)
        X_a0 = np.hstack([X, np.zeros_like(A).reshape(-1, 1)])
        X_a1 = np.hstack([X, np.ones_like(A).reshape(-1, 1)])
        pm1_a0 = np.clip(
            med_fit.predict_proba(X_a0)[:, 1], prob_clip_eps, 1 - prob_clip_eps
        )
        pm1_a1 = np.clip(
            med_fit.predict_proba(X_a1)[:, 1], prob_clip_eps, 1 - prob_clip_eps
        )
    pm0_a0 = 1.0 - pm1_a0
    pm0_a1 = 1.0 - pm1_a1

    # ---- Outcome model: E[Y | A, M, X] with cross-fitting ----
    X_out = np.hstack([X, A.reshape(-1, 1), M.reshape(-1, 1)])
    
    # Set up cross-fitting splitter for outcome model
    splitter_out = _make_splitter(
        n_splits=n_splits_outcome, shuffle=True, seed=seed_out, groups=groups
    )
    
    # Initialize arrays to store out-of-fold predictions for all (A,M) combinations
    n_units = len(X)
    yhat_00 = np.zeros(n_units)  # E[Y | A=0, M=0, X]
    yhat_01 = np.zeros(n_units)  # E[Y | A=0, M=1, X]
    yhat_10 = np.zeros(n_units)  # E[Y | A=1, M=0, X]
    yhat_11 = np.zeros(n_units)  # E[Y | A=1, M=1, X]
    
    # Track which fold each unit belongs to for diagnostics
    outcome_fold = np.full(n_units, -1, dtype=int)
    
    # Cross-fit outcome models
    for fold, (tr_idx, te_idx) in enumerate(splitter_out.split(X_out, groups=groups)):
        if len(tr_idx) == 0 or len(te_idx) == 0:
            continue
            
        # Fit outcome model on training fold
        out_fit = clone(model_outcome)
        if "random_state" in out_fit.get_params(deep=False):
            out_fit.set_params(random_state=int(np.random.RandomState(seed_out + fold).randint(2**31 - 1)))
        out_fit.fit(X_out[tr_idx], Y[tr_idx])
        
        # Record fold assignments for diagnostics
        outcome_fold[te_idx] = fold
        
        # Generate predictions for test fold on all (A,M) combinations
        def predict_counterfactual(test_indices, a_val, m_val):
            X_am = np.hstack([
                X[test_indices], 
                np.full(len(test_indices), a_val).reshape(-1, 1), 
                np.full(len(test_indices), m_val).reshape(-1, 1)
            ])
            if outcome_type == "binary":
                # For binary outcomes, use predict_proba and clip probabilities
                probs = out_fit.predict_proba(X_am)[:, 1]
                return np.clip(probs, prob_clip_eps_outcome, 1 - prob_clip_eps_outcome)
            else:
                # For continuous outcomes, use predict
                return out_fit.predict(X_am)
        
        # Get counterfactual predictions for test fold
        yhat_00[te_idx] = predict_counterfactual(te_idx, 0, 0)
        yhat_01[te_idx] = predict_counterfactual(te_idx, 0, 1)
        yhat_10[te_idx] = predict_counterfactual(te_idx, 1, 0)
        yhat_11[te_idx] = predict_counterfactual(te_idx, 1, 1)

    # ---- Plug-in functionals (binary mediator expectations) ----
    # E[Y(1,M₁) | X] = μ(1,1)p(M=1|A=1,X) + μ(1,0)p(M=0|A=1,X)
    Ey_1_M1 = yhat_11 * pm1_a1 + yhat_10 * pm0_a1

    # E[Y(0,M₀) | X] = μ(0,1)p(M=1|A=0,X) + μ(0,0)p(M=0|A=0,X)
    Ey_0_M0 = yhat_01 * pm1_a0 + yhat_00 * pm0_a0

    # E[Y(1,M₀) | X] = μ(1,1)p(M=1|A=0,X) + μ(1,0)p(M=0|A=0,X)
    Ey_1_M0 = yhat_11 * pm1_a0 + yhat_10 * pm0_a0

    # E[Y(0,M₁) | X] = μ(0,1)p(M=1|A=1,X) + μ(0,0)p(M=0|A=1,X)
    Ey_0_M1 = yhat_01 * pm1_a1 + yhat_00 * pm0_a1

    # ---- Unit-level effects ----
    te_i = Ey_1_M1 - Ey_0_M0  # Total effect
    dir_i = Ey_1_M0 - Ey_0_M0  # Direct effect (same algebra for IDE/NDE)
    ind_i = te_i - dir_i  # Indirect effect (IIE = TE - IDE)

    # Sanity check: for natural effects, this should equal Ey_1_M1 - Ey_1_M0
    # For interventional effects, this is the proper definition
    if effect_type == "natural":
        # For natural effects, indirect effect should equal Ey_1_M1 - Ey_1_M0 (within tolerance)
        if not np.allclose(ind_i, Ey_1_M1 - Ey_1_M0, atol=1e-8):
            raise AssertionError(
                "Sanity check failed: indirect effect does not match Ey_1_M1 - Ey_1_M0 for natural effects."
            )

    # ---- Aggregate effects ----
    te = float(np.mean(te_i))
    direct = float(np.mean(dir_i))
    indirect = float(np.mean(ind_i))

    # Proportion mediated with guard against division by zero
    prop = float(np.nan) if abs(te) < 1e-12 else float(indirect / te)

    # ---- Optional detailed output ----
    detail = None
    if return_detail:
        detail = dict(
            yhat_00=yhat_00,
            yhat_01=yhat_01,
            yhat_10=yhat_10,
            yhat_11=yhat_11,
            pm1_a0=pm1_a0,
            pm1_a1=pm1_a1,
            pm0_a0=pm0_a0,
            pm0_a1=pm0_a1,
            unit_te=te_i,
            unit_dir=dir_i,
            unit_ind=ind_i,
            Ey_1_M1=Ey_1_M1,
            Ey_0_M0=Ey_0_M0,
            Ey_1_M0=Ey_1_M0,
            Ey_0_M1=Ey_0_M1,
            outcome_fold=outcome_fold,  # New diagnostic information
        )

    # ---- Return results based on effect type ----
    scale = "risk_difference" if outcome_type == "binary" else "mean_difference"
    
    if effect_type == "interventional":
        return dict(
            te=te,
            ide=direct,  # interventional direct effect
            iie=indirect,  # interventional indirect effect
            prop_mediated=prop,
            mediator_type="binary",
            scale=scale,
            detail=detail,
        )
    elif effect_type == "natural":
        # Same algebra, but labeled as natural effects for proper interpretation
        return dict(
            te=te,
            nde=direct,  # natural direct effect
            nie=indirect,  # natural indirect effect
            prop_mediated=prop,
            mediator_type="binary",
            scale=scale,
            detail=detail,
        )
    else:
        raise ValueError("effect_type must be 'interventional' or 'natural'.")


def _estimate_mediation_continuous(
    X: np.ndarray,
    A: np.ndarray,
    M: np.ndarray,
    Y: np.ndarray,
    model_mediator: BaseEstimator,
    model_outcome: BaseEstimator,
    n_splits_mediator: int,
    n_splits_outcome: int,
    groups: Optional[np.ndarray],
    seed_med: int,
    seed_out: int,
    seed_mc: int,
    n_mc_mediator: int,
    residual_pool: str,
    residual_knn: int,
    standardize_X_for_knn: bool,
    clip_m_support: Optional[Tuple[float, float]],
    quantile_bounds: Tuple[float, float],
    max_truncation_warn: float,
    prob_clip_eps_outcome: float,
    outcome_type: str,
    effect_type: str,
    return_detail: bool,
) -> dict:
    """Handle continuous mediator case with residual-bootstrap sampling for both binary and continuous outcomes."""

    # Validate residual pool parameter
    if residual_pool not in ["knn", "global"]:
        raise ValueError(
            f"residual_pool must be 'knn' or 'global', got '{residual_pool}'"
        )

    # For binary outcomes, check that outcome model supports predict_proba
    if outcome_type == "binary" and not hasattr(model_outcome, "predict_proba"):
        raise TypeError(
            "model_outcome must implement predict_proba for binary outcome."
        )

    # ---- Mediator model: E[M | A, X] with cross-fitting for residuals ----
    X_med = np.hstack([X, A.reshape(-1, 1)])
    splitter_med = _make_splitter(
        n_splits=n_splits_mediator, shuffle=True, seed=seed_med, groups=groups
    )

    # Cross-validated predictions to get out-of-fold residuals
    med_cv_model = clone(model_mediator)
    if "random_state" in med_cv_model.get_params(deep=False):
        med_cv_model.set_params(random_state=seed_med)
    m_hat_cv = cross_val_predict(med_cv_model, X_med, M, cv=splitter_med, groups=groups)
    residuals = M - m_hat_cv

    # Fit full mediator model for counterfactual predictions
    med_fit = clone(model_mediator)
    if "random_state" in med_fit.get_params(deep=False):
        med_fit.set_params(random_state=seed_med)
    med_fit.fit(X_med, M)

    # Get counterfactual mediator means
    X_a0 = np.hstack([X, np.zeros_like(A).reshape(-1, 1)])
    X_a1 = np.hstack([X, np.ones_like(A).reshape(-1, 1)])
    m_mean_a0 = med_fit.predict(X_a0)
    m_mean_a1 = med_fit.predict(X_a1)

    # ---- Overlap diagnostics ----
    # Compare distributions of counterfactual mediator means
    if HAS_SCIPY:
        ks_stat, _ = ks_2samp(m_mean_a0, m_mean_a1)
        # Heuristic threshold; adjust if needed
        if ks_stat > 0.6:
            warnings.warn(
                f"Low mediator overlap by predicted means: KS statistic={ks_stat:.2f}. "
                "Estimates may rely on extrapolation; consider model re-specification or stronger clipping.",
                UserWarning
            )
    else:
        # Fallback using simple L1 distance between empirical CDFs
        # This is a simpler overlap diagnostic when scipy is not available
        sorted_a0 = np.sort(m_mean_a0)
        sorted_a1 = np.sort(m_mean_a1)
        # Compute L1 distance on a common grid
        combined = np.concatenate([sorted_a0, sorted_a1])
        grid = np.linspace(combined.min(), combined.max(), 100)
        cdf_a0 = np.searchsorted(sorted_a0, grid, side='right') / len(sorted_a0)
        cdf_a1 = np.searchsorted(sorted_a1, grid, side='right') / len(sorted_a1)
        l1_dist = np.mean(np.abs(cdf_a0 - cdf_a1))
        if l1_dist > 0.3:  # Heuristic threshold
            warnings.warn(
                f"Low mediator overlap by predicted means: L1 distance={l1_dist:.2f}. "
                "Estimates may rely on extrapolation; consider model re-specification or stronger clipping.",
                UserWarning
            )

    # ---- Set up clipping bounds (per arm) ----
    if clip_m_support is not None:
        m_lo_a0 = m_lo_a1 = clip_m_support[0]
        m_hi_a0 = m_hi_a1 = clip_m_support[1]
    else:
        m_lo_a0 = np.quantile(M[A == 0], quantile_bounds[0]) if np.any(A == 0) else M.min()
        m_hi_a0 = np.quantile(M[A == 0], quantile_bounds[1]) if np.any(A == 0) else M.max()
        m_lo_a1 = np.quantile(M[A == 1], quantile_bounds[0]) if np.any(A == 1) else M.min()
        m_hi_a1 = np.quantile(M[A == 1], quantile_bounds[1]) if np.any(A == 1) else M.max()

    if residual_pool == "knn":
        # Prepare for KNN-based residual sampling
        X_for_knn = X.copy()
        if standardize_X_for_knn:
            scaler = StandardScaler()
            X_for_knn = scaler.fit_transform(X_for_knn)

        # Separate residuals and KNN indices by treatment arm
        nn_a0 = NearestNeighbors(n_neighbors=min(residual_knn, np.sum(A == 0))).fit(
            X_for_knn[A == 0]
        )
        nn_a1 = NearestNeighbors(n_neighbors=min(residual_knn, np.sum(A == 1))).fit(
            X_for_knn[A == 1]
        )
        residuals_a0 = residuals[A == 0]
        residuals_a1 = residuals[A == 1]

    def sample_mediator(mean_vals: np.ndarray, treatment_arm: int) -> tuple[np.ndarray, int]:
        """Sample mediator values using residual bootstrap."""
        n_units = len(mean_vals)
        samples = np.zeros((n_units, n_mc_mediator))
        n_clipped_local = 0

        for i in range(n_units):
            # Create reproducible random state for this unit
            unit_rng = np.random.default_rng(seed_mc + i + treatment_arm * n_units)

            if residual_pool == "global":
                # Sample from all residuals in the treatment arm
                resid_pool = residuals[A == treatment_arm]
            else:  # KNN
                # Sample from KNN residual pool
                if treatment_arm == 0:
                    _, knn_idx = nn_a0.kneighbors(X_for_knn[i:i+1])
                    resid_pool = residuals_a0[knn_idx[0]]
                else:
                    _, knn_idx = nn_a1.kneighbors(X_for_knn[i:i+1])
                    resid_pool = residuals_a1[knn_idx[0]]

            drawn = unit_rng.choice(resid_pool, size=n_mc_mediator, replace=True)
            raw = mean_vals[i] + drawn

            # choose per-arm bounds
            lo = m_lo_a0 if treatment_arm == 0 else m_lo_a1
            hi = m_hi_a0 if treatment_arm == 0 else m_hi_a1

            clipped = np.clip(raw, lo, hi)
            # count truncations precisely
            n_clipped_local += np.count_nonzero((raw < lo) | (raw > hi))
            samples[i] = clipped

        return samples, n_clipped_local

    # Sample mediator values for counterfactual scenarios
    M_samples_a0, n_clip_a0 = sample_mediator(m_mean_a0, 0)  # M ~ p(M|A=0,X)
    M_samples_a1, n_clip_a1 = sample_mediator(m_mean_a1, 1)  # M ~ p(M|A=1,X)

    # Track truncation statistics
    n_total_samples = M_samples_a0.size + M_samples_a1.size
    truncation_frac = (n_clip_a0 + n_clip_a1) / n_total_samples

    if truncation_frac > max_truncation_warn:
        warnings.warn(
            f"Large fraction of mediator draws were truncated: {truncation_frac:.3f} > {max_truncation_warn}. "
            f"This may indicate overlap violations or model misspecification. "
            f"Consider adjusting clip_m_support or quantile_bounds.",
            UserWarning,
        )

    # ---- Outcome model: E[Y | A, M, X] with cross-fitting ----
    X_out = np.hstack([X, A.reshape(-1, 1), M.reshape(-1, 1)])
    
    # Set up cross-fitting splitter for outcome model
    splitter_out = _make_splitter(
        n_splits=n_splits_outcome, shuffle=True, seed=seed_out, groups=groups
    )
    
    # Initialize arrays for cross-fitted predictions
    n_units = len(X)
    Ey_1_M1 = np.zeros(n_units)
    Ey_0_M0 = np.zeros(n_units)
    Ey_1_M0 = np.zeros(n_units)
    Ey_0_M1 = np.zeros(n_units)
    
    # Track which fold each unit belongs to for diagnostics
    outcome_fold = np.full(n_units, -1, dtype=int)
    
    # Cross-fit outcome models and compute Monte Carlo expectations
    for fold, (tr_idx, te_idx) in enumerate(splitter_out.split(X_out, groups=groups)):
        if len(tr_idx) == 0 or len(te_idx) == 0:
            continue
        
        # Fit outcome model on training fold
        out_fit = clone(model_outcome)
        if "random_state" in out_fit.get_params(deep=False):
            out_fit.set_params(random_state=int(np.random.RandomState(seed_out + fold).randint(2**31 - 1)))
        out_fit.fit(X_out[tr_idx], Y[tr_idx])
        
        # Record fold assignments for diagnostics
        outcome_fold[te_idx] = fold
        
        # For each unit in test fold, compute Monte Carlo expectations
        for i in te_idx:
            # E[Y(1,M₁) | X] - average over M ~ p(M|A=1,X)
            X_rep = np.tile(X[i], (n_mc_mediator, 1))
            A_rep = np.ones(n_mc_mediator)
            M_rep = M_samples_a1[i]
            X_full = np.hstack([X_rep, A_rep.reshape(-1, 1), M_rep.reshape(-1, 1)])
            if outcome_type == "binary":
                y_probs = out_fit.predict_proba(X_full)[:, 1]
                y_probs = np.clip(y_probs, prob_clip_eps_outcome, 1 - prob_clip_eps_outcome)
                Ey_1_M1[i] = np.mean(y_probs)
            else:
                y_pred = out_fit.predict(X_full)
                Ey_1_M1[i] = np.mean(y_pred)
            
            # E[Y(0,M₀) | X] - average over M ~ p(M|A=0,X)
            X_rep = np.tile(X[i], (n_mc_mediator, 1))
            A_rep = np.zeros(n_mc_mediator)
            M_rep = M_samples_a0[i]
            X_full = np.hstack([X_rep, A_rep.reshape(-1, 1), M_rep.reshape(-1, 1)])
            if outcome_type == "binary":
                y_probs = out_fit.predict_proba(X_full)[:, 1]
                y_probs = np.clip(y_probs, prob_clip_eps_outcome, 1 - prob_clip_eps_outcome)
                Ey_0_M0[i] = np.mean(y_probs)
            else:
                y_pred = out_fit.predict(X_full)
                Ey_0_M0[i] = np.mean(y_pred)
            
            # E[Y(1,M₀) | X] - A=1 but M ~ p(M|A=0,X)
            X_rep = np.tile(X[i], (n_mc_mediator, 1))
            A_rep = np.ones(n_mc_mediator)
            M_rep = M_samples_a0[i]
            X_full = np.hstack([X_rep, A_rep.reshape(-1, 1), M_rep.reshape(-1, 1)])
            if outcome_type == "binary":
                y_probs = out_fit.predict_proba(X_full)[:, 1]
                y_probs = np.clip(y_probs, prob_clip_eps_outcome, 1 - prob_clip_eps_outcome)
                Ey_1_M0[i] = np.mean(y_probs)
            else:
                y_pred = out_fit.predict(X_full)
                Ey_1_M0[i] = np.mean(y_pred)
            
            # E[Y(0,M₁) | X] - A=0 but M ~ p(M|A=1,X)
            X_rep = np.tile(X[i], (n_mc_mediator, 1))
            A_rep = np.zeros(n_mc_mediator)
            M_rep = M_samples_a1[i]
            X_full = np.hstack([X_rep, A_rep.reshape(-1, 1), M_rep.reshape(-1, 1)])
            if outcome_type == "binary":
                y_probs = out_fit.predict_proba(X_full)[:, 1]
                y_probs = np.clip(y_probs, prob_clip_eps_outcome, 1 - prob_clip_eps_outcome)
                Ey_0_M1[i] = np.mean(y_probs)
            else:
                y_pred = out_fit.predict(X_full)
                Ey_0_M1[i] = np.mean(y_pred)

    # ---- Unit-level effects ----
    te_i = Ey_1_M1 - Ey_0_M0  # Total effect
    dir_i = Ey_1_M0 - Ey_0_M0  # Direct effect (same algebra for IDE/NDE)
    ind_i = te_i - dir_i  # Indirect effect (IIE = TE - IDE)

    # Sanity check: for natural effects, this should equal Ey_1_M1 - Ey_1_M0
    if effect_type == "natural":
        if not np.allclose(ind_i, Ey_1_M1 - Ey_1_M0, atol=1e-6):
            warnings.warn(
                "Sanity check: indirect effect differs from Ey_1_M1 - Ey_1_M0 for natural effects. "
                "This may be due to Monte Carlo error.",
                UserWarning,
            )

    # ---- Aggregate effects ----
    te = float(np.mean(te_i))
    direct = float(np.mean(dir_i))
    indirect = float(np.mean(ind_i))

    # Proportion mediated with guard against division by zero
    prop = float(np.nan) if abs(te) < 1e-12 else float(indirect / te)

    # ---- Optional detailed output ----
    detail = None
    if return_detail:
        # Summaries only
        M_a0_mean = M_samples_a0.mean(axis=1)
        M_a0_sd = M_samples_a0.std(axis=1, ddof=1)
        M_a1_mean = M_samples_a1.mean(axis=1)
        M_a1_sd = M_samples_a1.std(axis=1, ddof=1)

        detail = dict(
            # Mediator draw summaries & diagnostics
            m_mean_a0=m_mean_a0, m_mean_a1=m_mean_a1,
            M_a0_mean=M_a0_mean, M_a0_sd=M_a0_sd,
            M_a1_mean=M_a1_mean, M_a1_sd=M_a1_sd,
            residuals=residuals,
            truncation_frac=truncation_frac,
            clip_bounds_a0=(m_lo_a0, m_hi_a0),
            clip_bounds_a1=(m_lo_a1, m_hi_a1),
            # Effects and counterfactual expectations
            unit_te=te_i, unit_dir=dir_i, unit_ind=ind_i,
            Ey_1_M1=Ey_1_M1, Ey_0_M0=Ey_0_M0, Ey_1_M0=Ey_1_M0, Ey_0_M1=Ey_0_M1,
            outcome_fold=outcome_fold,  # New diagnostic information
        )

    # ---- Return results based on effect type ----
    scale = "risk_difference" if outcome_type == "binary" else "mean_difference"
    
    if effect_type == "interventional":
        return dict(
            te=te,
            ide=direct,  # interventional direct effect
            iie=indirect,  # interventional indirect effect
            prop_mediated=prop,
            mediator_type="continuous",
            scale=scale,
            detail=detail,
        )
    elif effect_type == "natural":
        return dict(
            te=te,
            nde=direct,  # natural direct effect
            nie=indirect,  # natural indirect effect
            prop_mediated=prop,
            mediator_type="continuous",
            scale=scale,
            detail=detail,
        )
    else:
        raise ValueError("effect_type must be 'interventional' or 'natural'.")
