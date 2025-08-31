import numpy as np
import pytest
from pandas.testing import assert_frame_equal
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sksurv.ensemble import RandomSurvivalForest
from sksurv.linear_model import CoxPHSurvivalAnalysis

from causalem import estimate_te, load_data_lalonde, load_data_tof
from causalem.estimation.ensemble import estimate_te_multi

# -------------------------------------------------------------------
# Helpers / lightweight configs
# -------------------------------------------------------------------
KW_COMMON = dict(
    niter=1,  # single-iteration fast path
    n_splits_propensity=3,
    n_splits_outcome=3,
    matching_is_stochastic=False,
    matching_scale=1.0,
    matching_caliper=None,
)

KW_NO_STACK = {**KW_COMMON, "niter": 2, "do_stacking": False}


# -------------------------------------------------------------------
# Continuous outcome (Lalonde, re78)
# -------------------------------------------------------------------
def test_te_continuous_runs_and_reproducible():
    X, t, y = load_data_lalonde(raw=False)

    model = RandomForestRegressor(n_estimators=20)
    out1 = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=model,
        random_state_master=123,
        **KW_COMMON,
    )
    out2 = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=model,
        random_state_master=123,
        **KW_COMMON,
    )
    assert "te" in out1 and np.isfinite(out1["te"])
    assert "matching" in out1 and out1["matching"].shape == (X.shape[0], 1)
    # reproducibility
    assert np.isclose(out1["te"], out2["te"])


# -------------------------------------------------------------------
# Binary outcome (Lalonde, indicator re78 > 3700)
# -------------------------------------------------------------------
def test_te_binary_runs_and_in_range():
    X, t, y = load_data_lalonde(raw=False)
    y_bin = (y > 3700).astype(int)

    res = estimate_te(
        X,
        t,
        y_bin,
        outcome_type="binary",
        model_outcome=RandomForestClassifier(n_estimators=20),
        random_state_master=42,
        **KW_COMMON,
    )
    assert -1.0 <= res["te"] <= 1.0
    assert "matching" in res and res["matching"].shape == (X.shape[0], 1)


# -------------------------------------------------------------------
# Survival outcome (TOF data)
# -------------------------------------------------------------------
def test_te_survival_runs_and_reproducible():
    X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])

    model = RandomSurvivalForest(n_estimators=20, n_jobs=1)
    res1 = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=model,
        random_state_master=7,
        **KW_COMMON,
    )
    res2 = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=model,
        random_state_master=7,
        **KW_COMMON,
    )
    assert "te" in res1 and np.isfinite(res1["te"])
    assert "matching" in res1 and res1["matching"].shape == (X.shape[0], 1)
    assert np.isclose(res1["te"], res2["te"])


def test_te_survival_respects_n_mc():
    X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])

    model = RandomSurvivalForest(n_estimators=20, n_jobs=1)
    res1 = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=model,
        random_state_master=7,
        n_mc=1,
        **KW_COMMON,
    )
    res2 = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=model,
        random_state_master=7,
        n_mc=3,
        **KW_COMMON,
    )
    assert not np.isclose(res1["te"], res2["te"])


def test_te_survival_meta_linear():
    X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])

    base = RandomSurvivalForest(n_estimators=10, n_jobs=1)
    meta = CoxPHSurvivalAnalysis()
    res1 = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        model_meta=meta,
        random_state_master=3,
        **{**KW_COMMON, "niter": 3},
    )
    res2 = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        model_meta=meta,
        random_state_master=3,
        **{**KW_COMMON, "niter": 3},
    )
    assert np.isfinite(res1["te"])
    assert np.isclose(res1["te"], res2["te"])


def test_te_survival_multi_meta_reproducible():
    df = load_data_tof(raw=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df[["time", "status"]].to_numpy()

    base = RandomSurvivalForest(n_estimators=100, n_jobs=1)
    # meta = CoxPHSurvivalAnalysis()
    meta = RandomSurvivalForest(n_estimators=100, n_jobs=1)

    kw = {**KW_COMMON, "niter": 2, "ref_group": "PrP"}
    res1 = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        model_meta=meta,
        random_state_master=17,
        **kw,
    )
    res2 = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        model_meta=meta,
        random_state_master=17,
        **kw,
    )

    df1 = (
        res1["pairwise"]
        .sort_values(["treatment_1", "treatment_2"])
        .reset_index(drop=True)
    )
    df2 = (
        res2["pairwise"]
        .sort_values(["treatment_1", "treatment_2"])
        .reset_index(drop=True)
    )
    assert_frame_equal(df1, df2)
    assert np.all(np.isfinite(df1["te"]))
    assert "matching" in res1 and res1["matching"].shape == (X.shape[0], kw["niter"])


