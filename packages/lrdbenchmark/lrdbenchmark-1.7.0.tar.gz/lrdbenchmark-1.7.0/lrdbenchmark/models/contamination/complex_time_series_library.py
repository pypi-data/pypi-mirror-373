"""
Complex Time Series Library

This module provides a library of complex time series types that combine
different base models with specific contaminations, creating realistic
test cases for estimator robustness testing.

Each time series type represents a specific real-world scenario with
known characteristics and challenges for estimation methods.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from models.contamination.contamination_models import (
    ContaminationModel,
    ContaminationType,
    ContaminationConfig,
)
from models.data_models.fbm.fbm_model import FractionalBrownianMotion
from models.data_models.fgn.fgn_model import FractionalGaussianNoise
from models.data_models.arfima.arfima_model import ARFIMAModel
from models.data_models.mrw.mrw_model import MultifractalRandomWalk


class ComplexTimeSeriesType(Enum):
    """Types of complex time series in the library."""

    # Heavy-tailed with non-stationary trend
    HEAVY_TAILED_TRENDING = "heavy_tailed_trending"

    # Multidimensional with fractal properties
    MULTIDIMENSIONAL_FRACTAL = "multidimensional_fractal"

    # Irregular sampled with artifacts
    IRREGULAR_SAMPLED_ARTIFACTS = "irregular_sampled_artifacts"

    # Noisy with seasonal patterns
    NOISY_SEASONAL = "noisy_seasonal"

    # Long-memory with level shifts
    LONG_MEMORY_LEVEL_SHIFTS = "long_memory_level_shifts"

    # Multifractal with measurement errors
    MULTIFRACTAL_MEASUREMENT_ERRORS = "multifractal_measurement_errors"

    # Anti-persistent with impulsive noise
    ANTIPERSISTENT_IMPULSIVE = "antipersistent_impulsive"

    # Stationary with systematic bias
    STATIONARY_SYSTEMATIC_BIAS = "stationary_systematic_bias"

    # Non-stationary with aliasing
    NONSTATIONARY_ALIASING = "nonstationary_aliasing"

    # Mixed regime with missing data
    MIXED_REGIME_MISSING = "mixed_regime_missing"


@dataclass
class ComplexTimeSeriesConfig:
    """Configuration for complex time series generation."""

    # Base model parameters
    hurst_parameter: float = 0.7
    arfima_d: float = 0.3
    mrw_lambda_squared: float = 0.1

    # Contamination parameters
    trend_strength: float = 0.02
    noise_level: float = 0.1
    artifact_probability: float = 0.01
    missing_data_probability: float = 0.05

    # Sampling parameters
    irregular_sampling_probability: float = 0.1
    aliasing_frequency: float = 0.05

    # Measurement parameters
    systematic_bias: float = 0.1
    measurement_noise_std: float = 0.05


class ComplexTimeSeriesLibrary:
    """
    Library of complex time series types for robust testing.

    This class provides methods to generate various complex time series
    that combine different base models with realistic contaminations.
    """

    def __init__(self, config: Optional[ComplexTimeSeriesConfig] = None):
        """
        Initialize the complex time series library.

        Parameters
        ----------
        config : ComplexTimeSeriesConfig, optional
            Configuration for time series generation. If None, uses defaults.
        """
        self.config = config or ComplexTimeSeriesConfig()
        self.contamination_model = ContaminationModel()

    def generate_heavy_tailed_trending(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate heavy-tailed time series with non-stationary trend.

        Characteristics:
        - Base: fGn with H > 0.5 (long memory)
        - Contamination: Linear trend + impulsive noise
        - Challenge: Trend removal affects long-memory estimation

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base fGn with long memory
        fgn = FractionalGaussianNoise(H=self.config.hurst_parameter)
        base_data = fgn.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [ContaminationType.TREND_LINEAR, ContaminationType.NOISE_IMPULSIVE],
            slope=self.config.trend_strength,
            probability=0.01,
            amplitude=2.0,
        )

        return {
            "data": contaminated,
            "base_model": "fGn",
            "true_hurst": self.config.hurst_parameter,
            "contaminations": ["linear_trend", "impulsive_noise"],
            "description": "Heavy-tailed time series with non-stationary linear trend",
            "challenges": ["trend_removal", "outlier_robustness"],
        }

    def generate_multidimensional_fractal(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate multidimensional time series with fractal properties.

        Characteristics:
        - Base: fBm (non-stationary fractal)
        - Contamination: Polynomial trend + colored noise
        - Challenge: Non-stationarity affects spectral estimation

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base fBm
        fbm = FractionalBrownianMotion(H=self.config.hurst_parameter)
        base_data = fbm.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [ContaminationType.TREND_POLYNOMIAL, ContaminationType.NOISE_COLORED],
            degree=2,
            power=1.5,
        )

        return {
            "data": contaminated,
            "base_model": "fBm",
            "true_hurst": self.config.hurst_parameter,
            "contaminations": ["polynomial_trend", "colored_noise"],
            "description": "Multidimensional fractal time series with polynomial trend",
            "challenges": ["non_stationarity", "trend_detection"],
        }

    def generate_irregular_sampled_artifacts(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate irregularly sampled time series with artifacts.

        Characteristics:
        - Base: ARFIMA (long memory)
        - Contamination: Irregular sampling + spikes + level shifts
        - Challenge: Missing data and artifacts affect estimation

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base ARFIMA
        arfima = ARFIMAModel(d=self.config.arfima_d)
        base_data = arfima.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [
                ContaminationType.SAMPLING_IRREGULAR,
                ContaminationType.ARTIFACT_SPIKES,
                ContaminationType.ARTIFACT_LEVEL_SHIFTS,
            ],
            probability=self.config.irregular_sampling_probability,
            amplitude=3.0,
        )

        return {
            "data": contaminated,
            "base_model": "ARFIMA",
            "true_hurst": self.config.arfima_d + 0.5,  # H = d + 0.5 for ARFIMA
            "contaminations": ["irregular_sampling", "spikes", "level_shifts"],
            "description": "Irregularly sampled long-memory time series with artifacts",
            "challenges": ["missing_data", "artifact_detection", "irregular_sampling"],
        }

    def generate_noisy_seasonal(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate noisy time series with seasonal patterns.

        Characteristics:
        - Base: fGn (stationary)
        - Contamination: Seasonal trend + Gaussian noise
        - Challenge: Seasonal component affects spectral analysis

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base fGn
        fgn = FractionalGaussianNoise(H=self.config.hurst_parameter)
        base_data = fgn.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [ContaminationType.TREND_SEASONAL, ContaminationType.NOISE_GAUSSIAN],
            period=100,
            amplitude=0.5,
            std=self.config.noise_level,
        )

        return {
            "data": contaminated,
            "base_model": "fGn",
            "true_hurst": self.config.hurst_parameter,
            "contaminations": ["seasonal_trend", "gaussian_noise"],
            "description": "Noisy time series with seasonal patterns",
            "challenges": ["seasonal_detrending", "noise_filtering"],
        }

    def generate_long_memory_level_shifts(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate long-memory time series with level shifts.

        Characteristics:
        - Base: ARFIMA with strong long memory
        - Contamination: Level shifts + systematic bias
        - Challenge: Level shifts affect stationarity assumptions

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base ARFIMA with strong long memory
        arfima = ARFIMAModel(d=0.4)  # Strong long memory
        base_data = arfima.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [
                ContaminationType.ARTIFACT_LEVEL_SHIFTS,
                ContaminationType.MEASUREMENT_SYSTEMATIC,
            ],
            probability=0.01,
            amplitude=3.0,
            bias=self.config.systematic_bias,
        )

        return {
            "data": contaminated,
            "base_model": "ARFIMA",
            "true_hurst": 0.9,  # H = d + 0.5
            "contaminations": ["level_shifts", "systematic_bias"],
            "description": "Long-memory time series with level shifts and systematic bias",
            "challenges": ["change_point_detection", "bias_correction"],
        }

    def generate_multifractal_measurement_errors(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate multifractal time series with measurement errors.

        Characteristics:
        - Base: MRW (multifractal)
        - Contamination: Random measurement errors + aliasing
        - Challenge: Measurement errors affect multifractal analysis

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base MRW
        mrw = MultifractalRandomWalk(
            H=self.config.hurst_parameter, lambda_param=self.config.mrw_lambda_squared
        )
        base_data = mrw.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [ContaminationType.MEASUREMENT_RANDOM, ContaminationType.SAMPLING_ALIASING],
            std=self.config.measurement_noise_std,
            frequency=self.config.aliasing_frequency,
        )

        return {
            "data": contaminated,
            "base_model": "MRW",
            "true_hurst": self.config.hurst_parameter,
            "contaminations": ["measurement_errors", "aliasing"],
            "description": "Multifractal time series with measurement errors and aliasing",
            "challenges": [
                "error_correction",
                "aliasing_detection",
                "multifractal_robustness",
            ],
        }

    def generate_antipersistent_impulsive(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate anti-persistent time series with impulsive noise.

        Characteristics:
        - Base: fGn with H < 0.5 (anti-persistent)
        - Contamination: Impulsive noise + missing data
        - Challenge: Anti-persistence + outliers affect estimation

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base fGn with anti-persistence
        fgn = FractionalGaussianNoise(H=0.3)  # Anti-persistent
        base_data = fgn.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [
                ContaminationType.NOISE_IMPULSIVE,
                ContaminationType.ARTIFACT_MISSING_DATA,
            ],
            probability=0.02,
            amplitude=4.0,
        )

        return {
            "data": contaminated,
            "base_model": "fGn",
            "true_hurst": 0.3,
            "contaminations": ["impulsive_noise", "missing_data"],
            "description": "Anti-persistent time series with impulsive noise and missing data",
            "challenges": [
                "outlier_robustness",
                "missing_data_handling",
                "anti_persistence_detection",
            ],
        }

    def generate_stationary_systematic_bias(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate stationary time series with systematic bias.

        Characteristics:
        - Base: fGn with H = 0.5 (independent)
        - Contamination: Systematic bias + colored noise
        - Challenge: Bias affects mean estimation

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base fGn with H = 0.5 (independent)
        fgn = FractionalGaussianNoise(H=0.5)
        base_data = fgn.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [ContaminationType.MEASUREMENT_SYSTEMATIC, ContaminationType.NOISE_COLORED],
            bias=self.config.systematic_bias,
            power=1.0,
        )

        return {
            "data": contaminated,
            "base_model": "fGn",
            "true_hurst": 0.5,
            "contaminations": ["systematic_bias", "colored_noise"],
            "description": "Stationary time series with systematic bias and colored noise",
            "challenges": [
                "bias_detection",
                "mean_estimation",
                "noise_characterization",
            ],
        }

    def generate_nonstationary_aliasing(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate non-stationary time series with aliasing effects.

        Characteristics:
        - Base: fBm (non-stationary)
        - Contamination: Aliasing + exponential trend
        - Challenge: Non-stationarity + aliasing affect spectral analysis

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base fBm
        fbm = FractionalBrownianMotion(H=self.config.hurst_parameter)
        base_data = fbm.generate(n)

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [ContaminationType.SAMPLING_ALIASING, ContaminationType.TREND_EXPONENTIAL],
            frequency=self.config.aliasing_frequency,
            rate=0.05,
        )

        return {
            "data": contaminated,
            "base_model": "fBm",
            "true_hurst": self.config.hurst_parameter,
            "contaminations": ["aliasing", "exponential_trend"],
            "description": "Non-stationary time series with aliasing and exponential trend",
            "challenges": [
                "aliasing_detection",
                "trend_removal",
                "non_stationarity_handling",
            ],
        }

    def generate_mixed_regime_missing(
        self, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate mixed regime time series with missing data.

        Characteristics:
        - Base: Combination of different models
        - Contamination: Missing data + level shifts
        - Challenge: Regime changes + missing data affect estimation

        Parameters
        ----------
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate mixed regime: first half fGn, second half ARFIMA
        n1 = n // 2
        n2 = n - n1

        fgn = FractionalGaussianNoise(H=0.6)
        arfima = ARFIMAModel(d=0.2)

        data1 = fgn.generate(n1)
        data2 = arfima.generate(n2)

        # Combine with a smooth transition
        transition_length = min(50, n1 // 4)
        transition = np.linspace(0, 1, transition_length)

        # Apply transition
        data1[-transition_length:] *= 1 - transition
        data2[:transition_length] *= transition

        base_data = np.concatenate([data1, data2])

        # Add contaminations
        contaminated = self.contamination_model.apply_contamination(
            base_data,
            [
                ContaminationType.ARTIFACT_MISSING_DATA,
                ContaminationType.ARTIFACT_LEVEL_SHIFTS,
            ],
            probability=self.config.missing_data_probability,
            amplitude=1.5,
        )

        return {
            "data": contaminated,
            "base_model": "Mixed (fGn + ARFIMA)",
            "true_hurst": [0.6, 0.7],  # Different H for different regimes
            "contaminations": ["missing_data", "level_shifts"],
            "description": "Mixed regime time series with missing data and level shifts",
            "challenges": [
                "regime_detection",
                "missing_data_handling",
                "change_point_detection",
            ],
        }

    def generate_complex_time_series(
        self, series_type: ComplexTimeSeriesType, n: int, seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a complex time series of the specified type.

        Parameters
        ----------
        series_type : ComplexTimeSeriesType
            Type of complex time series to generate
        n : int
            Length of time series
        seed : int, optional
            Random seed

        Returns
        -------
        Dict[str, Any]
            Dictionary containing time series and metadata
        """
        if series_type == ComplexTimeSeriesType.HEAVY_TAILED_TRENDING:
            return self.generate_heavy_tailed_trending(n, seed)
        elif series_type == ComplexTimeSeriesType.MULTIDIMENSIONAL_FRACTAL:
            return self.generate_multidimensional_fractal(n, seed)
        elif series_type == ComplexTimeSeriesType.IRREGULAR_SAMPLED_ARTIFACTS:
            return self.generate_irregular_sampled_artifacts(n, seed)
        elif series_type == ComplexTimeSeriesType.NOISY_SEASONAL:
            return self.generate_noisy_seasonal(n, seed)
        elif series_type == ComplexTimeSeriesType.LONG_MEMORY_LEVEL_SHIFTS:
            return self.generate_long_memory_level_shifts(n, seed)
        elif series_type == ComplexTimeSeriesType.MULTIFRACTAL_MEASUREMENT_ERRORS:
            return self.generate_multifractal_measurement_errors(n, seed)
        elif series_type == ComplexTimeSeriesType.ANTIPERSISTENT_IMPULSIVE:
            return self.generate_antipersistent_impulsive(n, seed)
        elif series_type == ComplexTimeSeriesType.STATIONARY_SYSTEMATIC_BIAS:
            return self.generate_stationary_systematic_bias(n, seed)
        elif series_type == ComplexTimeSeriesType.NONSTATIONARY_ALIASING:
            return self.generate_nonstationary_aliasing(n, seed)
        elif series_type == ComplexTimeSeriesType.MIXED_REGIME_MISSING:
            return self.generate_mixed_regime_missing(n, seed)
        else:
            raise ValueError(f"Unknown complex time series type: {series_type}")

    def get_all_series_types(self) -> List[ComplexTimeSeriesType]:
        """
        Get all available complex time series types.

        Returns
        -------
        List[ComplexTimeSeriesType]
            List of all available series types
        """
        return list(ComplexTimeSeriesType)

    def get_series_description(self, series_type: ComplexTimeSeriesType) -> str:
        """
        Get description of a complex time series type.

        Parameters
        ----------
        series_type : ComplexTimeSeriesType
            Type of complex time series

        Returns
        -------
        str
            Description of the series type
        """
        descriptions = {
            ComplexTimeSeriesType.HEAVY_TAILED_TRENDING: "Heavy-tailed time series with non-stationary trend",
            ComplexTimeSeriesType.MULTIDIMENSIONAL_FRACTAL: "Multidimensional fractal time series with polynomial trend",
            ComplexTimeSeriesType.IRREGULAR_SAMPLED_ARTIFACTS: "Irregularly sampled long-memory time series with artifacts",
            ComplexTimeSeriesType.NOISY_SEASONAL: "Noisy time series with seasonal patterns",
            ComplexTimeSeriesType.LONG_MEMORY_LEVEL_SHIFTS: "Long-memory time series with level shifts and systematic bias",
            ComplexTimeSeriesType.MULTIFRACTAL_MEASUREMENT_ERRORS: "Multifractal time series with measurement errors and aliasing",
            ComplexTimeSeriesType.ANTIPERSISTENT_IMPULSIVE: "Anti-persistent time series with impulsive noise and missing data",
            ComplexTimeSeriesType.STATIONARY_SYSTEMATIC_BIAS: "Stationary time series with systematic bias and colored noise",
            ComplexTimeSeriesType.NONSTATIONARY_ALIASING: "Non-stationary time series with aliasing and exponential trend",
            ComplexTimeSeriesType.MIXED_REGIME_MISSING: "Mixed regime time series with missing data and level shifts",
        }
        return descriptions.get(series_type, "Unknown series type")
