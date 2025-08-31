import numpy as np
import pandas as pd
from sksurv.linear_model import CoxPHSurvivalAnalysis

from causalem.utils._survival import fit_cox_marginal_weighted


def _toy_surv_data():
    times = np.array([1.0, 2.0, 3.0, 4.0])
    events = np.array([1, 1, 1, 1], dtype=bool)
    d = np.array([0, 1, 0, 1])
    synth = np.array(list(zip(events, times)), dtype=[("event", "bool"), ("time", "f8")])
    return d, synth


def test_weighted_cox_matches_unweighted_when_all_ones():
    d, synth = _toy_surv_data()
    w = np.ones_like(d)
    hr_w = fit_cox_marginal_weighted(d, synth, w)
    mdl = CoxPHSurvivalAnalysis().fit(pd.DataFrame({"d": d}), synth)
    hr_unw = float(np.exp(mdl.coef_[0]))
    assert np.isclose(hr_w, hr_unw)


def test_weighting_affects_hazard_ratio():
    d, synth = _toy_surv_data()
    w = np.array([1, 2, 1, 1])
    hr_weighted = fit_cox_marginal_weighted(d, synth, w)
    d_rep = np.repeat(d, w)
    times_rep = np.repeat(synth["time"], w)
    events_rep = np.repeat(synth["event"], w)
    synth_rep = np.array(list(zip(events_rep, times_rep)), dtype=[("event", "bool"), ("time", "f8")])
    mdl_rep = CoxPHSurvivalAnalysis().fit(pd.DataFrame({"d": d_rep}), synth_rep)
    hr_rep = float(np.exp(mdl_rep.coef_[0]))
    assert np.isclose(hr_weighted, hr_rep)
    hr_unw = fit_cox_marginal_weighted(d, synth, np.ones_like(d))
    assert not np.isclose(hr_weighted, hr_unw)
