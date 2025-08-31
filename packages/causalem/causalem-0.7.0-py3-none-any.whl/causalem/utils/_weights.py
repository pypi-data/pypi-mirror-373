import numpy as np
import inspect


def appearance_weights(cluster_mat: np.ndarray) -> np.ndarray:
    """Return per-row appearance counts from cluster id matrix ``(n, niter)``.

    Parameters
    ----------
    cluster_mat : np.ndarray
        Matrix of cluster identifiers where ``-1`` denotes an unmatched row.

    Returns
    -------
    np.ndarray
        Array of length ``n`` containing the number of iterations each
        observation appeared in.
    """
    return np.sum(cluster_mat != -1, axis=1)

def _has_fit_param(estimator, name: str = "sample_weight") -> bool:
    try:
        return name in inspect.signature(estimator.fit).parameters
    except (TypeError, ValueError):
        return False

def _repeat_by_weights(X, y, w):
    w = np.asarray(w)
    if not np.issubdtype(w.dtype, np.integer):
        w = np.rint(w).astype(int)
    keep = w > 0
    if not np.all(keep):
        if hasattr(X, "iloc"):
            X = X.iloc[keep]
        else:
            X = X[keep]
        if y is not None:
            y = y.iloc[keep] if hasattr(y, "iloc") else y[keep]
        w = w[keep]
    idx = np.repeat(np.arange(len(w)), w)
    if hasattr(X, "iloc"):
        X_rep = X.iloc[idx]
    else:
        X_rep = X[idx]
    if y is None:
        y_rep = None
    elif hasattr(y, "iloc"):
        y_rep = y.iloc[idx]
    else:
        y_rep = y[idx]
    return X_rep, y_rep

def fit_with_appearance_weights(estimator, X, y, sample_weight=None, **kwargs):
    """Fit estimator using sample_weight if supported; else replicate rows.

    Parameters
    ----------
    estimator : object
        Estimator implementing ``fit``.
    X, y : array-like
        Training data.
    sample_weight : array-like, optional
        Appearance counts (non-negative integers).
    kwargs : dict
        Passed through to ``estimator.fit``.
    """
    if sample_weight is None:
        return estimator.fit(X, y, **kwargs)
    if _has_fit_param(estimator, "sample_weight"):
        return estimator.fit(X, y, sample_weight=np.asarray(sample_weight), **kwargs)
    X_rep, y_rep = _repeat_by_weights(X, y, sample_weight)
    return estimator.fit(X_rep, y_rep, **kwargs)
