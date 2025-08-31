"""
Test module for Fractional Brownian Motion model.

This module contains unit tests for the fBm model implementation,
including parameter validation, data generation, and theoretical properties.
"""

import numpy as np
import pytest
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lrdbench.models.data_models.fbm.fbm_model import FractionalBrownianMotion


class TestFractionalBrownianMotion:
    """Test class for Fractional Brownian Motion model."""
    
    def test_valid_parameters(self):
        """Test that valid parameters are accepted."""
        # Test valid H values
        for H in [0.1, 0.5, 0.9]:
            fbm = FractionalBrownianMotion(H=H, sigma=1.0)
            assert fbm.parameters['H'] == H
            assert fbm.parameters['sigma'] == 1.0
    
    def test_invalid_hurst_parameter(self):
        """Test that invalid Hurst parameters raise ValueError."""
        # Test H <= 0
        with pytest.raises(ValueError):
            FractionalBrownianMotion(H=0.0)
        
        with pytest.raises(ValueError):
            FractionalBrownianMotion(H=-0.1)
        
        # Test H >= 1
        with pytest.raises(ValueError):
            FractionalBrownianMotion(H=1.0)
        
        with pytest.raises(ValueError):
            FractionalBrownianMotion(H=1.1)
    
    def test_invalid_sigma(self):
        """Test that invalid sigma values raise ValueError."""
        with pytest.raises(ValueError):
            FractionalBrownianMotion(H=0.5, sigma=0.0)
        
        with pytest.raises(ValueError):
            FractionalBrownianMotion(H=0.5, sigma=-1.0)
    
    def test_invalid_method(self):
        """Test that invalid methods raise ValueError."""
        with pytest.raises(ValueError):
            FractionalBrownianMotion(H=0.5, method='invalid_method')
    
    def test_data_generation(self):
        """Test that data generation works correctly."""
        fbm = FractionalBrownianMotion(H=0.7, sigma=1.0)
        n = 1000
        
        # Test different methods
        for method in ['davies_harte', 'cholesky', 'circulant']:
            fbm.set_parameters(method=method)
            data = fbm.generate(n, seed=42)
            
            assert len(data) == n
            assert isinstance(data, np.ndarray)
            assert np.isfinite(data).all()
    
    def test_reproducibility(self):
        """Test that data generation is reproducible with the same seed."""
        fbm = FractionalBrownianMotion(H=0.6, sigma=1.0)
        n = 500
        
        # Generate two series with the same seed
        data1 = fbm.generate(n, seed=123)
        data2 = fbm.generate(n, seed=123)
        
        np.testing.assert_array_equal(data1, data2)
    
    def test_theoretical_properties(self):
        """Test that theoretical properties are correct."""
        H = 0.8
        sigma = 2.0
        fbm = FractionalBrownianMotion(H=H, sigma=sigma)
        
        properties = fbm.get_theoretical_properties()
        
        assert properties['hurst_parameter'] == H
        assert properties['variance'] == sigma**2
        assert properties['self_similarity_exponent'] == H
        assert properties['long_range_dependence'] == (H > 0.5)
        assert properties['stationary_increments'] is True
        assert properties['gaussian'] is True
    
    def test_increments(self):
        """Test that increments are computed correctly."""
        fbm = FractionalBrownianMotion(H=0.5, sigma=1.0)
        n = 100
        
        data = fbm.generate(n, seed=42)
        increments = fbm.get_increments(data)
        
        assert len(increments) == n - 1
        assert np.allclose(increments, np.diff(data))
    
    def test_parameter_setting(self):
        """Test that parameters can be updated."""
        fbm = FractionalBrownianMotion(H=0.5, sigma=1.0)
        
        # Update parameters
        fbm.set_parameters(H=0.8, sigma=2.0)
        
        assert fbm.parameters['H'] == 0.8
        assert fbm.parameters['sigma'] == 2.0
    
    def test_string_representations(self):
        """Test string representations of the model."""
        fbm = FractionalBrownianMotion(H=0.7, sigma=1.5)
        
        str_repr = str(fbm)
        repr_repr = repr(fbm)
        
        assert "FractionalBrownianMotion" in str_repr
        assert "FractionalBrownianMotion" in repr_repr
        assert "0.7" in str_repr
        assert "1.5" in str_repr


if __name__ == "__main__":
    pytest.main([__file__])
