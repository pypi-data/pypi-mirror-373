import numpy as np
import pandas as pd

from . import load_data_tof


def load_data_tof_with_mediator(
    *,
    raw: bool = True,
    treat_levels: list[str] = ["PrP", "RVOTd", "SPS"],
    binarize_outcome: bool = False,
    binarization_threshold: float | None = None,
    outcome_type: str | None = None,
) -> pd.DataFrame | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the simulated tetralogy of Fallot (TOF) dataset with mediator variable.
    
    .. deprecated:: 0.6.3
        Use ``load_data_tof(include_mediator=True, ...)`` instead.
    
    This function is now a wrapper around ``load_data_tof`` with ``include_mediator=True``.
    All functionality has been preserved for backward compatibility.
    
    By default returns a DataFrame with time-to-event information and mediator.
    If ``raw=False``, returns ``(X, t, m, y)`` where:
      • X : array (n × 2) of [age, zscore]
      • t : array (n,) treatment indicator (binary if 2 levels, categorical if 3 levels)
      • m : array (n,) mediator values
      • y : array (n × 2) of [time, status] for "survival", 
            array (n,) binary outcomes for "binary", 
            array (n,) continuous times for "continuous"
    
    The mediator variable represents a continuous post-treatment variable that
    mediates the relationship between treatment and outcome. The mediator values
    are generated with treatment-specific baseline levels and mild dependence
    on patient age (beta_age = 0.10 per unit age scaled by 60 minutes). 
    The mediator is associated with survival outcome through a log hazard ratio
    of approximately 0.20 per 60-minute unit increase.
    
    When ``outcome_type`` is specified, it determines the outcome format:
    - "survival" (default): Returns [time, status] arrays for survival analysis
    - "binary": Converts to binary outcome using binarization_threshold on uncensored time
    - "continuous": Returns uncensored time as continuous outcome
    
    When ``binarize_outcome=True`` (deprecated, use outcome_type="binary" instead),
    the outcome is converted to a binary failure indicator using ``binarization_threshold``.
    The threshold is now applied to uncensored time rather than censored time.
    
    Parameters
    ----------
    raw : bool
        If True, return pd.DataFrame. If False, return (X, t, m, y).
    treat_levels : list[str]
        List of 2 or 3 treatment labels to include.
        Must be subset of the three levels in the data: ['PrP', 'RVOTd', 'SPS'].
        For 2 levels: t is binary indicator (0/1).
        For 3 levels: t is categorical indicator (0/1/2).
    binarize_outcome : bool, default False
        [Deprecated] Convert the time-to-event outcome into a binary failure indicator.
        Use outcome_type="binary" instead.
    binarization_threshold : float or None, default None
        Threshold used for binarization. If ``None`` uses the median uncensored time.
        When outcome_type="binary", this threshold is applied to uncensored time.
    outcome_type : str or None, default None
        Output format: "survival" (default), "binary", or "continuous".
        - "survival": Return [time, status] for survival analysis
        - "binary": Return binary indicators based on uncensored time threshold
        - "continuous": Return uncensored times as continuous outcome
        If None, defaults to "survival" unless binarize_outcome=True.
    
    Returns
    -------
    pd.DataFrame or tuple
        If raw=True, returns DataFrame with columns:
        For outcome_type="survival": ['age', 'zscore', 'treatment', 'op_time', 'time', 'status']
        For outcome_type="binary": ['age', 'zscore', 'treatment', 'op_time', 'outcome'] 
        For outcome_type="continuous": ['age', 'zscore', 'treatment', 'op_time', 'outcome']
        If raw=False, returns (X, t, m, y) arrays.
    
    Notes
    -----
    This dataset extends the standard ToF survival data with a mediator variable
    that represents a continuous post-treatment measurement. The mediator is
    designed to demonstrate mediation analysis methods where treatment effects
    on survival outcomes can be decomposed into direct and indirect (mediated) 
    components.
    
    The dataset now includes uncensored event times which represent the true
    event times before administrative censoring. For outcome_type="binary",
    the binarization threshold is applied to these uncensored times rather 
    than the observed (potentially censored) times.
    
    The mediator values are simulated based on treatment assignment with:
    - Treatment-specific baseline levels (PrP: ~200, RVOTd: ~180, SPS: ~220)
    - Age-dependent effects (0.10 per unit age, scaled by 60 minutes)
    - Log-normal random variation to ensure positive values
    """
    return load_data_tof(
        raw=raw,
        treat_levels=treat_levels,
        binarize_outcome=binarize_outcome,
        binarization_threshold=binarization_threshold,
        include_mediator=True,
        outcome_type=outcome_type,
    )