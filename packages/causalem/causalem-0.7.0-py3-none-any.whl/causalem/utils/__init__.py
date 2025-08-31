"""
Utility helpers for post-processing CausalEM outputs.
"""

from __future__ import annotations

import pandas as pd


def as_pairwise(
    res: dict,
    *,
    treated_label: str = "treated",
    control_label: str = "control",
) -> pd.DataFrame:
    """
    Convert *any* result object returned by :pyfunc:`causalem.estimate_te`
    or :pyfunc:`causalem.estimate_te_multi` into a standard **pairwise**
    ``pandas.DataFrame``.

    Parameters
    ----------
    res : dict
        The dictionary returned by the estimation function.
    treated_label, control_label : str, default ``"treated"``, ``"control"``
        Labels to use when *res* comes from a **two-arm** design whose output
        is a scalar ``"te"``.  Ignored when *res* already contains a
        ``"pairwise"`` entry.

    Returns
    -------
    pandas.DataFrame
        A dataframe with columns ``["treatment_1", "treatment_2", "te",
        "lo", "hi"]`` (the last two only when available).  For convenience the
        original bootstrap draws (if any) are attached in
        ``df.attrs["boot"]``.
    """
    # ------------------------------------------------------------------
    # Case A – result already contains a pairwise DataFrame (multi-arm)
    # ------------------------------------------------------------------
    if "pairwise" in res and isinstance(res["pairwise"], pd.DataFrame):
        df = res["pairwise"].copy()  # shallow copy to avoid side-effects
        # rename legacy column
        if "est" in df.columns and "te" not in df.columns:
            df = df.rename(columns={"est": "te"})
        df.attrs["boot"] = res.get("boot", None)
        return df

    # Two-arm scalar → build a 1-row DataFrame.
    data: dict[str, list] = {
        "treatment_1": [treated_label],
        "treatment_2": [control_label],
        "te": [res["te"]],
    }
    if "ci" in res:
        lo, hi = res["ci"]
        data["lo"], data["hi"] = [lo], [hi]

    df = pd.DataFrame(data)
    df.attrs["boot"] = res.get("boot", None)
    return df
