"""
Unit tests for contamination models and complex time series library.

This module provides comprehensive testing for:
1. ContaminationModel - individual contamination methods
2. ComplexTimeSeriesLibrary - complex time series generation
3. Integration tests for estimator robustness
"""

import numpy as np
import pytest
from typing import Dict, List, Any

from lrdbench.models.contamination.contamination_models import (
    ContaminationModel, ContaminationType, ContaminationConfig
)
from lrdbench.models.contamination.complex_time_series_library import (
    ComplexTimeSeriesLibrary, ComplexTimeSeriesType, ComplexTimeSeriesConfig
)
from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise


class TestContaminationModel:
    """Test cases for ContaminationModel class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.contamination_model = ContaminationModel()
        self.test_data = np.random.randn(1000)
        self.n = 1000
    
    def test_initialization(self):
        """Test ContaminationModel initialization."""
        # Test with default config
        model = ContaminationModel()
        assert model.config is not None
        assert isinstance(model.config, ContaminationConfig)
        
        # Test with custom config
        custom_config = ContaminationConfig(
            trend_slope=0.05,
            noise_gaussian_std=0.2
        )
        model = ContaminationModel(custom_config)
        assert model.config.trend_slope == 0.05
        assert model.config.noise_gaussian_std == 0.2
    
    def test_add_trend_linear(self):
        """Test linear trend addition."""
        contaminated = self.contamination_model.add_trend_linear(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that trend is added (data should be different)
        assert not np.allclose(contaminated, self.test_data)
        
        # Check that trend is increasing (for positive slope)
        diff = np.diff(contaminated)
        assert np.mean(diff) > np.mean(np.diff(self.test_data))
    
    def test_add_trend_polynomial(self):
        """Test polynomial trend addition."""
        contaminated = self.contamination_model.add_trend_polynomial(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that trend is added
        assert not np.allclose(contaminated, self.test_data)
    
    def test_add_trend_exponential(self):
        """Test exponential trend addition."""
        contaminated = self.contamination_model.add_trend_exponential(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that trend is added
        assert not np.allclose(contaminated, self.test_data)
    
    def test_add_trend_seasonal(self):
        """Test seasonal trend addition."""
        contaminated = self.contamination_model.add_trend_seasonal(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that trend is added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check for periodicity (autocorrelation at seasonal lag)
        autocorr = np.correlate(contaminated, contaminated, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        # Should have peaks at seasonal periods
        assert np.max(autocorr[50:150]) > np.mean(autocorr)
    
    def test_add_artifact_spikes(self):
        """Test spike artifact addition."""
        contaminated = self.contamination_model.add_artifact_spikes(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that spikes are added (variance should increase)
        assert np.var(contaminated) > np.var(self.test_data)
        
        # Check that some values are significantly different
        diff = np.abs(contaminated - self.test_data)
        assert np.max(diff) > 2.0  # Should have spikes with amplitude > 2
    
    def test_add_artifact_level_shifts(self):
        """Test level shift artifact addition."""
        contaminated = self.contamination_model.add_artifact_level_shifts(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that level shifts are added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check for cumulative effect of level shifts
        diff = contaminated - self.test_data
        assert np.std(diff) > 0  # Should have variation in level shifts
    
    def test_add_artifact_missing_data(self):
        """Test missing data artifact addition."""
        contaminated = self.contamination_model.add_artifact_missing_data(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that NaN values are present
        assert np.any(np.isnan(contaminated))
        
        # Check that not all values are NaN
        assert not np.all(np.isnan(contaminated))
    
    def test_add_noise_gaussian(self):
        """Test Gaussian noise addition."""
        contaminated = self.contamination_model.add_noise_gaussian(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that noise is added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check that variance increases
        assert np.var(contaminated) > np.var(self.test_data)
    
    def test_add_noise_colored(self):
        """Test colored noise addition."""
        contaminated = self.contamination_model.add_noise_colored(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that noise is added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check that colored noise has different spectral properties
        fft_original = np.fft.fft(self.test_data)
        fft_contaminated = np.fft.fft(contaminated)
        
        # Power spectra should be different
        power_original = np.abs(fft_original) ** 2
        power_contaminated = np.abs(fft_contaminated) ** 2
        
        assert not np.allclose(power_original, power_contaminated)
    
    def test_add_noise_impulsive(self):
        """Test impulsive noise addition."""
        contaminated = self.contamination_model.add_noise_impulsive(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that impulsive noise is added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check for outliers
        diff = np.abs(contaminated - self.test_data)
        assert np.max(diff) > 3.0  # Should have impulsive noise with amplitude > 3
    
    def test_add_sampling_irregular(self):
        """Test irregular sampling simulation."""
        contaminated = self.contamination_model.add_sampling_irregular(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that NaN values are present
        assert np.any(np.isnan(contaminated))
        
        # Check that not all values are NaN
        assert not np.all(np.isnan(contaminated))
    
    def test_add_sampling_aliasing(self):
        """Test aliasing effects addition."""
        contaminated = self.contamination_model.add_sampling_aliasing(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that aliasing is added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check for periodic component
        fft_contaminated = np.fft.fft(contaminated)
        power_spectrum = np.abs(fft_contaminated) ** 2
        
        # Should have peaks at aliasing frequency
        freqs = np.fft.fftfreq(len(self.test_data))
        aliasing_freq_idx = np.argmin(np.abs(freqs - 0.1))  # Default aliasing frequency
        assert power_spectrum[aliasing_freq_idx] > np.mean(power_spectrum)
    
    def test_add_measurement_systematic(self):
        """Test systematic measurement bias addition."""
        contaminated = self.contamination_model.add_measurement_systematic(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that systematic bias is added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check that bias is constant
        bias = contaminated - self.test_data
        assert np.allclose(bias, bias[0])  # All bias values should be the same
    
    def test_add_measurement_random(self):
        """Test random measurement errors addition."""
        contaminated = self.contamination_model.add_measurement_random(self.test_data)
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that random errors are added
        assert not np.allclose(contaminated, self.test_data)
        
        # Check that variance increases
        assert np.var(contaminated) > np.var(self.test_data)
    
    def test_apply_contamination_multiple(self):
        """Test applying multiple contaminations."""
        contamination_types = [
            ContaminationType.TREND_LINEAR,
            ContaminationType.NOISE_GAUSSIAN,
            ContaminationType.ARTIFACT_SPIKES
        ]
        
        contaminated = self.contamination_model.apply_contamination(
            self.test_data, contamination_types
        )
        
        # Check that data length is preserved
        assert len(contaminated) == len(self.test_data)
        
        # Check that contaminations are applied
        assert not np.allclose(contaminated, self.test_data)
        
        # Check that variance increases significantly
        assert np.var(contaminated) > np.var(self.test_data)
    
    def test_get_contamination_info(self):
        """Test contamination information retrieval."""
        contamination_types = [
            ContaminationType.TREND_LINEAR,
            ContaminationType.NOISE_GAUSSIAN
        ]
        
        info = self.contamination_model.get_contamination_info(contamination_types)
        
        # Check that info is returned
        assert isinstance(info, dict)
        assert len(info) == 2
        
        # Check that keys match contamination types
        assert 'trend_linear' in info
        assert 'noise_gaussian' in info
        
        # Check that descriptions are strings
        assert isinstance(info['trend_linear'], str)
        assert isinstance(info['noise_gaussian'], str)


class TestComplexTimeSeriesLibrary:
    """Test cases for ComplexTimeSeriesLibrary class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.library = ComplexTimeSeriesLibrary()
        self.n = 1000
    
    def test_initialization(self):
        """Test ComplexTimeSeriesLibrary initialization."""
        # Test with default config
        library = ComplexTimeSeriesLibrary()
        assert library.config is not None
        assert isinstance(library.config, ComplexTimeSeriesConfig)
        
        # Test with custom config
        custom_config = ComplexTimeSeriesConfig(
            hurst_parameter=0.8,
            trend_strength=0.05
        )
        library = ComplexTimeSeriesLibrary(custom_config)
        assert library.config.hurst_parameter == 0.8
        assert library.config.trend_strength == 0.05
    
    def test_generate_heavy_tailed_trending(self):
        """Test heavy-tailed trending time series generation."""
        result = self.library.generate_heavy_tailed_trending(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        assert 'base_model' in result
        assert 'true_hurst' in result
        assert 'contaminations' in result
        assert 'description' in result
        assert 'challenges' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check metadata
        assert result['base_model'] == 'fGn'
        assert result['true_hurst'] == self.library.config.hurst_parameter
        assert 'linear_trend' in result['contaminations']
        assert 'impulsive_noise' in result['contaminations']
    
    def test_generate_multidimensional_fractal(self):
        """Test multidimensional fractal time series generation."""
        result = self.library.generate_multidimensional_fractal(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check metadata
        assert result['base_model'] == 'fBm'
        assert result['true_hurst'] == self.library.config.hurst_parameter
    
    def test_generate_irregular_sampled_artifacts(self):
        """Test irregular sampled artifacts time series generation."""
        result = self.library.generate_irregular_sampled_artifacts(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check for missing data
        assert np.any(np.isnan(data))
        
        # Check metadata
        assert result['base_model'] == 'ARFIMA'
        assert result['true_hurst'] == self.library.config.arfima_d + 0.5
    
    def test_generate_noisy_seasonal(self):
        """Test noisy seasonal time series generation."""
        result = self.library.generate_noisy_seasonal(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check for seasonality
        autocorr = np.correlate(data, data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        # Should have peaks at seasonal periods
        assert np.max(autocorr[50:150]) > np.mean(autocorr)
        
        # Check metadata
        assert result['base_model'] == 'fGn'
        assert result['true_hurst'] == self.library.config.hurst_parameter
    
    def test_generate_long_memory_level_shifts(self):
        """Test long memory level shifts time series generation."""
        result = self.library.generate_long_memory_level_shifts(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check metadata
        assert result['base_model'] == 'ARFIMA'
        assert result['true_hurst'] == 0.9
    
    def test_generate_multifractal_measurement_errors(self):
        """Test multifractal measurement errors time series generation."""
        result = self.library.generate_multifractal_measurement_errors(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check metadata
        assert result['base_model'] == 'MRW'
        assert result['true_hurst'] == self.library.config.hurst_parameter
    
    def test_generate_antipersistent_impulsive(self):
        """Test anti-persistent impulsive time series generation."""
        result = self.library.generate_antipersistent_impulsive(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check for missing data
        assert np.any(np.isnan(data))
        
        # Check metadata
        assert result['base_model'] == 'fGn'
        assert result['true_hurst'] == 0.3
    
    def test_generate_stationary_systematic_bias(self):
        """Test stationary systematic bias time series generation."""
        result = self.library.generate_stationary_systematic_bias(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check metadata
        assert result['base_model'] == 'fGn'
        assert result['true_hurst'] == 0.5
    
    def test_generate_nonstationary_aliasing(self):
        """Test non-stationary aliasing time series generation."""
        result = self.library.generate_nonstationary_aliasing(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check metadata
        assert result['base_model'] == 'fBm'
        assert result['true_hurst'] == self.library.config.hurst_parameter
    
    def test_generate_mixed_regime_missing(self):
        """Test mixed regime missing time series generation."""
        result = self.library.generate_mixed_regime_missing(self.n, seed=42)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'data' in result
        
        # Check data properties
        data = result['data']
        assert len(data) == self.n
        assert isinstance(data, np.ndarray)
        
        # Check for missing data
        assert np.any(np.isnan(data))
        
        # Check metadata
        assert result['base_model'] == 'Mixed (fGn + ARFIMA)'
        assert isinstance(result['true_hurst'], list)
        assert len(result['true_hurst']) == 2
    
    def test_generate_complex_time_series(self):
        """Test generic complex time series generation."""
        # Test all series types
        for series_type in ComplexTimeSeriesType:
            result = self.library.generate_complex_time_series(series_type, self.n, seed=42)
            
            # Check result structure
            assert isinstance(result, dict)
            assert 'data' in result
            assert 'base_model' in result
            assert 'true_hurst' in result
            assert 'contaminations' in result
            assert 'description' in result
            assert 'challenges' in result
            
            # Check data properties
            data = result['data']
            assert len(data) == self.n
            assert isinstance(data, np.ndarray)
    
    def test_get_all_series_types(self):
        """Test getting all series types."""
        series_types = self.library.get_all_series_types()
        
        # Check that all types are returned
        assert isinstance(series_types, list)
        assert len(series_types) == len(ComplexTimeSeriesType)
        
        # Check that all types are valid
        for series_type in series_types:
            assert isinstance(series_type, ComplexTimeSeriesType)
    
    def test_get_series_description(self):
        """Test getting series descriptions."""
        for series_type in ComplexTimeSeriesType:
            description = self.library.get_series_description(series_type)
            
            # Check that description is returned
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_invalid_series_type(self):
        """Test handling of invalid series type."""
        with pytest.raises(ValueError):
            self.library.generate_complex_time_series("invalid_type", self.n)


class TestContaminationIntegration:
    """Integration tests for contamination with estimators."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.library = ComplexTimeSeriesLibrary()
        self.n = 1000
    
    def test_contamination_effects_on_statistics(self):
        """Test that contaminations affect basic statistics as expected."""
        # Generate clean fGn
        fgn = FractionalGaussianNoise(H=0.7)
        clean_data = fgn.generate(self.n, seed=42)
        
        # Generate contaminated version
        contamination_model = ContaminationModel()
        contaminated_data = contamination_model.apply_contamination(
            clean_data,
            [
                ContaminationType.TREND_LINEAR,
                ContaminationType.NOISE_GAUSSIAN,
                ContaminationType.ARTIFACT_SPIKES
            ]
        )
        
        # Check that statistics are affected
        assert np.var(contaminated_data) > np.var(clean_data)
        assert np.std(contaminated_data) > np.std(clean_data)
        
        # Check that mean is affected (due to trend)
        assert not np.allclose(np.mean(contaminated_data), np.mean(clean_data))
    
    def test_complex_series_characteristics(self):
        """Test that complex series have expected characteristics."""
        # Test heavy-tailed trending
        result = self.library.generate_heavy_tailed_trending(self.n, seed=42)
        data = result['data']
        
        # Should have higher variance than clean fGn
        fgn = FractionalGaussianNoise(H=0.7)
        clean_data = fgn.generate(self.n, seed=42)
        assert np.var(data) > np.var(clean_data)
        
        # Should have outliers (impulsive noise)
        assert np.max(np.abs(data)) > np.max(np.abs(clean_data))
        
        # Should have trend (increasing mean)
        first_half = data[:self.n//2]
        second_half = data[self.n//2:]
        assert np.mean(second_half) > np.mean(first_half)
    
    def test_missing_data_handling(self):
        """Test that missing data is properly handled."""
        result = self.library.generate_irregular_sampled_artifacts(self.n, seed=42)
        data = result['data']
        
        # Check that missing data is present
        assert np.any(np.isnan(data))
        
        # Check that not all data is missing
        assert not np.all(np.isnan(data))
        
        # Check that missing data percentage is reasonable
        missing_percentage = np.sum(np.isnan(data)) / len(data)
        assert 0.01 < missing_percentage < 0.3  # Between 1% and 30% missing
    
    def test_seasonality_detection(self):
        """Test that seasonal patterns are detectable."""
        result = self.library.generate_noisy_seasonal(self.n, seed=42)
        data = result['data']
        
        # Check for seasonality using autocorrelation
        autocorr = np.correlate(data, data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Should have peaks at seasonal periods (around 100)
        seasonal_region = autocorr[50:150]
        assert np.max(seasonal_region) > np.mean(autocorr)
    
    def test_level_shift_detection(self):
        """Test that level shifts are detectable."""
        result = self.library.generate_long_memory_level_shifts(self.n, seed=42)
        data = result['data']
        
        # Check for level shifts using cumulative sum
        cumsum = np.cumsum(data - np.mean(data))
        
        # Should have significant changes in slope
        diff_cumsum = np.diff(cumsum)
        assert np.std(diff_cumsum) > 0  # Should have variation in changes


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
