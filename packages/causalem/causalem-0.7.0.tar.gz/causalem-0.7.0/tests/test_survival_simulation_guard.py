import numpy as np
import pytest
from sksurv.functions import StepFunction

from causalem.estimation.ensemble import _estimate_te_survival, _estimate_te_survival_multi


def _simple_sf():
    return StepFunction(x=np.array([0.0, 1.0]), y=np.array([1.0, 0.5]))


def test_estimate_te_survival_raises_on_missing_sf(monkeypatch):
    def _fake_stage1(*args, **kwargs):
        matched_union = np.array([0, 1])
        sf = _simple_sf()
        sf_fact = [sf, None]
        sf_cf = [sf, sf]
        cluster_mat = np.zeros((2, 1))
        return matched_union, sf_fact, sf_cf, cluster_mat

    monkeypatch.setattr(
        "causalem.estimation.ensemble.stage_1_meta_survival", _fake_stage1
    )

    X = np.zeros((2, 1))
    t = np.array([0, 1])
    y = np.array([[1.0, 1], [2.0, 1]], dtype=float)
    rng = np.random.default_rng(0)

    with pytest.raises(ValueError, match="Missing survival prediction"):
        _estimate_te_survival(
            X,
            t,
            y,
            rng_master=rng,
            outcome_templates=[object(), object()],
            niter=2,
            model_meta=None,
        )


def test_estimate_te_survival_multi_raises_on_missing_sf(monkeypatch):
    def _fake_stage1_multi(*args, **kwargs):
        matched_idx = np.array([0, 1])
        sf = _simple_sf()
        sf_all = [[sf, None], [sf, sf]]
        names = np.array(["A", "B"], dtype=object)
        cluster_mat = np.zeros((2, 1))
        return matched_idx, sf_all, names, cluster_mat

    monkeypatch.setattr(
        "causalem.estimation.ensemble.stage_1_meta_survival_multi", _fake_stage1_multi
    )

    X = np.zeros((2, 1))
    t = np.array(["A", "B"], dtype=object)
    y = np.array([[1.0, 1], [2.0, 1]], dtype=float)
    rng = np.random.default_rng(0)

    with pytest.raises(ValueError, match="Missing survival prediction"):
        _estimate_te_survival_multi(
            X,
            t,
            y,
            rng_master=rng,
            outcome_templates=[object(), object()],
            niter=2,
            model_meta=None,
        )
