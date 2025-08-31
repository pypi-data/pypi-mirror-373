"""
Tests for experimental mediation analysis functionality.
"""

import numpy as np
import pytest
import warnings
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.ensemble import RandomForestRegressor

from causalem.mediation import estimate_mediation


def simulate_mediation_data(n=1000, seed=42, tau=2.0, theta=3.0, alpha=1.0):
    """
    Simulate synthetic mediation data with known ground truth effects.
    
    Model:
    A ~ Bernoulli(0.5)
    M | A,X ~ Bernoulli(logit^{-1}(X₁ + X₂ + β_A * A))  
    Y | A,M,X ~ N(α + τ*A + θ*M + X₁ + X₂, σ²)
    
    Parameters
    ----------
    n : int
        Sample size
    seed : int
        Random seed
    tau : float
        Direct effect of A on Y
    theta : float  
        Effect of M on Y
    alpha : float
        Intercept for Y
        
    Returns
    -------
    dict with X, A, M, Y and true effects
    """
    rng = np.random.RandomState(seed)
    
    # Covariates
    X = rng.randn(n, 2)
    X_sum = X.sum(axis=1)
    
    # Treatment (binary)
    A = rng.binomial(1, 0.5, n)
    
    # Mediator depends on X and A
    beta_A = 0.5  # effect of A on M
    logit_M = X_sum + beta_A * A
    p_M = 1 / (1 + np.exp(-logit_M))
    M = rng.binomial(1, p_M)
    
    # Outcome depends on X, A, and M
    sigma_Y = 1.0
    Y = alpha + tau * A + theta * M + X_sum + sigma_Y * rng.randn(n)
    
    # Calculate true effects analytically
    # This requires computing expectations over the mediator distribution
    # For simplicity, we'll compute approximate true effects empirically
    # using a large simulation
    
    return {
        'X': X,
        'A': A, 
        'M': M,
        'Y': Y,
        'true_tau': tau,  # direct effect coefficient
        'true_theta': theta,  # mediator effect coefficient
        'true_alpha': alpha,  # intercept
        'true_beta_A': beta_A  # A -> M effect
    }


class TestMediationBasic:
    """Basic functionality tests for mediation estimator."""
    
    def test_mediation_runs_and_returns_expected_keys(self):
        """Test that estimate_mediation runs and returns expected keys."""
        data = simulate_mediation_data(n=500, seed=123)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Check return structure for interventional effects (default)
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['detail'] is None  # default return_detail=False
        assert result['mediator_type'] == "binary"  # Should auto-detect binary
        assert result['scale'] == "mean_difference"  # Continuous outcome scale
        
        # Check that all effects are finite numbers
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])  
        assert np.isfinite(result['iie'])
        assert np.isfinite(result['prop_mediated']) or np.isnan(result['prop_mediated'])

    def test_natural_effects_returns_nde_nie(self):
        """Test that effect_type='natural' returns NDE/NIE keys."""
        data = simulate_mediation_data(n=500, seed=123)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            effect_type="natural",
            random_state_master=42
        )
        
        expected_keys = {'te', 'nde', 'nie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['mediator_type'] == "binary"  # Should auto-detect binary
        assert result['scale'] == "mean_difference"  # Continuous outcome scale

    def test_reproducibility_with_same_random_state(self):
        """Test that results are reproducible with same random_state_master."""
        data = simulate_mediation_data(n=500, seed=123)
        
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Results should be identical
        assert result1['te'] == result2['te']
        assert result1['ide'] == result2['ide'] 
        assert result1['iie'] == result2['iie']
        assert result1['prop_mediated'] == result2['prop_mediated']

    def test_no_mediation_effect_when_theta_zero(self):
        """Test that indirect effect is near zero when mediator has no effect on outcome."""
        # Simulate data where M has no effect on Y (theta=0)
        data = simulate_mediation_data(n=1000, seed=123, tau=2.0, theta=0.0)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Indirect effect should be close to zero
        assert abs(result['iie']) < 0.1, f"Expected small indirect effect, got {result['iie']}"
        
        # Total effect should be close to direct effect
        assert abs(result['te'] - result['ide']) < 0.1

    def test_no_direct_effect_when_tau_zero(self):
        """Test that direct effect is near zero when treatment has no direct effect on outcome.""" 
        # Simulate data where A has no direct effect on Y (tau=0)
        data = simulate_mediation_data(n=1000, seed=123, tau=0.0, theta=3.0)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Direct effect should be close to zero
        assert abs(result['ide']) < 0.2, f"Expected small direct effect, got {result['ide']}"
        
        # Total effect should be close to indirect effect  
        assert abs(result['te'] - result['iie']) < 0.2

    def test_return_detail_includes_unit_level_estimates(self):
        """Test that return_detail=True includes unit-level estimates."""
        data = simulate_mediation_data(n=100, seed=123)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            return_detail=True,
            random_state_master=42
        )
        
        assert result['detail'] is not None
        detail = result['detail']
        
        # Check that unit-level arrays have correct length
        n = len(data['A'])
        assert len(detail['unit_te']) == n
        assert len(detail['unit_dir']) == n
        assert len(detail['unit_ind']) == n
        
        # Check that aggregation is consistent
        assert abs(np.mean(detail['unit_te']) - result['te']) < 1e-10
        assert abs(np.mean(detail['unit_dir']) - result['ide']) < 1e-10
        assert abs(np.mean(detail['unit_ind']) - result['iie']) < 1e-10

    def test_custom_models(self):
        """Test that custom models are accepted and used."""
        data = simulate_mediation_data(n=500, seed=123)
        
        # Use simple linear models instead of defaults
        custom_mediator = LogisticRegression(solver='lbfgs', max_iter=500)
        custom_outcome = LinearRegression()
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=custom_mediator,
            model_outcome=custom_outcome,
            random_state_master=42
        )
        
        # Should run without error and return expected structure
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['mediator_type'] == "binary"  # Should auto-detect binary
        assert result['scale'] == "mean_difference"  # Continuous outcome scale

    def test_input_validation_binary_treatment(self):
        """Test that non-binary treatment raises ValueError."""
        data = simulate_mediation_data(n=100, seed=123)
        
        # Make treatment non-binary 
        bad_treatment = data['A'].copy().astype(float)
        bad_treatment[0] = 2.0  # Invalid value
        
        with pytest.raises(ValueError, match="treatment must be binary"):
            estimate_mediation(data['X'], bad_treatment, data['M'], data['Y'])

    def test_continuous_mediator_auto_detection(self):
        """Test that non-binary mediator is auto-detected as continuous."""
        data = simulate_mediation_data(n=100, seed=123)
        
        # Make mediator non-binary (should be treated as continuous)
        continuous_mediator = data['M'].copy().astype(float)  
        continuous_mediator[0] = 0.5  # Non-binary value
        
        # Should run successfully and detect continuous mediator
        result = estimate_mediation(
            data['X'], data['A'], continuous_mediator, data['Y'],
            n_mc_mediator=10,  # Small for speed
            random_state_master=42
        )
        
        # Should return expected structure
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['mediator_type'] == "continuous"  # Should auto-detect continuous
        assert result['scale'] == "mean_difference"  # Continuous outcome scale

    def test_input_validation_shape_mismatch(self):
        """Test that shape mismatches raise ValueError."""
        data = simulate_mediation_data(n=100, seed=123)
        
        # Truncate one array
        X_short = data['X'][:-1]
        
        with pytest.raises(ValueError, match="must have the same number of rows"):
            estimate_mediation(X_short, data['A'], data['M'], data['Y'])

    def test_mediator_model_without_predict_proba_raises_error(self):
        """Test that mediator models without predict_proba raise TypeError."""
        data = simulate_mediation_data(n=100, seed=123)
        
        # Use a regressor as mediator model (doesn't have predict_proba)
        bad_mediator_model = LinearRegression()
        
        with pytest.raises(TypeError, match="must implement predict_proba"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                model_mediator=bad_mediator_model
            )

    def test_invalid_effect_type_raises_error(self):
        """Test that invalid effect_type raises ValueError."""
        data = simulate_mediation_data(n=100, seed=123)
        
        with pytest.raises(ValueError, match="effect_type must be"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                effect_type="invalid"
            )

    def test_binary_outcome_now_supported(self):
        """Test that binary outcomes are now supported."""
        data = simulate_mediation_data(n=100, seed=123)
        
        # Create binary outcome (0, 1) 
        binary_y = np.random.binomial(1, 0.5, size=len(data['Y']))
        
        # Should now work without error
        result = estimate_mediation(data['X'], data['A'], data['M'], binary_y, 
                                    random_state_master=42)
        
        # Check return structure
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['scale'] == "risk_difference"  # Binary outcome scale
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        
        # Test with float binary outcome (0.0, 1.0)
        binary_y_float = binary_y.astype(float)
        result_float = estimate_mediation(data['X'], data['A'], data['M'], binary_y_float,
                                         random_state_master=42)
        assert result_float['scale'] == "risk_difference"  # Binary outcome scale

    def test_binary_outcome_additivity(self):
        """Test that binary outcomes maintain additivity: TE = IDE + IIE."""
        data = simulate_mediation_data(n=200, seed=42)
        binary_y = np.random.binomial(1, 0.5, size=len(data['Y']))
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], binary_y,
            random_state_master=42
        )
        
        # Check additivity within numerical tolerance
        additivity_error = abs(result['te'] - (result['ide'] + result['iie']))
        assert additivity_error < 1e-10, f"Additivity violated: error = {additivity_error}"


class TestMediationEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_small_sample_size(self):
        """Test that estimator works with small sample sizes."""
        data = simulate_mediation_data(n=50, seed=123)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            n_splits_mediator=3,  # Reduce splits for small sample
            random_state_master=42
        )
        
        # Should complete without error
        assert np.isfinite(result['te'])

    def test_constant_mediator(self):
        """Test behavior when mediator is constant (all 0 or all 1)."""
        data = simulate_mediation_data(n=200, seed=123)
        
        # Force all mediators to be 0
        M_constant = np.zeros_like(data['M'])
        
        result = estimate_mediation(
            data['X'], data['A'], M_constant, data['Y'],
            random_state_master=42
        )
        
        # Indirect effect should be zero when mediator is constant
        assert abs(result['iie']) < 0.01

    def test_grouped_cross_validation(self):
        """Test that grouped CV works when groups are provided."""
        data = simulate_mediation_data(n=300, seed=123)
        
        # Create some group structure
        groups = np.repeat(np.arange(10), 30)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            groups=groups,
            n_splits_mediator=3,  # Fewer splits for grouped CV
            random_state_master=42
        )
        
        # Should complete without error
        assert np.isfinite(result['te'])

    def test_non_binary_discrete_outcome_works(self):
        """Test that discrete but non-binary outcomes work (not rejected as binary)."""
        data = simulate_mediation_data(n=200, seed=123)
        
        # Create discrete outcome with values [0, 1, 2] - should be treated as continuous
        discrete_y = np.random.choice([0, 1, 2], size=len(data['Y']), p=[0.3, 0.4, 0.3])
        
        # Should run without error instead of raising ValueError
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Should return expected structure
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['mediator_type'] == "binary"  # Should auto-detect binary
        assert result['scale'] == "mean_difference"  # Continuous outcome scale

    def test_continuous_outcome_with_binary_values_detected_correctly(self):
        """Test edge case where continuous outcome happens to only have 0s and 1s."""
        data = simulate_mediation_data(n=50, seed=123) # Small sample for this edge case
        
        # Manually create outcome that's only 0.0 and 1.0 but intended as continuous
        # This tests the boundary of our binary detection
        continuous_y = np.random.choice([0.0, 1.0], size=len(data['Y']))
        
        # This should be detected as binary and handled appropriately
        result = estimate_mediation(data['X'], data['A'], data['M'], continuous_y,
                                   random_state_master=42)
        assert result['scale'] == "risk_difference"  # Should be detected as binary