def test_te_survival_multi_naive_avg():
    df = load_data_tof(raw=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df[["time", "status"]].to_numpy()

    base = RandomSurvivalForest(n_estimators=10, n_jobs=1)

    kw = {**KW_COMMON, "niter": 2, "ref_group": "PrP", "do_stacking": False}
    res1 = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        model_meta=None,
        random_state_master=17,
        **kw,
    )
    res2 = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        model_meta=None,
        random_state_master=17,
        **kw,
    )

    df1 = (
        res1["pairwise"]
        .sort_values(["treatment_1", "treatment_2"])
        .reset_index(drop=True)
    )
    df2 = (
        res2["pairwise"]
        .sort_values(["treatment_1", "treatment_2"])
        .reset_index(drop=True)
    )
    assert_frame_equal(df1, df2)
    assert np.all(np.isfinite(df1["te"]))


def test_te_survival_multi_bootstrap_runs():
    df = load_data_tof(raw=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df[["time", "status"]].to_numpy()

    base = RandomSurvivalForest(n_estimators=10, n_jobs=1)
    meta = RandomSurvivalForest(n_estimators=10, n_jobs=1)

    kw = {**KW_COMMON, "ref_group": "PrP"}
    res = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        model_meta=meta,
        nboot=2,
        random_state_master=11,
        **kw,
    )

    assert "boot" in res and "pairwise" in res
    # ensure bootstrapped draws exist for all treatment pairs
    pairs = [
        tuple(x) for x in res["pairwise"][["treatment_1", "treatment_2"]].to_numpy()
    ]
    for pair in pairs:
        assert pair in res["boot"]
        assert len(res["boot"][pair]) == 2
    assert "matching" in res and res["matching"].shape[0] == X.shape[0]


def test_te_survival_multi_respects_n_mc():
    df = load_data_tof(raw=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df[["time", "status"]].to_numpy()

    base = RandomSurvivalForest(n_estimators=10, n_jobs=1)

    res1 = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        random_state_master=5,
        n_mc=1,
        ref_group="PrP",
        **KW_COMMON,
    )
    res2 = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=base,
        random_state_master=5,
        n_mc=3,
        ref_group="PrP",
        **KW_COMMON,
    )

    df1 = (
        res1["pairwise"]
        .sort_values(["treatment_1", "treatment_2"])
        .reset_index(drop=True)
    )
    df2 = (
        res2["pairwise"]
        .sort_values(["treatment_1", "treatment_2"])
        .reset_index(drop=True)
    )
    assert not np.allclose(df1["te"], df2["te"])


def test_te_multi_bootstrap_fastpath_binary():
    df = load_data_tof(raw=True, binarize_outcome=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df["outcome"].to_numpy()

    res = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="binary",
        niter=1,
        nboot=2,
        ref_group="PrP",
        random_state_master=3,
    )

    assert res["per_treatment"].shape == (3, 4)
    assert res["pairwise"].shape == (3, 5)
    for key in ["PrP", "RVOTd", "SPS"]:
        assert len(res["boot"][key]) == 2
    assert res["matching"].shape == (X.shape[0], 1)


@pytest.mark.parametrize(
    "extra",
    [
        {"niter": 1},
        {"niter": 1, "nboot": 1},
        {"niter": 2, "do_stacking": False},
        {"niter": 2, "do_stacking": True},
    ],
)
def test_te_multi_binary_uniform_structure(extra):
    df = load_data_tof(raw=True, binarize_outcome=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df["outcome"].to_numpy()

    res = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="binary",
        model_outcome=RandomForestClassifier(n_estimators=5),
        random_state_master=0,
        ref_group="PrP",
        **extra,
    )

    assert set(res) == {"per_treatment", "pairwise", "boot", "matching"}
    assert set(res["per_treatment"].columns).issuperset({"treatment", "mean"})
    assert set(res["pairwise"].columns).issuperset({"treatment_1", "treatment_2", "te"})
    assert isinstance(res["boot"], dict)
    assert res["matching"].shape[0] == X.shape[0]


def test_te_multi_survival_uniform_structure_fastpath():
    df = load_data_tof(raw=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df[["time", "status"]].to_numpy()

    res = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=RandomSurvivalForest(n_estimators=5, n_jobs=1),
        random_state_master=1,
        niter=1,
        ref_group="PrP",
    )

    assert set(res) == {"per_treatment", "pairwise", "boot", "matching"}
    assert res["per_treatment"].empty
    assert list(res["pairwise"].columns) == ["treatment_1", "treatment_2", "te"]
    assert isinstance(res["boot"], dict)
    assert res["matching"].shape[0] == X.shape[0]


def test_te_bootstrap_returns_expected_keys():
    X, t, y = load_data_lalonde(raw=False)

    res = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=5),
        niter=1,
        nboot=1,
        random_state_master=5,
    )

    assert set(res) == {"te", "ci", "boot", "matching"}
    assert isinstance(res["boot"], np.ndarray)
    assert len(res["boot"]) == 1
    assert res["matching"].shape[0] == X.shape[0]


