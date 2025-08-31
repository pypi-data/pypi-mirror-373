import numpy as np
import pytest

from causalem import load_data_lalonde, load_data_tof


def test_load_tof():
    df = load_data_tof()
    assert df.shape[1] == 5  # time, status, age, zscore, treatment
    assert df.shape[0] == 1662  # Number of rows
    assert {"treatment", "status", "age", "zscore", "time"} <= set(
        df.columns
    )  # Check column names


def test_load_lalonde():
    df = load_data_lalonde()
    assert (
        df.shape[1] == 12
    )  # age, educ, black, hisp, married, nodegr, re74, re75, treat, re78, u74, u75
    assert df.shape[0] == 445  # Number of rows
    assert {
        "age",
        "educ",
        "black",
        "hisp",
        "married",
        "nodegr",
        "re74",
        "re75",
        "treat",
        "re78",
        "u74",
        "u75",
    } <= set(
        df.columns
    )  # Check column names
    assert df["treat"].nunique() == 2  # Check treatment variable has two unique values


def test_load_lalonde_processed():
    X, t, y = load_data_lalonde(raw=False)
    # shapes
    assert X.shape[0] == 445 and t.shape[0] == 445 and y.shape[0] == 445
    # X dims = all confounders except treat & re78 → 10 cols
    assert X.shape[1] == 10
    # treatment indicator
    assert set(np.unique(t)) <= {0, 1}
    # outcome is 1-D numeric
    assert y.ndim == 1


def test_load_tof_processed_default():
    X, t, y = load_data_tof(raw=False)
    # ensure alignment
    assert X.shape[0] == t.shape[0] == y.shape[0]
    # confounders only: age, zscore
    assert X.shape[1] == 2
    # t is now categorical with all 3 levels by default
    assert set(np.unique(t)) <= {0, 1, 2}
    # y is 2-D [time,status]
    assert y.ndim == 2 and y.shape[1] == 2


def test_load_tof_processed_binary():
    # Test backward compatibility with 2 levels
    X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])
    # ensure alignment
    assert X.shape[0] == t.shape[0] == y.shape[0]
    # confounders only: age, zscore
    assert X.shape[1] == 2
    # t is binary for 2 levels
    assert set(np.unique(t)) <= {0, 1}
    # y is 2-D [time,status]
    assert y.ndim == 2 and y.shape[1] == 2


def test_load_tof_custom_levels_and_errors():
    # valid custom levels (2 levels)
    X, t, y = load_data_tof(raw=False, treat_levels=["RVOTd", "PrP"])
    assert set(np.unique(t)) <= {0, 1}
    # valid custom levels (3 levels)
    X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "RVOTd", "SPS"])
    assert set(np.unique(t)) <= {0, 1, 2}
    # invalid levels should raise
    with pytest.raises(ValueError):
        load_data_tof(raw=False, treat_levels=["A", "B"])
    with pytest.raises(ValueError):
        load_data_tof(raw=False, treat_levels=["PrP"])
    with pytest.raises(ValueError):
        load_data_tof(raw=False, treat_levels=["PrP", "SPS", "RVOTd", "Extra"])


def test_binarize_lalonde():
    df_raw = load_data_lalonde()
    med = df_raw["re78"].median()
    df = load_data_lalonde(binarize_outcome=True)
    assert set(df["re78"].unique()) <= {0, 1}
    expected = (df_raw["re78"] > med).astype(int).to_numpy()
    assert (df["re78"].to_numpy() == expected).all()

    X, t, y = load_data_lalonde(
        raw=False, binarize_outcome=True, binarization_threshold=med
    )
    assert set(np.unique(y)) <= {0, 1}
    assert (y == expected).all()


def test_binarize_tof():
    df_raw = load_data_tof()
    med = df_raw["time"].median()
    with pytest.warns(UserWarning):
        df = load_data_tof(binarize_outcome=True, binarization_threshold=med)
    assert set(df["outcome"].unique()) <= {0, 1}
    kept = df_raw.loc[
        (df_raw["time"] > med) | ((df_raw["time"] <= med) & (df_raw["status"] == 1))
    ]
    assert len(df) == len(kept)

    X, t, y = load_data_tof(
        raw=False,
        binarize_outcome=True,
        binarization_threshold=med,
    )
    assert set(np.unique(y)) <= {0, 1}
    # Now by default all 3 treatment levels are included, not just PrP and SPS
    assert len(y) == len(kept)
