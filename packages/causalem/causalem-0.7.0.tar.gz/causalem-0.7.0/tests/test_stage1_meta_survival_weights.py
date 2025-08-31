import numpy as np
from sksurv.ensemble import RandomSurvivalForest

from causalem import load_data_tof
from causalem.estimation.ensemble import (
    stage_1_meta_survival,
    stage_1_meta_survival_multi,
)
from causalem.utils._weights import appearance_weights


class RSFCheck(RandomSurvivalForest):
    def fit(self, X, y, sample_weight=None):
        if sample_weight is None:
            raise RuntimeError("sample_weight missing")
        return super().fit(X, y, sample_weight=sample_weight)

def _make_binary_surv_data(n: int = 200):
    """Small binary-treatment survival sample from the TOF data."""
    X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])
    rng = np.random.default_rng(0)
    idx = rng.choice(len(t), size=n, replace=False)
    return X[idx], t[idx], y[idx]


def test_stage1_meta_survival_uses_weights_and_union():
    X, treatment, y = _make_binary_surv_data()
    rng = np.random.default_rng(0)
    outcome_templates = [RandomSurvivalForest(n_estimators=10, random_state=0, n_jobs=1)]
    matched_union, sf_f, sf_cf, cluster_mat = stage_1_meta_survival(
        X,
        treatment,
        y,
        rng_master=rng,
        outcome_templates=outcome_templates,
        niter=1,
        model_meta=RSFCheck(n_estimators=10, random_state=1, n_jobs=1),
        n_splits_propensity=2,
        n_splits_outcome=2,
        matching_is_stochastic=False,
    )
    weights = appearance_weights(cluster_mat)
    assert np.array_equal(matched_union, np.where(weights > 0)[0])
    assert set(treatment[matched_union]) == {0, 1}
def _make_multi_surv_data(n_per_group: int = 30):
    """Balanced multi-arm survival sample from the TOF data."""
    df = load_data_tof(raw=True)
    # sample equally from each treatment group for speed and balance
    df_bal = (
        df.groupby("treatment")
        .apply(lambda g: g.sample(n=n_per_group, random_state=0))
        .reset_index(drop=True)
    )
    X = df_bal[["age", "zscore"]].to_numpy(dtype=float)
    t = df_bal["treatment"].to_numpy()
    y = df_bal[["time", "status"]].to_numpy(dtype=float)
    return X, t, y


def test_stage1_meta_survival_multi_uses_weights_and_union():
    X, treatment, y = _make_multi_surv_data()
    rng = np.random.default_rng(0)
    outcome_templates = [RandomSurvivalForest(n_estimators=10, random_state=0, n_jobs=1)]
    matched_union, sf_all, treatment_names, cluster_mat = stage_1_meta_survival_multi(
        X,
        treatment,
        y,
        rng_master=rng,
        outcome_templates=outcome_templates,
        niter=1,
        model_meta=RSFCheck(n_estimators=10, random_state=1, n_jobs=1),
        n_splits_propensity=2,
        n_splits_outcome=2,
        matching_is_stochastic=False,
        ref_group="PrP",
    )
    weights = appearance_weights(cluster_mat)
    assert np.array_equal(matched_union, np.where(weights > 0)[0])
    assert set(np.unique(treatment[matched_union])) == {"PrP", "SPS", "RVOTd"}