def test_te_no_stacking_reproducible():
    X, t, y = load_data_lalonde(raw=False)

    model = RandomForestRegressor(n_estimators=20)
    res1 = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=model,
        random_state_master=123,
        **KW_NO_STACK,
    )
    res2 = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=model,
        random_state_master=123,
        **KW_NO_STACK,
    )
    assert np.isclose(res1["te"], res2["te"])
    assert res1["matching"].shape == (X.shape[0], KW_NO_STACK["niter"])


def test_te_no_stacking_errors():
    X = np.zeros((6, 2))
    t = np.array([0, 1, 2, 0, 1, 2])
    y = np.arange(6)
    with pytest.raises(ValueError):
        estimate_te(X, t, y, outcome_type="continuous", **KW_NO_STACK)

    Xs, ts, ys = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])
    res = estimate_te(
        Xs,
        ts,
        ys,
        outcome_type="survival",
        model_outcome=RandomSurvivalForest(n_estimators=10, n_jobs=1),
        **KW_NO_STACK,
    )
    assert np.isfinite(res["te"]) and res["matching"].shape == (
        Xs.shape[0],
        KW_NO_STACK["niter"],
    )


def test_te_two_arm_averages_over_all_matched():
    X, t, y = load_data_lalonde(raw=False)
    model = RandomForestRegressor(n_estimators=5)
    kw = dict(
        outcome_type="continuous",
        model_outcome=model,
        niter=1,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        matching_scale=1.0,
        matching_caliper=None,
        random_state_master=0,
    )
    res = estimate_te(X, t, y, **kw)

    from causalem.estimation.ensemble import stage_1_single_iter

    rng = np.random.default_rng(0)
    seed_iter = int(rng.integers(2**32))
    cid, yp, yp_cf = stage_1_single_iter(
        X,
        t,
        y,
        rng=np.random.default_rng(seed_iter),
        outcome_is_binary=False,
        n_splits_propensity=3,
        model_propensity=LogisticRegression(solver="newton-cg"),
        matching_scale=1.0,
        matching_caliper=None,
        n_splits_outcome=3,
        model_outcome=model,
        matching_is_stochastic=False,
        prob_clip_eps=1e-6,
    )
    matched_idx = np.where(cid != -1)[0]
    yp_treat = np.where(t == 1, yp, yp_cf)
    yp_ctrl = np.where(t == 1, yp_cf, yp)
    te_expected = np.mean(yp_treat[matched_idx]) - np.mean(yp_ctrl[matched_idx])
    te_old = np.mean(yp[np.intersect1d(matched_idx, np.where(t == 1)[0])]) - np.mean(
        yp_cf[np.intersect1d(matched_idx, np.where(t == 1)[0])]
    )
    assert np.isclose(res["te"], te_expected)
    assert not np.isclose(res["te"], te_old)


def test_stacking_passes_appearance_weights(monkeypatch):
    X, t, y = load_data_lalonde(raw=False)

    from causalem.estimation import ensemble

    captured: list[np.ndarray] = []
    orig = ensemble.fit_with_appearance_weights

    def record(estimator, X, y, sample_weight=None, **kwargs):
        captured.append(sample_weight)
        return orig(estimator, X, y, sample_weight=sample_weight, **kwargs)

    monkeypatch.setattr(ensemble, "fit_with_appearance_weights", record)

    estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=5),
        model_meta=LinearRegression(),
        random_state_master=0,
        niter=2,
        n_splits_propensity=2,
        n_splits_outcome=2,
        matching_is_stochastic=False,
    )

    assert captured and all(w is not None and np.any(w != 1) for w in captured)


def test_stacking_passes_appearance_weights_multi(monkeypatch):
    rng = np.random.default_rng(0)
    X = rng.normal(size=(60, 2))
    t = rng.choice(["a", "b", "c"], size=60)
    y = rng.normal(size=60)

    from causalem.estimation import ensemble

    captured: list[np.ndarray] = []
    orig = ensemble.fit_with_appearance_weights

    def record(estimator, X, y, sample_weight=None, **kwargs):
        captured.append(sample_weight)
        return orig(estimator, X, y, sample_weight=sample_weight, **kwargs)

    monkeypatch.setattr(ensemble, "fit_with_appearance_weights", record)

    estimate_te_multi(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=LinearRegression(),
        model_meta=LinearRegression(),
        ref_group="a",
        random_state_master=0,
        niter=2,
        n_splits_propensity=2,
        n_splits_outcome=2,
        matching_is_stochastic=False,
    )

    assert captured and all(w is not None and np.any(w != 1) for w in captured)