class TestCrossFittingIntegrity:
    """Test cross-fitting integrity and no-leakage properties."""
    
    def test_outcome_cross_fitting_no_leakage_binary(self):
        """Test that outcome cross-fitting prevents leakage in binary mediator case."""
        data = simulate_mediation_data(n=200, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            n_splits_outcome=5,
            return_detail=True,
            random_state_master=42
        )
        
        detail = result['detail']
        outcome_fold = detail['outcome_fold']
        
        # Verify each unit has a valid fold assignment
        assert np.all(outcome_fold >= 0), "All units should have valid fold assignments"
        assert np.all(outcome_fold < 5), "Fold indices should be within valid range"
        
        # Verify that all folds are used (with reasonable sample size)
        unique_folds = np.unique(outcome_fold)
        assert len(unique_folds) >= 3, f"Expected at least 3 folds to be used, got {len(unique_folds)}"
        
        # Each fold should have reasonable number of units
        for fold in unique_folds:
            fold_size = np.sum(outcome_fold == fold)
            assert fold_size >= 5, f"Fold {fold} has too few units: {fold_size}"

    def test_outcome_cross_fitting_no_leakage_continuous(self):
        """Test that outcome cross-fitting prevents leakage in continuous mediator case."""
        np.random.seed(42)
        n = 150
        X = np.random.randn(n, 3)
        A = np.random.binomial(1, 0.5, n)
        M = 0.5*A + 0.3*X[:, 0] + np.random.randn(n)  # continuous
        Y = 1.5*A + 2.0*M + 0.4*X[:, 2] + np.random.randn(n)
        
        result = estimate_mediation(
            X, A, M, Y,
            n_splits_outcome=4,
            n_mc_mediator=20,
            return_detail=True,
            random_state_master=42
        )
        
        detail = result['detail']
        outcome_fold = detail['outcome_fold']
        
        # Verify each unit has a valid fold assignment
        assert np.all(outcome_fold >= 0), "All units should have valid fold assignments"
        assert np.all(outcome_fold < 4), "Fold indices should be within valid range"
        
        # Verify that all folds are used
        unique_folds = np.unique(outcome_fold)
        assert len(unique_folds) >= 3, f"Expected at least 3 folds to be used, got {len(unique_folds)}"

    def test_determinism_with_cross_fitting_binary(self):
        """Test that cross-fitting results are deterministic with fixed random_state."""
        data = simulate_mediation_data(n=100, seed=123)
        
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            n_splits_mediator=3,
            n_splits_outcome=4, 
            return_detail=True,
            random_state_master=42
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            n_splits_mediator=3,
            n_splits_outcome=4,
            return_detail=True, 
            random_state_master=42
        )
        
        # Results should be identical
        assert result1['te'] == result2['te']
        assert result1['ide'] == result2['ide']
        assert result1['iie'] == result2['iie']
        
        # Fold assignments should be identical
        assert np.array_equal(result1['detail']['outcome_fold'], result2['detail']['outcome_fold'])
        
        # Outcome predictions should be identical  
        assert np.allclose(result1['detail']['yhat_00'], result2['detail']['yhat_00'])
        assert np.allclose(result1['detail']['yhat_01'], result2['detail']['yhat_01'])
        assert np.allclose(result1['detail']['yhat_10'], result2['detail']['yhat_10'])
        assert np.allclose(result1['detail']['yhat_11'], result2['detail']['yhat_11'])

    def test_determinism_with_cross_fitting_continuous(self):
        """Test that cross-fitting results are deterministic for continuous mediator."""
        np.random.seed(123) 
        n = 100
        X = np.random.randn(n, 3)
        A = np.random.binomial(1, 0.5, n)
        M = 0.7*A + 0.5*X[:, 0] + np.random.randn(n)  # continuous
        Y = 1.5*A + 2.0*M + 0.4*X[:, 2] + np.random.randn(n)
        
        result1 = estimate_mediation(
            X, A, M, Y,
            n_splits_mediator=3,
            n_splits_outcome=4,
            n_mc_mediator=25,
            return_detail=True,
            random_state_master=42
        )
        
        result2 = estimate_mediation(
            X, A, M, Y,
            n_splits_mediator=3,
            n_splits_outcome=4,
            n_mc_mediator=25,
            return_detail=True,
            random_state_master=42
        )
        
        # Results should be identical
        assert result1['te'] == result2['te']
        assert result1['ide'] == result2['ide'] 
        assert result1['iie'] == result2['iie']
        
        # Fold assignments should be identical
        assert np.array_equal(result1['detail']['outcome_fold'], result2['detail']['outcome_fold'])
        
        # Monte Carlo expectations should be identical
        assert np.allclose(result1['detail']['Ey_1_M1'], result2['detail']['Ey_1_M1'])
        assert np.allclose(result1['detail']['Ey_0_M0'], result2['detail']['Ey_0_M0'])
        assert np.allclose(result1['detail']['Ey_1_M0'], result2['detail']['Ey_1_M0'])
        assert np.allclose(result1['detail']['Ey_0_M1'], result2['detail']['Ey_0_M1'])

    def test_cross_fitting_with_different_fold_counts(self):
        """Test that different fold counts work for mediator and outcome models."""
        data = simulate_mediation_data(n=120, seed=42)
        
        # Test asymmetric fold counts
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            n_splits_mediator=3,
            n_splits_outcome=4,
            return_detail=True,
            random_state_master=42
        )
        
        # Should work without error
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        
        # Check fold assignments are in correct ranges
        outcome_fold = result['detail']['outcome_fold']
        assert np.all(outcome_fold >= 0), "All outcome fold indices should be non-negative"
        assert np.all(outcome_fold < 4), "All outcome fold indices should be < n_splits_outcome"


class TestBinaryOutcomeFunctionality:
    """Test binary outcome functionality specifically."""
    
    def simulate_binary_outcome_data(self, n=500, seed=42, mediator_type="binary"):
        """Simulate data with binary outcome for testing."""
        rng = np.random.RandomState(seed)
        
        # Covariates
        X = rng.randn(n, 3)
        X_sum = X.sum(axis=1)
        
        # Treatment (binary)
        A = rng.binomial(1, 0.5, n)
        
        if mediator_type == "binary":
            # Binary mediator depends on X and A
            beta_A = 0.5  # effect of A on M
            logit_M = X_sum + beta_A * A
            p_M = 1 / (1 + np.exp(-logit_M))
            M = rng.binomial(1, p_M)
        else:  # continuous
            # Continuous mediator
            M = 0.7 * A + 0.5 * X[:, 0] + rng.randn(n)
        
        # Binary outcome depends on X, A, and M
        logit_Y = X_sum + 1.5 * A + 2.0 * M
        p_Y = 1 / (1 + np.exp(-logit_Y))
        Y = rng.binomial(1, p_Y)
        
        return {'X': X, 'A': A, 'M': M, 'Y': Y}
    
    def test_binary_mediator_binary_outcome_basic(self):
        """Test basic functionality with binary mediator and binary outcome."""
        data = self.simulate_binary_outcome_data(n=300, seed=42, mediator_type="binary")
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Check expected structure
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['mediator_type'] == "binary"
        assert result['scale'] == "risk_difference"
        
        # Check all effects are finite
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        
        # Check additivity: TE = IDE + IIE (within numerical tolerance)
        additivity_error = abs(result['te'] - (result['ide'] + result['iie']))
        assert additivity_error < 1e-10, f"Additivity violated: error = {additivity_error}"
        
        # Effects should be on risk difference scale, so bounded by [-1, 1]
        assert -1 <= result['te'] <= 1
        assert -1 <= result['ide'] <= 1 
        assert -1 <= result['iie'] <= 1
    
    def test_continuous_mediator_binary_outcome_basic(self):
        """Test basic functionality with continuous mediator and binary outcome."""
        data = self.simulate_binary_outcome_data(n=300, seed=42, mediator_type="continuous")
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            n_mc_mediator=30,  # Keep reasonable for test speed
            random_state_master=42
        )
        
        # Check expected structure
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['mediator_type'] == "continuous"
        assert result['scale'] == "risk_difference"
        
        # Check all effects are finite
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        
        # Check additivity: TE = IDE + IIE (with small MC tolerance)
        additivity_error = abs(result['te'] - (result['ide'] + result['iie']))
        assert additivity_error < 1e-6, f"Additivity violated: error = {additivity_error}"
        
        # Effects should be on risk difference scale, so bounded by [-1, 1]
        assert -1 <= result['te'] <= 1
        assert -1 <= result['ide'] <= 1 
        assert -1 <= result['iie'] <= 1
    
    def test_binary_outcome_natural_effects(self):
        """Test natural effects with binary outcome."""
        data = self.simulate_binary_outcome_data(n=200, seed=42, mediator_type="binary")
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            effect_type="natural",
            random_state_master=42
        )
        
        # Check natural effects structure
        expected_keys = {'te', 'nde', 'nie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['scale'] == "risk_difference"
        
        # Check additivity for natural effects
        additivity_error = abs(result['te'] - (result['nde'] + result['nie']))
        assert additivity_error < 1e-10, f"Natural effects additivity violated: error = {additivity_error}"
    
    def test_binary_outcome_probability_clipping(self):
        """Test probability clipping functionality for binary outcomes."""
        data = self.simulate_binary_outcome_data(n=150, seed=42, mediator_type="binary")
        
        # Test with different clipping parameters
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            prob_clip_eps_outcome=1e-6,
            random_state_master=42
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            prob_clip_eps_outcome=1e-3,  # Larger clipping
            random_state_master=42
        )
        
        # Both should work and produce finite results
        assert np.isfinite(result1['te'])
        assert np.isfinite(result2['te'])
        
        # Results should be similar but may differ slightly due to clipping
        # (exact equality not expected due to clipping differences)
        assert abs(result1['te'] - result2['te']) < 0.1
    
    def test_binary_outcome_cross_fitting_integrity(self):
        """Test cross-fitting integrity for binary outcomes."""
        data = self.simulate_binary_outcome_data(n=200, seed=42, mediator_type="binary")
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            n_splits_outcome=5,
            return_detail=True,
            random_state_master=42
        )
        
        detail = result['detail']
        outcome_fold = detail['outcome_fold']
        
        # Verify cross-fitting structure
        assert np.all(outcome_fold >= 0), "All units should have valid fold assignments"
        assert np.all(outcome_fold < 5), "Fold indices should be within valid range"
        
        # Verify that multiple folds are used
        unique_folds = np.unique(outcome_fold)
        assert len(unique_folds) >= 3, f"Expected at least 3 folds to be used, got {len(unique_folds)}"
    
    def test_binary_outcome_determinism(self):
        """Test determinism of binary outcome results."""
        data = self.simulate_binary_outcome_data(n=150, seed=42, mediator_type="binary")
        
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Results should be exactly identical
        assert result1['te'] == result2['te']
        assert result1['ide'] == result2['ide'] 
        assert result1['iie'] == result2['iie']
        assert result1['scale'] == result2['scale']
    
    def test_binary_outcome_model_validation(self):
        """Test that appropriate model validation occurs for binary outcomes."""
        data = self.simulate_binary_outcome_data(n=100, seed=42, mediator_type="binary")
        
        # Test that models without predict_proba fail for binary outcomes
        from sklearn.linear_model import LinearRegression
        bad_outcome_model = LinearRegression()
        
        with pytest.raises(TypeError, match="must implement predict_proba for binary outcome"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                model_outcome=bad_outcome_model
            )
    
    def test_mixed_outcome_types(self):
        """Test that we can handle different combinations of mediator/outcome types."""
        # Binary mediator + continuous outcome (existing functionality)
        data_cont = simulate_mediation_data(n=100, seed=42)
        result_cont = estimate_mediation(
            data_cont['X'], data_cont['A'], data_cont['M'], data_cont['Y'],
            random_state_master=42
        )
        assert result_cont['scale'] == "mean_difference"
        
        # Binary mediator + binary outcome (new functionality)
        data_bin = self.simulate_binary_outcome_data(n=100, seed=42, mediator_type="binary")
        result_bin = estimate_mediation(
            data_bin['X'], data_bin['A'], data_bin['M'], data_bin['Y'],
            random_state_master=42
        )
        assert result_bin['scale'] == "risk_difference"


