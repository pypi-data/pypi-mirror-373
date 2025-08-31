import numpy as np
from causalem.utils._weights import fit_with_appearance_weights, appearance_weights
from sklearn.linear_model import LinearRegression


class RecordingEstimator:
    def __init__(self):
        self.received_sw = None
        self.n_samples = None

    def fit(self, X, y, sample_weight=None):
        self.n_samples = X.shape[0]
        self.received_sw = sample_weight
        return self


class NoSampleWeightLinearRegression(LinearRegression):
    def fit(self, X, y):
        self.n_samples_fit_ = X.shape[0]
        return super().fit(X, y)


def test_uses_sample_weight_when_supported():
    est = RecordingEstimator()
    X = np.arange(6).reshape(-1, 1)
    y = np.arange(6)
    w = np.array([1, 2, 1, 1, 0, 1])
    fit_with_appearance_weights(est, X, y, sample_weight=w)
    assert est.received_sw is not None
    assert est.n_samples == 6
    assert np.array_equal(est.received_sw, w)


def test_replication_matches_sample_weight_and_drops_zero():
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 2.0, 2.0, 5.0])
    w = np.array([1, 2, 1, 0])

    lr = LinearRegression().fit(X, y, sample_weight=w)

    lr_nosw = NoSampleWeightLinearRegression()
    fit_with_appearance_weights(lr_nosw, X, y, sample_weight=w)

    assert lr_nosw.n_samples_fit_ == np.sum(w[w > 0])
    assert np.allclose(lr_nosw.coef_, lr.coef_)
    assert np.allclose(lr_nosw.intercept_, lr.intercept_)


def test_all_ones_equivalent_unweighted():
    X = np.array([[0.0], [1.0], [2.0]])
    y = np.array([0.0, 1.0, 2.0])
    w = np.ones(3, dtype=int)

    lr_nosw = NoSampleWeightLinearRegression()
    fit_with_appearance_weights(lr_nosw, X, y, sample_weight=w)

    lr_unweighted = NoSampleWeightLinearRegression().fit(X, y)

    assert lr_nosw.n_samples_fit_ == 3
    assert np.allclose(lr_nosw.coef_, lr_unweighted.coef_)
    assert np.allclose(lr_nosw.intercept_, lr_unweighted.intercept_)


def test_appearance_weights_counts_and_unmatched():
    cluster_mat = np.array([[0, 1], [-1, -1], [2, -1], [3, 3]])
    w = appearance_weights(cluster_mat)
    assert np.array_equal(w, np.array([2, 0, 1, 2]))


def test_appearance_weights_niter_one():
    cluster_mat = np.array([[0], [-1], [5]])
    w = appearance_weights(cluster_mat)
    assert np.array_equal(w, np.array([1, 0, 1]))
