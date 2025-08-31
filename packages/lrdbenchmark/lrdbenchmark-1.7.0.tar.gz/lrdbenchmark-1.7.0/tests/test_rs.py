import numpy as np
import pytest

from lrdbench.analysis.temporal.rs.rs_estimator import RSEstimator


class TestRSEstimator:
    """Test cases for RSEstimator."""
    
    def test_valid_parameters(self):
        """Test valid parameter initialization."""
        estimator = RSEstimator(min_window_size=10, max_window_size=100)
        params = estimator.get_parameters()
        assert params['min_window_size'] == 10
        assert params['max_window_size'] == 100
        assert params['window_sizes'] is None
        assert params['overlap'] is False
    
    def test_invalid_min_window_size(self):
        """Test invalid minimum window size."""
        with pytest.raises(ValueError, match="min_window_size must be at least 4"):
            RSEstimator(min_window_size=3)
    
    def test_invalid_max_window_size(self):
        """Test invalid maximum window size."""
        with pytest.raises(ValueError, match="max_window_size must be greater than min_window_size"):
            RSEstimator(min_window_size=10, max_window_size=5)
    
    def test_invalid_window_sizes(self):
        """Test invalid window sizes."""
        with pytest.raises(ValueError, match="All window sizes must be at least 4"):
            RSEstimator(window_sizes=[3, 10, 20])
        
        with pytest.raises(ValueError, match="Window sizes must be in ascending order"):
            RSEstimator(window_sizes=[20, 10, 30])
    
    def test_estimation_length_and_type(self):
        """Test estimation returns correct length and type."""
        estimator = RSEstimator()
        
        # Generate test data (fBm-like)
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        assert isinstance(results, dict)
        assert 'hurst_parameter' in results
        assert 'window_sizes' in results
        assert 'rs_values' in results
        assert 'r_squared' in results
        assert 'std_error' in results
        assert 'confidence_interval' in results
        
        assert isinstance(results['hurst_parameter'], float)
        assert isinstance(results['window_sizes'], list)
        assert isinstance(results['rs_values'], list)
        assert len(results['window_sizes']) == len(results['rs_values'])
        assert len(results['window_sizes']) >= 3
    
    def test_estimation_with_short_data(self):
        """Test estimation with insufficient data."""
        estimator = RSEstimator()
        data = np.random.normal(0, 1, 15)  # Too short
        
        with pytest.raises(ValueError, match="Need at least 3 window sizes"):
            estimator.estimate(data)
    
    def test_estimation_with_large_window(self):
        """Test estimation with window size too large."""
        estimator = RSEstimator(min_window_size=1000, max_window_size=2000)
        data = np.random.normal(0, 1, 100)  # Too short for large windows
        
        with pytest.raises(ValueError, match="Need at least 3 window sizes"):
            estimator.estimate(data)
    
    def test_reproducibility(self):
        """Test that estimation is reproducible with same seed."""
        estimator1 = RSEstimator()
        estimator2 = RSEstimator()
        
        np.random.seed(42)
        data1 = np.cumsum(np.random.normal(0, 1, 1000))
        
        np.random.seed(42)
        data2 = np.cumsum(np.random.normal(0, 1, 1000))
        
        results1 = estimator1.estimate(data1)
        results2 = estimator2.estimate(data2)
        
        assert np.allclose(results1['hurst_parameter'], results2['hurst_parameter'])
        assert np.allclose(results1['r_squared'], results2['r_squared'])
    
    def test_custom_window_sizes(self):
        """Test estimation with custom window sizes."""
        window_sizes = [10, 20, 40, 80]
        estimator = RSEstimator(window_sizes=window_sizes)
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        assert results['window_sizes'] == window_sizes
        assert len(results['rs_values']) == len(window_sizes)
    
    def test_confidence_intervals(self):
        """Test confidence interval calculation."""
        estimator = RSEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        estimator.estimate(data)
        ci = estimator.get_confidence_intervals()
        
        assert 'hurst_parameter' in ci
        assert len(ci['hurst_parameter']) == 2
        assert ci['hurst_parameter'][0] < ci['hurst_parameter'][1]
        
        # Test different confidence level
        ci_90 = estimator.get_confidence_intervals(confidence_level=0.90)
        ci_95 = estimator.get_confidence_intervals(confidence_level=0.95)
        
        # 90% CI should be narrower than 95% CI
        width_90 = ci_90['hurst_parameter'][1] - ci_90['hurst_parameter'][0]
        width_95 = ci_95['hurst_parameter'][1] - ci_95['hurst_parameter'][0]
        assert width_90 < width_95
    
    def test_estimation_quality(self):
        """Test estimation quality metrics."""
        estimator = RSEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        estimator.estimate(data)
        quality = estimator.get_estimation_quality()
        
        assert 'r_squared' in quality
        assert 'p_value' in quality
        assert 'std_error' in quality
        assert 'n_windows' in quality
        
        assert 0 <= quality['r_squared'] <= 1
        assert 0 <= quality['p_value'] <= 1
        assert quality['std_error'] > 0
        assert quality['n_windows'] >= 3
    
    def test_parameter_setting(self):
        """Test parameter setting after initialization."""
        estimator = RSEstimator(min_window_size=10)
        
        estimator.set_parameters(max_window_size=200)
        params = estimator.get_parameters()
        
        assert params['max_window_size'] == 200
    
    def test_string_representations(self):
        """Test string representations."""
        estimator = RSEstimator(min_window_size=10, max_window_size=100)
        
        str_repr = str(estimator)
        repr_repr = repr(estimator)
        
        assert 'RSEstimator' in str_repr
        assert 'min_window_size' in str_repr
        assert 'RSEstimator' in repr_repr
        assert 'parameters' in repr_repr
    
    def test_rs_statistic_calculation(self):
        """Test R/S statistic calculation for known data."""
        estimator = RSEstimator()
        
        # Simple test data: [1, 2, 3, 4, 5]
        data = np.array([1, 2, 3, 4, 5])
        
        # For window size 5, we have one window
        rs_val = estimator._calculate_rs_statistic(data, 5)
        
        # Manual calculation:
        # Mean = 3
        # Deviations = [-2, -1, 0, 1, 2]
        # Cumulative deviations = [-2, -3, -3, -2, 0]
        # Range R = 0 - (-3) = 3
        # Standard deviation S = sqrt(2.5) ≈ 1.581
        # R/S = 3 / 1.581 ≈ 1.897
        
        expected_rs = 3 / np.sqrt(2.5)
        assert np.isclose(rs_val, expected_rs, rtol=1e-10)
    
    def test_rs_statistic_with_zero_std(self):
        """Test R/S statistic with zero standard deviation."""
        estimator = RSEstimator()
        
        # Data with zero standard deviation
        data = np.array([1, 1, 1, 1, 1])
        
        # This should skip the window due to zero standard deviation
        with pytest.raises(ValueError, match="No valid R/S values calculated"):
            estimator._calculate_rs_statistic(data, 5)
    
    def test_plot_scaling_without_results(self):
        """Test plotting without estimation results."""
        estimator = RSEstimator()
        
        with pytest.raises(ValueError, match="No estimation results available"):
            estimator.plot_scaling()
    
    def test_plot_scaling_with_results(self):
        """Test plotting with estimation results."""
        estimator = RSEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        estimator.estimate(data)
        
        # Test that plotting doesn't raise an error
        try:
            estimator.plot_scaling()
        except Exception as e:
            # If matplotlib is not available, this is expected
            if "matplotlib" in str(e).lower():
                pytest.skip("Matplotlib not available for plotting test")
            else:
                raise
