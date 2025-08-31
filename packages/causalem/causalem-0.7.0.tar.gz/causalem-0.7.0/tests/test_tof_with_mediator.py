import numpy as np
import pytest

from causalem import load_data_tof
from causalem.datasets.tof_with_mediator import load_data_tof_with_mediator


def test_load_tof_with_mediator():
    df = load_data_tof_with_mediator()
    assert (
        df.shape[1] == 6
    )  # age, zscore, treatment, op_time, time, status (no time_uncensored)
    assert df.shape[0] == 1662  # Number of rows (same as original ToF)
    assert {"treatment", "status", "age", "zscore", "time", "op_time"} <= set(
        df.columns
    )  # Check column names (no time_uncensored)
    # Mediator should be continuous and positive
    assert df["op_time"].dtype in ["float64", "float32"]
    assert df["op_time"].min() > 0
    assert df["op_time"].max() > df["op_time"].min()
    # time_uncensored should NOT exist for survival (default) outcome
    assert "time_uncensored" not in df.columns
    # Check column order
    expected_cols = ["age", "zscore", "treatment", "op_time", "time", "status"]
    assert list(df.columns) == expected_cols


def test_load_tof_with_mediator_processed_default():
    X, t, m, y = load_data_tof_with_mediator(raw=False)
    # ensure alignment
    assert X.shape[0] == t.shape[0] == m.shape[0] == y.shape[0]
    # confounders only: age, zscore
    assert X.shape[1] == 2
    # t is categorical with all 3 levels by default
    assert set(np.unique(t)) <= {0, 1, 2}
    # m is mediator (1-D continuous)
    assert m.ndim == 1 and m.dtype in ["float64", "float32"]
    assert m.min() > 0  # mediator should be positive
    # y is 2-D [time,status] for default survival
    assert y.ndim == 2 and y.shape[1] == 2


def test_load_tof_with_mediator_processed_binary():
    # Test backward compatibility with 2 levels
    X, t, m, y = load_data_tof_with_mediator(raw=False, treat_levels=["PrP", "SPS"])
    # ensure alignment
    assert X.shape[0] == t.shape[0] == m.shape[0] == y.shape[0]
    # confounders only: age, zscore
    assert X.shape[1] == 2
    # t is binary for 2 levels
    assert set(np.unique(t)) <= {0, 1}
    # m is mediator (1-D continuous)
    assert m.ndim == 1
    # y is 2-D [time,status] for default survival
    assert y.ndim == 2 and y.shape[1] == 2


def test_load_tof_with_mediator_custom_levels_and_errors():
    # valid custom levels (2 levels)
    X, t, m, y = load_data_tof_with_mediator(raw=False, treat_levels=["RVOTd", "PrP"])
    assert set(np.unique(t)) <= {0, 1}
    assert m.ndim == 1  # mediator should be present
    # valid custom levels (3 levels)
    X, t, m, y = load_data_tof_with_mediator(
        raw=False, treat_levels=["PrP", "RVOTd", "SPS"]
    )
    assert set(np.unique(t)) <= {0, 1, 2}
    assert m.ndim == 1  # mediator should be present
    # invalid levels should raise
    with pytest.raises(ValueError):
        load_data_tof_with_mediator(raw=False, treat_levels=["A", "B"])
    with pytest.raises(ValueError):
        load_data_tof_with_mediator(raw=False, treat_levels=["PrP"])
    with pytest.raises(ValueError):
        load_data_tof_with_mediator(
            raw=False, treat_levels=["PrP", "SPS", "RVOTd", "Extra"]
        )


def test_outcome_type_survival():
    """Test outcome_type='survival' (default)"""
    df = load_data_tof_with_mediator(outcome_type="survival")
    assert "time" in df.columns
    assert "status" in df.columns
    assert "time_uncensored" not in df.columns  # Should be dropped for survival
    # Check column order: time and status should be rightmost
    expected_cols = ["age", "zscore", "treatment", "op_time", "time", "status"]
    assert list(df.columns) == expected_cols

    X, t, m, y = load_data_tof_with_mediator(raw=False, outcome_type="survival")
    assert y.ndim == 2 and y.shape[1] == 2
    assert y.shape[0] == X.shape[0]


def test_outcome_type_binary():
    """Test outcome_type='binary'"""
    df = load_data_tof_with_mediator(outcome_type="binary")
    assert "outcome" in df.columns
    assert "time" not in df.columns
    assert "status" not in df.columns
    assert "time_uncensored" not in df.columns
    assert set(df["outcome"].unique()) <= {0, 1}

    X, t, m, y = load_data_tof_with_mediator(raw=False, outcome_type="binary")
    assert y.ndim == 1
    assert set(np.unique(y)) <= {0, 1}
    assert y.shape[0] == X.shape[0]


def test_outcome_type_continuous():
    """Test outcome_type='continuous'"""
    df = load_data_tof_with_mediator(outcome_type="continuous")
    assert "outcome" in df.columns
    assert "time" not in df.columns
    assert "status" not in df.columns
    assert "time_uncensored" not in df.columns
    # outcome should be continuous (uncensored times)
    assert len(df["outcome"].unique()) > 2  # more than just 0/1

    X, t, m, y = load_data_tof_with_mediator(raw=False, outcome_type="continuous")
    assert y.ndim == 1
    assert y.dtype in [np.float64, np.float32]
    assert y.shape[0] == X.shape[0]
    assert y.min() >= 1  # minimum time
    assert y.max() > y.min()