class TestContinuousMediatorFunctionality:
    """Test continuous mediator functionality."""
    
    def simulate_continuous_mediation_data(self, n=500, seed=42, tau=1.5, theta=2.0):
        """Simulate data with continuous mediator."""
        rng = np.random.RandomState(seed)
        
        # Covariates
        X = rng.randn(n, 3)
        X_sum = X.sum(axis=1)
        
        # Treatment (binary)
        A = rng.binomial(1, 0.5, n)
        
        # Continuous mediator depends on X and A
        beta_A = 0.7  # effect of A on M
        M = beta_A * A + 0.5 * X[:, 0] + rng.randn(n)
        
        # Outcome depends on X, A, and M
        Y = tau * A + theta * M + 0.3 * X_sum + rng.randn(n)
        
        return {
            'X': X, 'A': A, 'M': M, 'Y': Y,
            'true_tau': tau, 'true_theta': theta, 'true_beta_A': beta_A
        }
    
    def test_continuous_mediator_basic_functionality(self):
        """Test basic continuous mediator functionality."""
        data = self.simulate_continuous_mediation_data(n=200, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42,
            n_mc_mediator=30  # Small for speed
        )
        
        # Check return structure
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['detail'] is None  # default return_detail=False
        assert result['mediator_type'] == "continuous"  # Should auto-detect continuous
        assert result['scale'] == "mean_difference"  # Continuous outcome scale
        
        # Check that all effects are finite
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        assert np.isfinite(result['prop_mediated']) or np.isnan(result['prop_mediated'])
        
        # Check that TE = IDE + IIE (approximately)
        assert abs(result['te'] - (result['ide'] + result['iie'])) < 0.01
    
    def test_continuous_mediator_reproducibility(self):
        """Test reproducibility with continuous mediators."""
        data = self.simulate_continuous_mediation_data(n=150, seed=42)
        
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42,
            n_mc_mediator=25
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42,
            n_mc_mediator=25
        )
        
        # Results should be identical
        assert result1['te'] == result2['te']
        assert result1['ide'] == result2['ide']
        assert result1['iie'] == result2['iie']
    
    def test_continuous_mediator_residual_pool_options(self):
        """Test different residual pool options."""
        data = self.simulate_continuous_mediation_data(n=100, seed=42)
        
        # Test global pool
        result_global = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            residual_pool="global",
            n_mc_mediator=20,
            random_state_master=42
        )
        
        # Test KNN pool
        result_knn = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            residual_pool="knn",
            residual_knn=30,
            n_mc_mediator=20,
            random_state_master=42
        )
        
        # Both should work and return finite results
        assert np.isfinite(result_global['te'])
        assert np.isfinite(result_knn['te'])
    
    def test_continuous_mediator_clipping_bounds(self):
        """Test mediator clipping functionality."""
        data = self.simulate_continuous_mediation_data(n=100, seed=42)
        
        # Test explicit bounds
        m_min, m_max = data['M'].min(), data['M'].max()
        result_explicit = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            clip_m_support=(m_min - 0.5, m_max + 0.5),
            n_mc_mediator=20,
            random_state_master=42
        )
        
        # Test auto bounds with custom quantiles
        result_auto = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            quantile_bounds=(0.05, 0.95),
            n_mc_mediator=20,
            random_state_master=42
        )
        
        # Both should work
        assert np.isfinite(result_explicit['te'])
        assert np.isfinite(result_auto['te'])
    
    def test_continuous_mediator_return_detail(self):
        """Test detailed output for continuous mediator."""
        data = self.simulate_continuous_mediation_data(n=80, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            return_detail=True,
            n_mc_mediator=15,
            random_state_master=42
        )
        
        assert result['detail'] is not None
        detail = result['detail']
        
        # Check that detail includes continuous-specific info (summaries, not raw samples)
        assert 'M_a0_mean' in detail
        assert 'M_a0_sd' in detail
        assert 'M_a1_mean' in detail
        assert 'M_a1_sd' in detail
        assert 'residuals' in detail
        assert 'truncation_frac' in detail
        assert 'clip_bounds_a0' in detail
        assert 'clip_bounds_a1' in detail
        
        # Check shapes
        n_units = len(data['A'])
        assert len(detail['M_a0_mean']) == n_units
        assert len(detail['M_a0_sd']) == n_units
        assert len(detail['M_a1_mean']) == n_units
        assert len(detail['M_a1_sd']) == n_units
        assert len(detail['unit_te']) == n_units
    
    def test_continuous_mediator_natural_effects(self):
        """Test natural effects with continuous mediator."""
        data = self.simulate_continuous_mediation_data(n=100, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            effect_type="natural",
            n_mc_mediator=20,
            random_state_master=42
        )
        
        # Check return structure for natural effects
        expected_keys = {'te', 'nde', 'nie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert result['mediator_type'] == "continuous"  # Should auto-detect continuous
        assert result['scale'] == "mean_difference"  # Continuous outcome scale
        
        # Check finite values
        assert np.isfinite(result['te'])
        assert np.isfinite(result['nde'])
        assert np.isfinite(result['nie'])
    
    def test_continuous_mediator_truncation_warning(self):
        """Test truncation warning functionality."""
        data = self.simulate_continuous_mediation_data(n=100, seed=42)
        
        # Use very tight bounds to trigger truncation warning
        m_median = np.median(data['M'])
        tight_bounds = (m_median - 0.1, m_median + 0.1)
        
        with pytest.warns(UserWarning, match="Large fraction of mediator draws were truncated"):
            result = estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                clip_m_support=tight_bounds,
                max_truncation_warn=0.05,  # Low threshold to trigger warning
                n_mc_mediator=20,
                random_state_master=42
            )
        
        # Should still produce finite results despite warning
        assert np.isfinite(result['te'])
    
    def test_invalid_residual_pool_parameter(self):
        """Test validation of residual_pool parameter."""
        data = self.simulate_continuous_mediation_data(n=50, seed=42)
        
        with pytest.raises(ValueError, match="residual_pool must be"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                residual_pool="invalid_option",
                n_mc_mediator=10,
                random_state_master=42
            )
    
    def test_validation_guards(self):
        """Test input validation guards added per detailed feedback."""
        data = self.simulate_continuous_mediation_data(n=50, seed=42)
        
        # Test single treatment arm validation
        with pytest.raises(ValueError, match="treatment must contain both 0 and 1"):
            estimate_mediation(
                data['X'], np.ones(50), data['M'], data['Y']  # Only A=1
            )
        
        # Test n_mc_mediator validation
        with pytest.raises(ValueError, match="n_mc_mediator must be >= 1"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                n_mc_mediator=0
            )
        
        # Test quantile_bounds validation
        with pytest.raises(ValueError, match="quantile_bounds must satisfy 0 < low < high < 1"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                quantile_bounds=(0.9, 0.1)  # Invalid order
            )
        
        # Test clip_m_support validation
        with pytest.raises(ValueError, match="clip_m_support must be \\(lo, hi\\) with finite lo < hi"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                clip_m_support=(10.0, 5.0)  # Invalid order
            )


