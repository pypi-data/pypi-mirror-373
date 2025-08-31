import numpy as np

from causalem import stochastic_match

# ----- helper dataset ------------------------------------------------------
rng = np.random.default_rng(0)
n_per = 40
treat = np.repeat([0, 1, 2], n_per)  # three arms
score = rng.normal(size=treat.size)  # dummy scalar score


def _cluster_ok(cid, t):
    """Verify each non-negative cluster id has exactly one of each arm."""
    for c in np.unique(cid[cid >= 0]):
        idx = np.where(cid == c)[0]
        if len(idx) != 3:
            return False
        if set(t[idx]) != {0, 1, 2}:
            return False
    return True


# ---------------------------------------------------------------------------


def test_multi_deterministic():
    cid = stochastic_match(
        treatment=treat,
        score=score,
        ref_group=0,
        nsmp=0,
    )
    assert cid.shape == (treat.size, 1)
    assert _cluster_ok(cid.ravel(), treat)


def test_multi_stochastic_reproducible():
    cid1 = stochastic_match(
        treatment=treat,
        score=score,
        ref_group=0,
        scale=0.1,
        nsmp=2,
        random_state=123,
    )
    cid2 = stochastic_match(
        treatment=treat,
        score=score,
        ref_group=0,
        scale=0.1,
        nsmp=2,
        random_state=123,
    )
    assert np.array_equal(cid1, cid2)
    # shape & cluster integrity
    assert cid1.shape == (treat.size, 2)
    assert _cluster_ok(cid1[:, 0], treat)
    assert _cluster_ok(cid1[:, 1], treat)


def test_multi_2d_score():
    # create a fake (G−1)=2 logit matrix
    score_2d = rng.normal(size=(treat.size, 2))
    cid = stochastic_match(
        treatment=treat,
        score=score_2d,
        ref_group=0,
        nsmp=0,
    )
    assert _cluster_ok(cid.ravel(), treat)
