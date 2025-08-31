import numpy as np
import pytest

from causalem import clip_logit


def test_clip_logit_basic_functionality():
    """Test basic functionality of clip_logit."""
    p = np.array([0.1, 0.5, 0.9])
    eps = 0.001
    result = clip_logit(p, eps)
    
    # For probabilities away from 0/1, should match regular logit
    expected = np.log(p / (1 - p))
    np.testing.assert_array_almost_equal(result, expected)


def test_clip_logit_handles_edge_cases():
    """Test that clip_logit properly handles edge cases with clipping."""
    eps = 0.001
    
    # Test with extreme probabilities that need clipping
    p_edge = np.array([0.0, 1.0])
    result = clip_logit(p_edge, eps)
    
    # Should not produce infinite values
    assert np.all(np.isfinite(result))
    
    # Check that clipping works correctly
    expected_low = np.log(eps / (1 - eps))
    expected_high = np.log((1 - eps) / eps)
    
    np.testing.assert_almost_equal(result[0], expected_low)
    np.testing.assert_almost_equal(result[1], expected_high)


def test_clip_logit_different_eps_values():
    """Test clip_logit with different eps values."""
    p = np.array([0.0, 0.5, 1.0])
    
    # Test with larger eps
    eps1 = 0.01
    result1 = clip_logit(p, eps1)
    
    # Test with smaller eps
    eps2 = 0.001
    result2 = clip_logit(p, eps2)
    
    # Both should be finite
    assert np.all(np.isfinite(result1))
    assert np.all(np.isfinite(result2))
    
    # Larger eps should produce values closer to 0 (less extreme)
    assert abs(result1[0]) < abs(result2[0])
    assert abs(result1[2]) < abs(result2[2])


def test_clip_logit_array_shapes():
    """Test clip_logit with different array shapes."""
    eps = 0.001
    
    # 1D array
    p1d = np.array([0.2, 0.5, 0.8])
    result1d = clip_logit(p1d, eps)
    assert result1d.shape == p1d.shape
    
    # 2D array
    p2d = np.array([[0.2, 0.8], [0.3, 0.7]])
    result2d = clip_logit(p2d, eps)
    assert result2d.shape == p2d.shape


def test_clip_logit_public_api_accessible():
    """Test that clip_logit is accessible from the main causalem module."""
    # This test ensures the function is properly exported
    assert hasattr(clip_logit, '__call__')
    assert clip_logit.__name__ == 'clip_logit'