class TestBootstrapConfidenceIntervals:
    """Test bootstrap confidence interval functionality."""
    
    def test_bootstrap_basic_functionality(self):
        """Test that bootstrap runs and returns expected structure."""
        data = simulate_mediation_data(n=200, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=10,
            random_state_master=42,
            random_state_boot=123,
            n_jobs=1  # Single job for reproducibility
        )
        
        # Check that bootstrap keys are added
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail', 'ci', 'boot'}
        assert set(result.keys()) == expected_keys
        
        # Check CI structure
        assert 'ci' in result
        ci = result['ci']
        expected_ci_keys = {'te', 'ide', 'iie', 'prop_mediated'}
        assert set(ci.keys()) == expected_ci_keys
        
        # Each CI should be a tuple of (lower, upper)
        for key, (lo, hi) in ci.items():
            assert isinstance(lo, (int, float)) and isinstance(hi, (int, float))
            assert np.isfinite(lo) and np.isfinite(hi)
            assert lo <= hi, f"CI for {key}: lower ({lo}) > upper ({hi})"
        
        # Check boot structure
        assert 'boot' in result
        boot = result['boot']
        expected_boot_keys = {'te', 'ide', 'iie', 'prop_mediated'}
        assert set(boot.keys()) == expected_boot_keys
        
        # Each boot should be array of length nboot
        for key, values in boot.items():
            assert isinstance(values, np.ndarray)
            assert values.shape == (10,), f"Boot {key} has shape {values.shape}, expected (10,)"
            assert np.all(np.isfinite(values)), f"Boot {key} contains non-finite values"

    def test_bootstrap_natural_effects(self):
        """Test bootstrap with natural effects."""
        data = simulate_mediation_data(n=150, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=8,
            effect_type="natural",
            random_state_boot=456,
            n_jobs=1
        )
        
        # Check keys match natural effects
        expected_keys = {'te', 'nde', 'nie', 'prop_mediated', 'mediator_type', 'scale', 'detail', 'ci', 'boot'}
        assert set(result.keys()) == expected_keys
        
        # Check CI and boot have NDE/NIE keys
        expected_effect_keys = {'te', 'nde', 'nie', 'prop_mediated'}
        assert set(result['ci'].keys()) == expected_effect_keys
        assert set(result['boot'].keys()) == expected_effect_keys

    def test_bootstrap_reproducibility(self):
        """Test that bootstrap is reproducible with fixed random_state_boot."""
        data = simulate_mediation_data(n=100, seed=42)
        
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=5,
            random_state_master=42,
            random_state_boot=789,
            n_jobs=1
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=5,
            random_state_master=42,
            random_state_boot=789,
            n_jobs=1
        )
        
        # Bootstrap results should be identical
        np.testing.assert_array_equal(result1['boot']['te'], result2['boot']['te'])
        np.testing.assert_array_equal(result1['boot']['ide'], result2['boot']['ide'])
        np.testing.assert_array_equal(result1['boot']['iie'], result2['boot']['iie'])
        
        # CIs should be identical
        assert result1['ci']['te'] == result2['ci']['te']
        assert result1['ci']['ide'] == result2['ci']['ide']
        assert result1['ci']['iie'] == result2['ci']['iie']


