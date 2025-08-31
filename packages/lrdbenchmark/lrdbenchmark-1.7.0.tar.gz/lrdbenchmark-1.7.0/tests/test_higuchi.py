import numpy as np
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for testing

from lrdbench.analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator


class TestHiguchiEstimator:
    """Test cases for HiguchiEstimator."""
    
    def test_valid_parameters(self):
        """Test valid parameter initialization."""
        estimator = HiguchiEstimator(min_k=2, max_k=50)
        params = estimator.get_parameters()
        assert params['min_k'] == 2
        assert params['max_k'] == 50
        assert params['k_values'] is None
    
    def test_invalid_min_k(self):
        """Test invalid minimum k value."""
        with pytest.raises(ValueError, match="min_k must be at least 2"):
            HiguchiEstimator(min_k=1)
    
    def test_invalid_max_k(self):
        """Test invalid maximum k value."""
        with pytest.raises(ValueError, match="max_k must be greater than min_k"):
            HiguchiEstimator(min_k=10, max_k=5)
    
    def test_invalid_k_values(self):
        """Test invalid k values."""
        with pytest.raises(ValueError, match="All k values must be at least 2"):
            HiguchiEstimator(k_values=[1, 5, 10])
        
        with pytest.raises(ValueError, match="k values must be in ascending order"):
            HiguchiEstimator(k_values=[10, 5, 20])
    
    def test_estimation_length_and_type(self):
        """Test estimation returns correct length and type."""
        estimator = HiguchiEstimator()
        
        # Generate test data (fBm-like)
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        assert isinstance(results, dict)
        assert 'fractal_dimension' in results
        assert 'hurst_parameter' in results
        assert 'k_values' in results
        assert 'curve_lengths' in results
        assert 'r_squared' in results
        assert 'std_error' in results
        assert 'confidence_interval' in results
        
        assert isinstance(results['fractal_dimension'], float)
        assert isinstance(results['hurst_parameter'], float)
        assert isinstance(results['k_values'], list)
        assert isinstance(results['curve_lengths'], list)
        assert len(results['k_values']) == len(results['curve_lengths'])
        assert len(results['k_values']) >= 3
        
        # Check relationship between D and H
        assert np.isclose(results['hurst_parameter'], 2 - results['fractal_dimension'])
    
    def test_estimation_with_short_data(self):
        """Test estimation with insufficient data."""
        estimator = HiguchiEstimator()
        data = np.random.normal(0, 1, 5)  # Too short
        
        with pytest.raises(ValueError, match="Data length must be at least 10"):
            estimator.estimate(data)
    
    def test_estimation_with_large_k(self):
        """Test estimation with k values too large."""
        estimator = HiguchiEstimator(min_k=1000, max_k=2000)
        data = np.random.normal(0, 1, 100)  # Too short for large k values
        
        with pytest.raises(ValueError, match="Need at least 3 k values"):
            estimator.estimate(data)
    
    def test_reproducibility(self):
        """Test that estimation is reproducible with same seed."""
        estimator1 = HiguchiEstimator()
        estimator2 = HiguchiEstimator()
        
        np.random.seed(42)
        data1 = np.cumsum(np.random.normal(0, 1, 1000))
        
        np.random.seed(42)
        data2 = np.cumsum(np.random.normal(0, 1, 1000))
        
        results1 = estimator1.estimate(data1)
        results2 = estimator2.estimate(data2)
        
        assert np.allclose(results1['fractal_dimension'], results2['fractal_dimension'])
        assert np.allclose(results1['hurst_parameter'], results2['hurst_parameter'])
        assert np.allclose(results1['r_squared'], results2['r_squared'])
    
    def test_custom_k_values(self):
        """Test estimation with custom k values."""
        k_values = [2, 4, 8, 16, 32]
        estimator = HiguchiEstimator(k_values=k_values)
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        assert results['k_values'] == k_values
        assert len(results['curve_lengths']) == len(k_values)
    
    def test_confidence_intervals(self):
        """Test confidence interval calculation."""
        estimator = HiguchiEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        estimator.estimate(data)
        ci = estimator.get_confidence_intervals()
        
        assert 'fractal_dimension' in ci
        assert 'hurst_parameter' in ci
        assert len(ci['fractal_dimension']) == 2
        assert len(ci['hurst_parameter']) == 2
        assert ci['fractal_dimension'][0] < ci['fractal_dimension'][1]
        assert ci['hurst_parameter'][0] < ci['hurst_parameter'][1]
        
        # Test different confidence level
        ci_90 = estimator.get_confidence_intervals(confidence_level=0.90)
        ci_95 = estimator.get_confidence_intervals(confidence_level=0.95)
        
        # 90% CI should be narrower than 95% CI
        width_90_D = ci_90['fractal_dimension'][1] - ci_90['fractal_dimension'][0]
        width_95_D = ci_95['fractal_dimension'][1] - ci_95['fractal_dimension'][0]
        assert width_90_D < width_95_D
    
    def test_estimation_quality(self):
        """Test estimation quality metrics."""
        estimator = HiguchiEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        estimator.estimate(data)
        quality = estimator.get_estimation_quality()
        
        assert 'r_squared' in quality
        assert 'p_value' in quality
        assert 'std_error' in quality
        assert 'n_k_values' in quality
        
        assert 0 <= quality['r_squared'] <= 1
        assert 0 <= quality['p_value'] <= 1
        assert quality['std_error'] > 0
        assert quality['n_k_values'] >= 3
    
    def test_parameter_setting(self):
        """Test parameter setting after initialization."""
        estimator = HiguchiEstimator(min_k=2)
        
        estimator.set_parameters(max_k=100)
        params = estimator.get_parameters()
        
        assert params['max_k'] == 100
    
    def test_string_representations(self):
        """Test string representations."""
        estimator = HiguchiEstimator(min_k=2, max_k=50)
        
        str_repr = str(estimator)
        repr_repr = repr(estimator)
        
        assert 'HiguchiEstimator' in str_repr
        assert 'min_k' in str_repr
        assert 'HiguchiEstimator' in repr_repr
        assert 'parameters' in repr_repr
    
    def test_curve_length_calculation(self):
        """Test curve length calculation for known data."""
        estimator = HiguchiEstimator()
        
        # Simple test data: [0, 1, 2, 3, 4, 5]
        data = np.array([0, 1, 2, 3, 4, 5])
        
        # For k=2, we expect:
        # m=0: segments [0,2], [2,4], [4,6] -> lengths [2, 2, 1] -> avg = 1.67
        # m=1: segments [1,3], [3,5] -> lengths [2, 2] -> avg = 2.0
        # Overall average should be around 1.83
        
        length = estimator._calculate_curve_length(data, 2)
        
        # The exact calculation involves normalization factors
        # This is a basic test to ensure the method works
        assert length > 0
        assert np.isfinite(length)
    
    def test_curve_length_with_small_k(self):
        """Test curve length calculation with k too large."""
        estimator = HiguchiEstimator()
        
        data = np.array([0, 1, 2, 3, 4, 5])
        
        # k=10 is too large for data of length 6
        with pytest.raises(ValueError, match="No valid curve lengths calculated"):
            estimator._calculate_curve_length(data, 10)
    
    def test_plot_scaling_without_results(self):
        """Test plotting without estimation results."""
        estimator = HiguchiEstimator()
        
        with pytest.raises(ValueError, match="No estimation results available"):
            estimator.plot_scaling()
    
    def test_plot_scaling_with_results(self):
        """Test plotting with estimation results."""
        estimator = HiguchiEstimator()
        
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
    
    def test_fractal_dimension_range(self):
        """Test that fractal dimension is in reasonable range."""
        estimator = HiguchiEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        # Fractal dimension should be between 1 and 2 for time series
        assert 1.0 <= results['fractal_dimension'] <= 2.0
        
        # Hurst parameter should be between 0 and 1
        assert 0.0 <= results['hurst_parameter'] <= 1.0
    
    def test_relationship_D_and_H(self):
        """Test the relationship between fractal dimension and Hurst parameter."""
        estimator = HiguchiEstimator()
        
        np.random.seed(42)
        data = np.cumsum(np.random.normal(0, 1, 1000))
        
        results = estimator.estimate(data)
        
        # H = 2 - D
        expected_H = 2 - results['fractal_dimension']
        assert np.isclose(results['hurst_parameter'], expected_H, rtol=1e-10)