def test_outcome_type_invalid():
    """Test invalid outcome_type raises error"""
    with pytest.raises(ValueError, match="outcome_type must be one of"):
        load_data_tof_with_mediator(outcome_type="invalid")


def test_binary_uses_uncensored_time():
    """Test that binary outcome uses uncensored time for thresholding"""
    # Load raw data from CSV to get access to time_uncensored
    import importlib.resources

    import pandas as pd

    pkg = importlib.resources.files("causalem.datasets")
    path = pkg.joinpath("tof_survival_with_mediator.csv")
    df_raw = pd.read_csv(path.open("r"))

    # Use a threshold where we know the difference matters
    threshold = df_raw["time"].quantile(0.7)  # Use censored time quantile

    # Compare old approach (would have used censored time) vs new (uses uncensored time)
    # We can't directly test the old approach, but we can verify the new logic
    df_binary = load_data_tof_with_mediator(
        outcome_type="binary", binarization_threshold=threshold
    )

    # Get the same threshold applied to the filtered data
    filtered_raw = df_raw[df_raw["treatment"].isin(["PrP", "RVOTd", "SPS"])].copy()

    # Check that the filtering is based on uncensored time
    expected_kept = filtered_raw[
        ~(
            (filtered_raw["time_uncensored"] <= threshold)
            & (filtered_raw["status"] == 0)
        )
    ]

    assert len(df_binary) == len(expected_kept)


def test_binarize_tof_with_mediator():
    """Test backward compatibility with binarize_outcome=True"""
    # Load raw data from CSV to get access to time_uncensored for median calculation
    import importlib.resources

    import pandas as pd

    pkg = importlib.resources.files("causalem.datasets")
    path = pkg.joinpath("tof_survival_with_mediator.csv")
    df_raw = pd.read_csv(path.open("r"))

    med = df_raw["time_uncensored"].median()  # Note: now uses uncensored time median

    with pytest.warns(UserWarning):
        df = load_data_tof_with_mediator(
            binarize_outcome=True, binarization_threshold=med
        )
    assert set(df["outcome"].unique()) <= {0, 1}
    assert "op_time" in df.columns  # mediator should be preserved

    # Check that observations are filtered based on uncensored time
    kept = df_raw.loc[
        (df_raw["time_uncensored"] > med)
        | ((df_raw["time_uncensored"] <= med) & (df_raw["status"] == 1))
    ]
    assert len(df) == len(kept)

    X, t, m, y = load_data_tof_with_mediator(
        raw=False,
        binarize_outcome=True,
        binarization_threshold=med,
    )
    assert set(np.unique(y)) <= {0, 1}
    assert m.ndim == 1  # mediator should be present
    assert len(y) == len(kept)


def test_binarize_outcome_vs_outcome_type_binary():
    """Test that binarize_outcome=True and outcome_type='binary' give same results"""
    threshold = 1500

    df_old = load_data_tof_with_mediator(
        binarize_outcome=True, binarization_threshold=threshold
    )
    df_new = load_data_tof_with_mediator(
        outcome_type="binary", binarization_threshold=threshold
    )

    assert len(df_old) == len(df_new)
    assert (df_old["outcome"].values == df_new["outcome"].values).all()

    # Test arrays too
    X_old, t_old, m_old, y_old = load_data_tof_with_mediator(
        raw=False, binarize_outcome=True, binarization_threshold=threshold
    )
    X_new, t_new, m_new, y_new = load_data_tof_with_mediator(
        raw=False, outcome_type="binary", binarization_threshold=threshold
    )

    assert np.array_equal(y_old, y_new)
    assert np.array_equal(X_old, X_new)


def test_continuous_returns_uncensored_times():
    """Test that continuous outcome returns uncensored times"""
    # Load raw data from CSV to get access to time_uncensored
    import importlib.resources

    import pandas as pd

    pkg = importlib.resources.files("causalem.datasets")
    path = pkg.joinpath("tof_survival_with_mediator.csv")
    df_raw = pd.read_csv(path.open("r"))

    df_cont = load_data_tof_with_mediator(outcome_type="continuous")

    # The continuous outcome should match the uncensored times from raw dataset
    # (accounting for the fact that treatment filtering might be applied)
    filtered_raw = df_raw[df_raw["treatment"].isin(["PrP", "RVOTd", "SPS"])]
    assert (df_cont["outcome"].values == filtered_raw["time_uncensored"].values).all()


@pytest.mark.skip(
    reason="Temporarily disabled - we may bring this back when merging the mediation-analysis branch with main"
)
def test_tof_with_mediator_vs_original_consistency():
    """Test that the mediator version has consistent base data with original."""
    df_original = load_data_tof()
    df_mediator = load_data_tof_with_mediator()

    # Same number of rows
    assert len(df_original) == len(df_mediator)

    # Same values for numeric columns
    numeric_cols = ["time", "status", "age", "zscore"]
    for col in numeric_cols:
        assert np.allclose(df_original[col], df_mediator[col], equal_nan=True)

    # Same values for categorical columns
    categorical_cols = ["treatment"]
    for col in categorical_cols:
        assert (df_original[col] == df_mediator[col]).all()