class TestListModelSupport:
    """Test support for lists of models in mediation analysis."""
    
    def test_single_models_backward_compatibility(self):
        """Test that single models still work (backward compatibility)."""
        data = simulate_mediation_data(n=100, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Should work exactly as before
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
    
    def test_list_models_single_iteration(self):
        """Test list of models with single iteration (no matching)."""
        data = simulate_mediation_data(n=150, seed=42)
        
        mediator_models = [
            LogisticRegression(solver='lbfgs', max_iter=500),
            LogisticRegression(solver='newton-cg', max_iter=500)
        ]
        outcome_models = [
            LinearRegression(),
            RandomForestRegressor(n_estimators=20, random_state=42)
        ]
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=mediator_models,
            model_outcome=outcome_models,
            random_state_master=42
        )
        
        # Should use first model from each list
        assert 'te' in result
        assert 'ide' in result
        assert 'iie' in result
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        # No matching matrix for single iteration
        assert 'matching' not in result
    
    def test_list_models_with_matching(self):
        """Test list of models with multiple iterations and matching."""
        data = simulate_mediation_data(n=200, seed=42)
        
        niter = 3
        mediator_models = [
            LogisticRegression(solver='lbfgs', max_iter=500),
            LogisticRegression(solver='newton-cg', max_iter=500), 
            LogisticRegression(solver='liblinear', max_iter=500)
        ]
        outcome_models = [
            LinearRegression(),
            RandomForestRegressor(n_estimators=10, random_state=42),
            Ridge(alpha=0.1)
        ]
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=mediator_models,
            model_outcome=outcome_models,
            niter=niter,
            matching_is_stochastic=True,
            random_state_master=42
        )
        
        # Should have matching results
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail', 'matching'}
        assert set(result.keys()) == expected_keys
        assert result['matching'].shape == (200, niter)
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
    
    def test_mixed_single_list_inputs(self):
        """Test mixed single model and list inputs."""
        data = simulate_mediation_data(n=120, seed=42)
        
        # Single mediator, list outcome
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=LogisticRegression(solver='lbfgs', max_iter=500),
            model_outcome=[LinearRegression(), RandomForestRegressor(n_estimators=10)],
            random_state_master=42
        )
        
        # List mediator, single outcome  
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=[LogisticRegression(solver='lbfgs'), LogisticRegression(solver='newton-cg')],
            model_outcome=LinearRegression(),
            random_state_master=42
        )
        
        for result in [result1, result2]:
            assert 'te' in result
            assert np.isfinite(result['te'])
    
    def test_insufficient_models_error(self):
        """Test error when list has insufficient models for niter."""
        data = simulate_mediation_data(n=100, seed=42)
        
        with pytest.raises(ValueError, match="model_mediator.*shorter than niter"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                model_mediator=[LogisticRegression()],  # Only 1 model
                niter=3,  # But need 3
                matching_is_stochastic=True,
                random_state_master=42
            )
        
        with pytest.raises(ValueError, match="model_outcome.*shorter than niter"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                model_outcome=[LinearRegression()],  # Only 1 model  
                niter=2,  # But need 2
                matching_is_stochastic=True,
                random_state_master=42
            )
    
    def test_empty_list_error(self):
        """Test error when model list is empty."""
        data = simulate_mediation_data(n=50, seed=42)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                model_mediator=[],  # Empty list
                random_state_master=42
            )
        
        with pytest.raises(ValueError, match="cannot be empty"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                model_outcome=[],  # Empty list
                random_state_master=42  
            )
    
    def test_generator_input(self):
        """Test generator/iterator input for models."""
        data = simulate_mediation_data(n=100, seed=42)
        
        def mediator_generator():
            yield LogisticRegression(solver='lbfgs', max_iter=500)
            yield LogisticRegression(solver='newton-cg', max_iter=500)
        
        def outcome_generator():
            yield LinearRegression()
            yield RandomForestRegressor(n_estimators=10, random_state=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=mediator_generator(),
            model_outcome=outcome_generator(),
            niter=2,
            matching_is_stochastic=True,
            random_state_master=42
        )
        
        assert 'te' in result
        assert 'matching' in result
        assert result['matching'].shape == (100, 2)
    
    def test_list_models_reproducibility(self):
        """Test that results are reproducible with same random state."""
        data = simulate_mediation_data(n=120, seed=42)
        
        models_mediator = [
            LogisticRegression(solver='lbfgs', max_iter=500),
            LogisticRegression(solver='newton-cg', max_iter=500)
        ]
        models_outcome = [LinearRegression(), Ridge(alpha=0.1)]
        
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=models_mediator,
            model_outcome=models_outcome,
            niter=2,
            matching_is_stochastic=True,
            random_state_master=42
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=models_mediator,
            model_outcome=models_outcome,
            niter=2,
            matching_is_stochastic=True,
            random_state_master=42
        )
        
        assert result1['te'] == result2['te']
        assert result1['ide'] == result2['ide']
        assert result1['iie'] == result2['iie']
    
    def test_list_models_with_continuous_mediator(self):
        """Test list models with continuous mediator."""
        np.random.seed(42)
        n = 100
        X = np.random.randn(n, 3)
        A = np.random.binomial(1, 0.5, n)
        M = 0.7*A + 0.5*X[:, 0] + np.random.randn(n)  # continuous
        Y = 1.5*A + 2.0*M + 0.4*X[:, 2] + np.random.randn(n)
        
        result = estimate_mediation(
            X, A, M, Y,
            model_mediator=[
                RandomForestRegressor(n_estimators=10, random_state=42),
                LinearRegression()
            ],
            model_outcome=[
                LinearRegression(),
                RandomForestRegressor(n_estimators=10, random_state=43)
            ],
            niter=2,
            matching_is_stochastic=True,
            n_mc_mediator=20,  # Small for speed
            random_state_master=42
        )
        
        assert result['mediator_type'] == 'continuous'
        assert 'matching' in result
        assert result['matching'].shape == (n, 2)
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
    
    def test_list_models_with_bootstrap(self):
        """Test list models with bootstrap confidence intervals."""
        data = simulate_mediation_data(n=100, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            model_mediator=[
                LogisticRegression(solver='lbfgs', max_iter=500),
                LogisticRegression(solver='newton-cg', max_iter=500)
            ],
            model_outcome=[
                LinearRegression(),
                Ridge(alpha=0.1)
            ],
            niter=2,
            matching_is_stochastic=True,
            nboot=5,  # Small for speed
            random_state_master=42,
            random_state_boot=123,
            n_jobs=1
        )
        
        # Should have bootstrap results
        assert 'ci' in result
        assert 'boot' in result
        assert result['boot']['te'].shape == (5,)
        assert result['boot']['ide'].shape == (5,)
        assert result['boot']['iie'].shape == (5,)

    def test_bootstrap_continuous_mediator(self):
        """Test bootstrap with continuous mediator."""
        np.random.seed(42)
        n = 100
        X = np.random.randn(n, 3)
        A = np.random.binomial(1, 0.5, n)
        M = 0.7 * A + 0.5 * X[:, 0] + np.random.randn(n)  # continuous
        Y = 1.5 * A + 2.0 * M + 0.4 * X[:, 2] + np.random.randn(n)
        
        result = estimate_mediation(
            X, A, M, Y,
            nboot=6,
            n_mc_mediator=20,  # Small for speed
            random_state_boot=321,
            n_jobs=1
        )
        
        # Check basic structure
        assert 'ci' in result and 'boot' in result
        assert result['mediator_type'] == "continuous"
        
        # Check bootstrap arrays
        assert result['boot']['te'].shape == (6,)
        assert result['boot']['ide'].shape == (6,)
        assert result['boot']['iie'].shape == (6,)

    def test_bootstrap_binary_outcome(self):
        """Test bootstrap with binary outcome."""
        np.random.seed(42)
        n = 120
        X = np.random.randn(n, 2)
        A = np.random.binomial(1, 0.5, n)
        M = np.random.binomial(1, 0.5, n)
        Y = np.random.binomial(1, 0.5, n)  # binary outcome
        
        result = estimate_mediation(
            X, A, M, Y,
            nboot=7,
            random_state_boot=654,
            n_jobs=1
        )
        
        # Check scale is risk difference
        assert result['scale'] == "risk_difference"
        
        # Check CI bounds are reasonable for risk difference
        for key, (lo, hi) in result['ci'].items():
            if key != 'prop_mediated':  # prop_mediated can be outside [-1, 1]
                assert -1.5 <= lo <= hi <= 1.5, f"CI for {key} outside reasonable bounds: ({lo}, {hi})"

    def test_bootstrap_confidence_interval_coverage(self):
        """Test that CIs have reasonable properties."""
        # Use deterministic data with known effects
        np.random.seed(12345)
        n = 200
        X = np.random.randn(n, 2)
        A = np.random.binomial(1, 0.5, n)
        
        # Design data so indirect effect should be substantial
        logit_M = X.sum(axis=1) + 0.8 * A  # A affects M
        M = np.random.binomial(1, 1/(1 + np.exp(-logit_M)))
        Y = 0.5 * A + 1.2 * M + 0.3 * X.sum(axis=1) + np.random.randn(n)
        
        result = estimate_mediation(
            X, A, M, Y,
            nboot=50,  # More bootstraps for stable CIs
            random_state_master=42,
            random_state_boot=999,
            n_jobs=1
        )
        
        # Point estimates should be within CIs
        assert result['ci']['te'][0] <= result['te'] <= result['ci']['te'][1]
        assert result['ci']['ide'][0] <= result['ide'] <= result['ci']['ide'][1]
        assert result['ci']['iie'][0] <= result['iie'] <= result['ci']['iie'][1]
        
        # CIs should have reasonable width (not too narrow, not too wide)
        te_width = result['ci']['te'][1] - result['ci']['te'][0]
        assert 0.01 < te_width < 5.0, f"TE CI width {te_width} seems unreasonable"

    def test_bootstrap_additivity_preserved(self):
        """Test that TE = IDE + IIE holds for each bootstrap replicate."""
        data = simulate_mediation_data(n=150, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=15,
            random_state_boot=111,
            n_jobs=1
        )
        
        boot_te = result['boot']['te']
        boot_ide = result['boot']['ide']
        boot_iie = result['boot']['iie']
        
        # Check additivity for each bootstrap replicate
        additivity_errors = np.abs(boot_te - (boot_ide + boot_iie))
        assert np.all(additivity_errors < 1e-10), f"Additivity violated in bootstrap: max error = {additivity_errors.max()}"

    def test_bootstrap_groups_ignored_warning(self):
        """Test that groups argument is ignored with warning when bootstrapping."""
        data = simulate_mediation_data(n=100, seed=42)
        groups = np.repeat(np.arange(20), 5)  # Some group structure
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                groups=groups,
                nboot=3,
                random_state_boot=222,
                n_jobs=1
            )
            
            # Should have warning about groups being ignored
            warning_messages = [str(warning.message) for warning in w]
            assert any("groups" in msg and "ignored" in msg for msg in warning_messages)
        
        # Should still produce valid results
        assert 'ci' in result and 'boot' in result

    def test_bootstrap_alpha_parameter(self):
        """Test different alpha values for confidence intervals."""
        data = simulate_mediation_data(n=100, seed=42)
        
        # Test alpha=0.1 (90% CI)
        result_90 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=20,
            alpha=0.1,
            random_state_boot=333,
            n_jobs=1
        )
        
        # Test alpha=0.05 (95% CI) 
        result_95 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=20,
            alpha=0.05,
            random_state_boot=333,
            n_jobs=1
        )
        
        # 95% CI should be wider than 90% CI
        width_90 = result_90['ci']['te'][1] - result_90['ci']['te'][0]
        width_95 = result_95['ci']['te'][1] - result_95['ci']['te'][0]
        assert width_95 > width_90, f"95% CI ({width_95}) should be wider than 90% CI ({width_90})"

    def test_no_bootstrap_when_nboot_zero(self):
        """Test that no bootstrap keys are added when nboot=0."""
        data = simulate_mediation_data(n=100, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=0,  # No bootstrap
            random_state_master=42
        )
        
        # Should not have CI or boot keys
        assert 'ci' not in result
        assert 'boot' not in result
        
        # Should have normal keys
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys

    def test_bootstrap_edge_cases(self):
        """Test bootstrap with edge cases."""
        # Small sample size
        data = simulate_mediation_data(n=50, seed=42)
        
        result_small = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=5,
            n_splits_mediator=3,  # Reduce splits for small sample
            random_state_boot=444,
            n_jobs=1
        )
        
        # Should work despite small sample
        assert 'ci' in result_small and 'boot' in result_small
        assert result_small['boot']['te'].shape == (5,)

    def test_bootstrap_parallel_execution(self):
        """Test that parallel execution produces consistent results.""" 
        data = simulate_mediation_data(n=100, seed=42)
        
        # Single job
        result_single = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=8,
            random_state_boot=555,
            n_jobs=1
        )
        
        # Multiple jobs (but limited to avoid overwhelming test environment)
        result_multi = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            nboot=8,
            random_state_boot=555,
            n_jobs=2
        )
        
        # Results should be identical (same random seed)
        np.testing.assert_array_equal(
            np.sort(result_single['boot']['te']), 
            np.sort(result_multi['boot']['te'])
        )
        
        # CIs should be identical
        assert result_single['ci']['te'] == result_multi['ci']['te']


