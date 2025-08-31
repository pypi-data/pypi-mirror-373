import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from causalem.utils import as_pairwise


# ---------------------------------------------------------------------
# 1. Two-arm result – no CI / no boot
# ---------------------------------------------------------------------
def test_as_pairwise_two_arm_basic():
    res = {"te": 0.42}
    df = as_pairwise(res)

    # expected 1-row dataframe
    exp = pd.DataFrame(
        {"treatment_1": ["treated"], "treatment_2": ["control"], "te": [0.42]}
    )
    assert_frame_equal(df.reset_index(drop=True), exp)
    # no CI columns and no boot attr
    assert set(df.columns) == {"treatment_1", "treatment_2", "te"}
    assert df.attrs["boot"] is None


# ---------------------------------------------------------------------
# 2. Two-arm with CI & boot
# ---------------------------------------------------------------------
def test_as_pairwise_two_arm_ci_boot():
    boot_draws = np.array([0.3, 0.4, 0.5])
    res = {"te": 0.4, "ci": (0.1, 0.7), "boot": boot_draws}
    df = as_pairwise(res, treated_label="T", control_label="C")

    exp = pd.DataFrame(
        {
            "treatment_1": ["T"],
            "treatment_2": ["C"],
            "te": [0.4],
            "lo": [0.1],
            "hi": [0.7],
        }
    )
    assert_frame_equal(df.reset_index(drop=True), exp)
    # bootstrap draws attached
    assert np.array_equal(df.attrs["boot"], boot_draws)


# ---------------------------------------------------------------------
# 3. Multi-arm passthrough
# ---------------------------------------------------------------------
def test_as_pairwise_multi_arm_passthrough():
    pair_df = pd.DataFrame(
        {
            "treatment_1": ["A", "B"],
            "treatment_2": ["B", "C"],
            "te": [1.2, 0.8],
        }
    )
    boot = {("A", "B"): np.array([1.0, 1.3]), ("B", "C"): np.array([0.7, 0.9])}
    res = {"pairwise": pair_df.copy(), "boot": boot}

    df = as_pairwise(res)
    assert_frame_equal(df.reset_index(drop=True), pair_df.reset_index(drop=True))
    assert df.attrs["boot"] == boot
