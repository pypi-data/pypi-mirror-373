import numpy as np
import pytest

from lrdbench.analysis.temporal.dma.dma_estimator import DMAEstimator


class TestDMAEstimator:
    """Test cases for DMAEstimator."""
    
    def test_valid_parameters(self):
        """Test valid parameter initialization."""
        estimator = DMAEstimator(min_window_size=4, max_window_size=100)
        params = estimator.get_parameters()
        assert params['min_window_size'] == 4
        assert params['max_window_size'] == 100
        assert params['window_sizes'] is None
        assert params['overlap'] is True
    
    def test_invalid_min_window_size(self):
        """Test invalid minimum window size."""
        with pytest.raises(ValueError, match="min_window_size must be at least 3"):
            DMAEstimator(min_window_size=2)
    
    def test_invalid_max_window_size(self):
        """Test invalid maximum window size."""
        with pytest.raises(ValueError, match="max_window_size must be greater than min_window_size"):
            DMAEstimator(min_window_size=10, max_window_size=5)
    
    def test_invalid_window_sizes(self):
        """Test invalid window sizes."""
        with pytest.raises(ValueError, match="All window sizes must be at least 3"):
            DMAEstimator(window_sizes=[2, 10, 20])
        
        with pytest.raises(ValueError, match="Window sizes must be in ascending order"):
            DMAEstimator(window_sizes=[20, 10, 30])
    
    def test_estimation_length_and_type(self):
        """Test estimation returns correct length and type."""
        estimator = DMAEstimator()
        
        # Generate test data (fBm-like)
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        assert isinstance(results, dict)
        assert 'hurst_parameter' in results
        assert 'window_sizes' in results
        assert 'fluctuation_values' in results
        assert 'r_squared' in results
        assert 'std_error' in results
        assert 'confidence_interval' in results
        
        assert isinstance(results['hurst_parameter'], float)
        assert isinstance(results['window_sizes'], list)
        assert isinstance(results['fluctuation_values'], list)
        assert len(results['window_sizes']) == len(results['fluctuation_values'])
        assert len(results['window_sizes']) >= 3
    
    def test_estimation_with_short_data(self):
        """Test estimation with insufficient data."""
        estimator = DMAEstimator()
        data = np.random.normal(0, 1, 5)  # Too short
        
        with pytest.raises(ValueError, match="Data length must be at least 10"):
            estimator.estimate(data)
    
    def test_estimation_with_large_window(self):
        """Test estimation with window size too large."""
        estimator = DMAEstimator(min_window_size=1000, max_window_size=2000)
        data = np.random.normal(0, 1, 100)  # Too short for large windows
        
        with pytest.raises(ValueError, match="Need at least 3 window sizes"):
            estimator.estimate(data)
    
    def test_reproducibility(self):
        """Test that estimation is reproducible with same seed."""
        estimator1 = DMAEstimator()
        estimator2 = DMAEstimator()
        
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
        window_sizes = [4, 8, 16, 32, 64]
        estimator = DMAEstimator(window_sizes=window_sizes)
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        assert results['window_sizes'] == window_sizes
        assert len(results['fluctuation_values']) == len(window_sizes)
    
    def test_overlap_parameter(self):
        """Test estimation with different overlap settings."""
        # Test with overlap=True (default)
        estimator_overlap = DMAEstimator(overlap=True)
        
        # Test with overlap=False
        estimator_no_overlap = DMAEstimator(overlap=False)
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results_overlap = estimator_overlap.estimate(data)
        results_no_overlap = estimator_no_overlap.estimate(data)
        
        # Results should be different but both valid
        assert isinstance(results_overlap['hurst_parameter'], float)
        assert isinstance(results_no_overlap['hurst_parameter'], float)
        assert results_overlap['hurst_parameter'] != results_no_overlap['hurst_parameter']
    
    def test_confidence_intervals(self):
        """Test confidence interval calculation."""
        estimator = DMAEstimator()
        
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
        estimator = DMAEstimator()
        
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
        estimator = DMAEstimator(min_window_size=4)
        
        estimator.set_parameters(max_window_size=200)
        params = estimator.get_parameters()
        
        assert params['max_window_size'] == 200
    
    def test_string_representations(self):
        """Test string representations."""
        estimator = DMAEstimator(min_window_size=4, max_window_size=100)
        
        str_repr = str(estimator)
        repr_repr = repr(estimator)
        
        assert 'DMAEstimator' in str_repr
        assert 'min_window_size' in str_repr
        assert 'DMAEstimator' in repr_repr
        assert 'parameters' in repr_repr
    
    def test_fluctuation_calculation(self):
        """Test fluctuation calculation for known data."""
        estimator = DMAEstimator()
        
        # Simple test data: [1, 2, 3, 4, 5]
        data = np.array([1, 2, 3, 4, 5])
        
        # For window size 3, we expect a reasonable fluctuation value
        fluctuation = estimator._calculate_fluctuation(data, 3)
        
        # The exact value depends on the moving average calculation
        # This is a basic test to ensure the method works
        assert fluctuation > 0
        assert np.isfinite(fluctuation)
    
    def test_fluctuation_with_overlap(self):
        """Test fluctuation calculation with overlap."""
        estimator_overlap = DMAEstimator(overlap=True)
        estimator_no_overlap = DMAEstimator(overlap=False)
        
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
        # Both should work without error
        fluct_overlap = estimator_overlap._calculate_fluctuation(data, 4)
        fluct_no_overlap = estimator_no_overlap._calculate_fluctuation(data, 4)
        
        assert fluct_overlap > 0
        assert fluct_no_overlap > 0
        assert fluct_overlap != fluct_no_overlap  # Different methods should give different results
    
    def test_plot_scaling_without_results(self):
        """Test plotting without estimation results."""
        estimator = DMAEstimator()
        
        with pytest.raises(ValueError, match="No estimation results available"):
            estimator.plot_scaling()
    
    def test_plot_scaling_with_results(self):
        """Test plotting with estimation results."""
        estimator = DMAEstimator()
        
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
    
    def test_hurst_parameter_range(self):
        """Test that Hurst parameter is in reasonable range."""
        estimator = DMAEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        # Hurst parameter should be between 0 and 1 for most time series
        # (though theoretically it can be outside this range for some processes)
        assert results['hurst_parameter'] > -1  # Very permissive lower bound
        assert results['hurst_parameter'] < 2   # Very permissive upper bound
    
    def test_fluctuation_values_positive(self):
        """Test that all fluctuation values are positive."""
        estimator = DMAEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        # All fluctuation values should be positive
        assert all(f > 0 for f in results['fluctuation_values'])
    
    def test_window_size_validation(self):
        """Test that window sizes are properly validated."""
        # Test with window size larger than data length
        estimator = DMAEstimator(min_window_size=1000, max_window_size=2000)
        data = np.random.normal(0, 1, 100)
        
        with pytest.raises(ValueError, match="Need at least 3 window sizes"):
            estimator.estimate(data)