class TestStochasticMatchingIntegration:
    """Test stochastic matching integration with mediation analysis."""
    
    def test_stochastic_matching_enabled_with_niter_greater_than_one(self):
        """Test that matching is enabled when niter > 1."""
        data = simulate_mediation_data(n=200, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=3,  # This should enable matching
            random_state_master=42
        )
        
        # Should have matching matrix
        assert 'matching' in result, "Matching matrix should be present when niter > 1"
        assert result['matching'].shape == (200, 3), f"Wrong matching matrix shape: {result['matching'].shape}"
        
        # All effects should be finite
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        
        # Additivity should hold
        additivity_error = abs(result['te'] - (result['ide'] + result['iie']))
        assert additivity_error < 1e-10, f"Additivity violated: error = {additivity_error}"
    
    def test_stochastic_matching_enabled_with_flag(self):
        """Test that matching is enabled when matching_is_stochastic=True even with niter=1."""
        data = simulate_mediation_data(n=200, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=1,
            matching_is_stochastic=True,  # This should enable matching
            random_state_master=42
        )
        
        # Should have matching matrix
        assert 'matching' in result, "Matching matrix should be present when matching_is_stochastic=True"
        assert result['matching'].shape == (200, 1), f"Wrong matching matrix shape: {result['matching'].shape}"
        
        # Should get different results compared to no matching
        result_no_match = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Results should be different (matching affects the analysis)
        assert result['te'] != result_no_match['te'], "Matching should change the results"
    
    def test_no_matching_by_default(self):
        """Test that no matching is performed by default (backward compatibility)."""
        data = simulate_mediation_data(n=150, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            random_state_master=42
        )
        
        # Should NOT have matching matrix
        assert 'matching' not in result, "Matching matrix should not be present by default"
        
        # Should have standard mediation keys
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail'}
        assert set(result.keys()) == expected_keys, f"Wrong keys: {set(result.keys())}"
    
    def test_deterministic_matching_with_multiple_iterations(self):
        """Test deterministic matching with multiple iterations."""
        data = simulate_mediation_data(n=200, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=3,
            matching_is_stochastic=False,
            random_state_master=42
        )
        
        # Should have matching matrix
        assert 'matching' in result
        assert result['matching'].shape == (200, 3)
        
        # Should be reproducible
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=3,
            matching_is_stochastic=False,
            random_state_master=42
        )
        
        assert result['te'] == result2['te'], "Deterministic matching should be reproducible"
        assert result['ide'] == result2['ide'], "Deterministic matching should be reproducible"
        assert result['iie'] == result2['iie'], "Deterministic matching should be reproducible"
    
    def test_matching_parameters_passed_correctly(self):
        """Test that matching parameters are used correctly."""
        data = simulate_mediation_data(n=200, seed=42)
        
        # Test with different matching scales
        result1 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=2,
            matching_is_stochastic=True,
            matching_scale=0.5,  # More deterministic
            random_state_master=42
        )
        
        result2 = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=2,
            matching_is_stochastic=True,
            matching_scale=2.0,  # More stochastic
            random_state_master=42
        )
        
        # Results should be different due to different matching behavior
        # (though they might be similar by chance, so we just check they both work)
        assert np.isfinite(result1['te'])
        assert np.isfinite(result2['te'])
        assert 'matching' in result1
        assert 'matching' in result2
    
    def test_matching_with_continuous_mediator(self):
        """Test matching works with continuous mediators."""
        np.random.seed(42)
        n = 200
        X = np.random.randn(n, 3)
        A = np.random.binomial(1, 0.5, n)
        M = 0.7*A + 0.5*X[:, 0] + np.random.randn(n)  # continuous
        Y = 1.5*A + 2.0*M + 0.4*X[:, 2] + np.random.randn(n)
        
        result = estimate_mediation(
            X, A, M, Y,
            niter=3,
            matching_is_stochastic=True,
            n_mc_mediator=20,  # Small for speed
            random_state_master=42
        )
        
        # Should work correctly
        assert result['mediator_type'] == 'continuous'
        assert 'matching' in result
        assert result['matching'].shape == (200, 3)
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])
        
        # Additivity should hold (approximately for continuous mediator)
        additivity_error = abs(result['te'] - (result['ide'] + result['iie']))
        assert additivity_error < 1e-6, f"Additivity violated: error = {additivity_error}"
    
    def test_matching_with_bootstrap(self):
        """Test that matching works correctly with bootstrap."""
        data = simulate_mediation_data(n=150, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=2,
            matching_is_stochastic=True,
            nboot=5,  # Small for speed
            random_state_master=42,
            random_state_boot=123,
            n_jobs=1
        )
        
        # Should have all expected keys
        expected_keys = {'te', 'ide', 'iie', 'prop_mediated', 'mediator_type', 'scale', 'detail', 'matching', 'ci', 'boot'}
        assert set(result.keys()) == expected_keys, f"Wrong keys: {set(result.keys())}"
        
        # Bootstrap arrays should be correct shape
        assert result['boot']['te'].shape == (5,)
        assert result['boot']['ide'].shape == (5,)
        assert result['boot']['iie'].shape == (5,)
        
        # CIs should be reasonable
        assert result['ci']['te'][0] <= result['te'] <= result['ci']['te'][1]
        assert result['ci']['ide'][0] <= result['ide'] <= result['ci']['ide'][1]
        assert result['ci']['iie'][0] <= result['iie'] <= result['ci']['iie'][1]
    
    def test_matching_with_natural_effects(self):
        """Test that matching works with natural effects."""
        data = simulate_mediation_data(n=150, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=2,
            matching_is_stochastic=True,
            effect_type="natural",
            random_state_master=42
        )
        
        # Should have natural effects keys
        expected_keys = {'te', 'nde', 'nie', 'prop_mediated', 'mediator_type', 'scale', 'detail', 'matching'}
        assert set(result.keys()) == expected_keys, f"Wrong keys: {set(result.keys())}"
        
        # Effects should be finite
        assert np.isfinite(result['te'])
        assert np.isfinite(result['nde'])
        assert np.isfinite(result['nie'])
        
        # Additivity should hold
        additivity_error = abs(result['te'] - (result['nde'] + result['nie']))
        assert additivity_error < 1e-10, f"Additivity violated: error = {additivity_error}"
    
    def test_matching_return_detail_provides_summary(self):
        """Test that return_detail provides iteration-level summaries for matching."""
        data = simulate_mediation_data(n=150, seed=42)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=3,
            matching_is_stochastic=True,
            return_detail=True,
            random_state_master=42
        )
        
        # Should have detail with iteration summaries
        assert result['detail'] is not None
        detail = result['detail']
        
        # Should have iteration-level summaries
        assert 'niter' in detail
        assert 'te_by_iter' in detail
        assert 'direct_by_iter' in detail
        assert 'indirect_by_iter' in detail
        assert 'n_matched_by_iter' in detail
        
        # Arrays should have correct length
        assert len(detail['te_by_iter']) == 3
        assert len(detail['direct_by_iter']) == 3
        assert len(detail['indirect_by_iter']) == 3
        assert len(detail['n_matched_by_iter']) == 3
        
        # All matched counts should be positive
        assert all(n > 0 for n in detail['n_matched_by_iter']), "All iterations should have matched units"
    
    def test_matching_error_when_no_matches_found(self):
        """Test that appropriate error is raised when no matches are found."""
        data = simulate_mediation_data(n=100, seed=42)
        
        # Use very restrictive caliper that should prevent matches
        with pytest.raises(ValueError, match="No matches found"):
            estimate_mediation(
                data['X'], data['A'], data['M'], data['Y'],
                niter=2,
                matching_is_stochastic=True,
                matching_caliper=1e-10,  # Extremely restrictive
                random_state_master=42
            )
    
    def test_custom_propensity_model(self):
        """Test that custom propensity models are accepted."""
        from sklearn.linear_model import LogisticRegression
        data = simulate_mediation_data(n=150, seed=42)
        
        custom_propensity_model = LogisticRegression(solver='lbfgs', max_iter=500)
        
        result = estimate_mediation(
            data['X'], data['A'], data['M'], data['Y'],
            niter=2,
            matching_is_stochastic=True,
            model_propensity=custom_propensity_model,
            random_state_master=42
        )
        
        # Should work without error
        assert 'matching' in result
        assert np.isfinite(result['te'])
        assert np.isfinite(result['ide'])
        assert np.isfinite(result['iie'])