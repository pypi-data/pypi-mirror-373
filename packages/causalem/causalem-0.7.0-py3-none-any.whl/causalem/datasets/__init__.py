import importlib.resources
import warnings

import numpy as np
import pandas as pd


def load_data_tof(
    *,
    raw: bool = True,
    treat_levels: list[str] = ["PrP", "RVOTd", "SPS"],
    binarize_outcome: bool = False,
    binarization_threshold: float | None = None,
    include_mediator: bool = False,
    outcome_type: str | None = None,
) -> pd.DataFrame | tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the simulated tetralogy of Fallot (TOF) dataset. By default
    returns a DataFrame with time-to-event information.
    If ``raw=False``, returns ``(X, t, y)`` or ``(X, t, m, y)`` when include_mediator=True where:
      • X : array (n × 2) of [age, zscore]
      • t : array (n,) treatment indicator (binary if 2 levels, categorical if 3 levels)
      • m : array (n,) mediator values (only when include_mediator=True)
      • y : array (n × 2) of [time, status] for "survival",
            array (n,) binary outcomes for "binary",
            array (n,) continuous times for "continuous"
    
    The outcome format is controlled by ``outcome_type`` or the deprecated ``binarize_outcome`` flag.
    When ``include_mediator=True``, the dataset includes a continuous post-treatment mediator variable
    that mediates the relationship between treatment and outcome.
    
    Parameters
    ----------
    raw : bool
        If True, return pd.DataFrame. If False, return (X,t,y) or (X,t,m,y) arrays.
    treat_levels : list[str]
        List of 2 or 3 treatment labels to include.
        Must be subset of the three levels in the data: ['PrP', 'RVOTd', 'SPS'].
        For 2 levels: t is binary indicator (0/1).
        For 3 levels: t is categorical indicator (0/1/2).
    binarize_outcome : bool, default False
        Convert the time-to-event outcome into a binary failure indicator.
        Deprecated: use outcome_type="binary" instead.
    binarization_threshold : float or None, default None
        Threshold used for binarization. If ``None`` uses the median time.
        When include_mediator=True and outcome_type="binary", applies to uncensored time.
        When include_mediator=False and outcome_type="binary", applies to observed time.
    include_mediator : bool, default False
        If True, load dataset with mediator variable and return (X,t,m,y) when raw=False.
    outcome_type : str or None, default None
        Output format: "survival" (default), "binary", or "continuous".
        - "survival": Return [time, status] for survival analysis
        - "binary": Return binary indicators based on time threshold
        - "continuous": Return times as continuous outcome (uncensored when include_mediator=True)
        If None, defaults to "survival" unless binarize_outcome=True.
    """
    # --- load CSV ---
    # Always use the mediator file since it contains all columns including mediator
    pkg = importlib.resources.files("causalem.datasets")
    path = pkg.joinpath("tof_survival_with_mediator.csv")
    df = pd.read_csv(path.open("r"))

    # When not including mediator, drop the extra columns to maintain backward compatibility
    if not include_mediator:
        df = df.drop(columns=["time_uncensored", "op_time"])

    # --- validate treat_levels ---
    levels = set(df["treatment"].unique())
    if (
        not isinstance(treat_levels, (list, tuple))
        or len(treat_levels) not in [2, 3]
        or any(lbl not in levels for lbl in treat_levels)
    ):
        raise ValueError(
            f"treat_levels must be 2 or 3 of {sorted(levels)}, got {treat_levels!r}"
        )

    # --- filter to selected treatment groups ---
    df = df[df["treatment"].isin(treat_levels)].copy()

    # --- determine outcome_type consistently ---
    if outcome_type is None:
        # Backward compatibility: use binarize_outcome flag
        outcome_type = "binary" if binarize_outcome else "survival"
    else:
        # Validate outcome_type
        valid_types = {"survival", "binary", "continuous"}
        if outcome_type not in valid_types:
            raise ValueError(f"outcome_type must be one of {valid_types}, got {outcome_type!r}")
        
        # If both outcome_type and binarize_outcome are specified, warn about conflict
        if binarize_outcome and outcome_type != "binary":
            warnings.warn(
                f"Both binarize_outcome=True and outcome_type='{outcome_type}' specified. "
                f"Using outcome_type='{outcome_type}'.",
                UserWarning,
            )

    # --- handle different outcome types ---
    if outcome_type == "binary":
        if include_mediator:
            # Use uncensored time for threshold when mediator is included
            time_col = "time_uncensored"
            threshold = (
                float(binarization_threshold)
                if binarization_threshold is not None
                else float(df[time_col].median())
            )
            # Apply threshold to uncensored time
            cens_mask = (df[time_col] <= threshold) & (df["status"] == 0)
            n_removed = int(cens_mask.sum())
            if n_removed:
                warnings.warn(
                    f"Removed {n_removed} observations censored before uncensored threshold {threshold}",
                    UserWarning,
                )
            df = df.loc[~cens_mask].copy()
            # Create binary outcome based on uncensored time
            df["outcome"] = np.where(df[time_col] > threshold, 0, 1)
            if raw:
                return df.drop(columns=["time", "status", "time_uncensored"])
        else:
            # Use observed time for threshold when mediator is not included
            time_col = "time"
            threshold = (
                float(binarization_threshold)
                if binarization_threshold is not None
                else float(df[time_col].median())
            )
            cens_mask = (df[time_col] <= threshold) & (df["status"] == 0)
            n_removed = int(cens_mask.sum())
            if n_removed:
                warnings.warn(
                    f"Removed {n_removed} observations censored before threshold {threshold}",
                    UserWarning,
                )
            df = df.loc[~cens_mask].copy()
            df["outcome"] = np.where(df[time_col] > threshold, 0, 1)
            if raw:
                return df.drop(columns=["time", "status"])
    
    elif outcome_type == "continuous":
        if include_mediator:
            # Return uncensored time as continuous outcome
            df["outcome"] = df["time_uncensored"]
            if raw:
                return df.drop(columns=["time", "status", "time_uncensored"])
        else:
            # Return observed time as continuous outcome
            df["outcome"] = df["time"]
            if raw:
                return df.drop(columns=["time", "status"])
    
    # outcome_type == "survival" (default behavior)
    if raw:
        if include_mediator:
            # For survival outcome: drop time_uncensored and move time, status to rightmost
            df = df.drop(columns=["time_uncensored"])
            # Reorder columns: move time and status to the end
            other_cols = [col for col in df.columns if col not in ["time", "status"]]
            df = df[other_cols + ["time", "status"]]
        return df

    # --- build arrays ---
    X = df[["age", "zscore"]].to_numpy(dtype=float)
    
    # --- encode treatment ---
    if len(treat_levels) == 2:
        # Binary treatment: 0 for treat_levels[0], 1 for treat_levels[1]
        t = (df["treatment"] == treat_levels[1]).astype(int).to_numpy()
    else:
        # Categorical treatment: 0, 1, 2 for treat_levels[0], treat_levels[1], treat_levels[2]
        treatment_map = {level: i for i, level in enumerate(treat_levels)}
        t = df["treatment"].map(treatment_map).to_numpy()
    
    # --- encode outcome based on outcome_type ---
    if outcome_type == "binary":
        y = df["outcome"].astype(int).to_numpy()
    elif outcome_type == "continuous": 
        y = df["outcome"].astype(float).to_numpy()
    else:  # outcome_type == "survival"
        y = df[["time", "status"]].to_numpy()

    # --- return arrays ---
    if include_mediator:
        m = df["op_time"].to_numpy(dtype=float)
        return X, t, m, y
    else:
        return X, t, y


def load_data_lalonde(
    *,
    raw: bool = True,
    binarize_outcome: bool = False,
    binarization_threshold: float | None = None,
) -> pd.DataFrame | tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the Lalonde job training data.
    By default returns a DataFrame.
    If ``raw=False``, returns ``(X, t, y)`` where:
      • X : array of confounders (all cols except treat, re78)
      • t : array of binary treatment indicator (from ``treat``)
      • y : array of outcomes (from ``re78``)
    When ``binarize_outcome=True`` the ``re78`` column is thresholded at
    ``binarization_threshold`` (or its median if ``None``) and converted to
    a 0/1 indicator.
    """
    pkg = importlib.resources.files("causalem.datasets")
    path = pkg.joinpath("lalonde.csv")
    df = pd.read_csv(path.open("r"))

    if binarize_outcome:
        threshold = (
            float(binarization_threshold)
            if binarization_threshold is not None
            else float(df["re78"].median())
        )
        df["re78"] = (df["re78"] > threshold).astype(int)
        if raw:
            return df

    if raw:
        return df

    # --- build arrays ---
    if "treat" not in df.columns or "re78" not in df.columns:
        raise ValueError("Expected columns 'treat' and 're78' in Lalonde data")

    t = df["treat"].astype(int).to_numpy()
    y = df["re78"].to_numpy()
    X = df.drop(columns=["treat", "re78"]).to_numpy()

    return X, t, y
