import numpy as np
from scipy.special import logit
from sklearn.linear_model import LogisticRegression

from causalem import load_data_lalonde, stochastic_match


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
def _prep_scores():
    """Load Lalonde, fit propensity model, return logit scores + treatment."""
    X, t, _ = load_data_lalonde(raw=False)
    lr = LogisticRegression(solver="newton-cg", C=1.0, max_iter=500)
    lr.fit(X, t)
    p = lr.predict_proba(X)[:, 1]
    scores = logit(np.clip(p, 1e-6, 1 - 1e-6))
    return scores, t


def _combined_ess(cluster_ids: np.ndarray) -> float:
    """Effective sample size across nsmp draws (Rubin-like)."""
    nsmp = cluster_ids.shape[1]
    counts = np.count_nonzero(cluster_ids >= 0, axis=1)
    w = counts / nsmp
    return (w.sum() ** 2) / np.sum(w**2)


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------
def test_reproducibility():
    score, t = _prep_scores()
    cid1 = stochastic_match(
        treatment=t, score=score, scale=1.0, nsmp=1, random_state=123
    )
    cid2 = stochastic_match(
        treatment=t, score=score, scale=1.0, nsmp=1, random_state=123
    )
    assert np.array_equal(cid1, cid2)


def test_score_balance_deterministic():
    score, t = _prep_scores()
    # Before matching
    diff_before = abs(score[t == 1].mean() - score[t == 0].mean())

    # Deterministic matching (nsmp=0)
    cid = stochastic_match(treatment=t, score=score, nsmp=0)
    matched = cid.ravel() >= 0
    diff_after = abs(
        score[(t == 1) & matched].mean() - score[(t == 0) & matched].mean()
    )
    assert diff_after < diff_before


def test_all_treated_matched_without_caliper():
    score, t = _prep_scores()
    cid = stochastic_match(treatment=t, score=score, nsmp=0)  # no caliper
    matched = cid.ravel() >= 0
    assert matched[t == 1].all()


def test_caliper_respects_max_distance():
    score, t = _prep_scores()
    cal = 0.5
    cid = stochastic_match(treatment=t, score=score, nsmp=0, caliper=cal)
    for cid_val in np.unique(cid[cid >= 0]):
        idx = np.where(cid == cid_val)[0]
        if len(idx) == 2:
            d = abs(score[idx[0]] - score[idx[1]])
            assert d <= cal + 1e-12  # numerical tolerance


def test_scale_affects_balance():
    score, t = _prep_scores()
    nsmp = 20
    cid_small = stochastic_match(
        treatment=t, score=score, scale=0.01, nsmp=nsmp, random_state=1
    )
    cid_large = stochastic_match(
        treatment=t, score=score, scale=10.0, nsmp=nsmp, random_state=1
    )

    def _mean_gap(cid):
        gaps = []
        for s in range(cid.shape[1]):
            m = cid[:, s] >= 0
            gaps.append(abs(score[(t == 1) & m].mean() - score[(t == 0) & m].mean()))
        return np.mean(gaps)

    assert _mean_gap(cid_small) < _mean_gap(cid_large)


def test_scale_affects_ess():
    score, t = _prep_scores()
    nsmp = 30
    cid_small = stochastic_match(
        treatment=t, score=score, scale=0.01, nsmp=nsmp, random_state=7
    )
    cid_large = stochastic_match(
        treatment=t, score=score, scale=10.0, nsmp=nsmp, random_state=7
    )
    ess_small = _combined_ess(cid_small)
    ess_large = _combined_ess(cid_large)
    assert ess_small < ess_large


def test_small_scale_large_distance_stochastic():
    t = np.array([1, 1, 0, 0])
    dist = np.array(
        [
            [0.0, 0.0, 2.0, 4.0],
            [0.0, 0.0, 3.0, 2.0],
            [2.0, 3.0, 0.0, 0.0],
            [4.0, 2.0, 0.0, 0.0],
        ]
    )
    cid = stochastic_match(
        treatment=t,
        distance=dist,
        scale=1e-3,
        nsmp=3,
        random_state=0,
    )
    assert cid.shape == (4, 3)
    # At least one pair matched in each draw
    assert (cid >= 0).any(axis=0).all()
