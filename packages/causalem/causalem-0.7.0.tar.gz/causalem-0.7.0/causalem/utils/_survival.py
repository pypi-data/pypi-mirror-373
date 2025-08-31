import numpy as np
import pandas as pd
from sksurv.linear_model import CoxPHSurvivalAnalysis

from ._weights import fit_with_appearance_weights


def fit_cox_marginal_weighted(d, synth, w):
    """Fit a marginal Cox model with appearance weights.

    Parameters
    ----------
    d : array-like
        Binary treatment indicator for each observation.
    synth : structured array
        Survival outcomes as returned by ``_simulate_from_sf``.
    w : array-like
        Appearance counts per observation. Rows with zero weight are ignored.

    Returns
    -------
    float
        The hazard ratio ``exp(beta)`` from the Cox model.
    """
    X = pd.DataFrame({"d": np.asarray(d)})
    mdl = CoxPHSurvivalAnalysis()
    fit_with_appearance_weights(mdl, X, synth, sample_weight=np.asarray(w))
    return float(np.exp(mdl.coef_[0]))
