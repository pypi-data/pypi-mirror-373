"""
Real-World Confounds and Contamination Models

This module provides a comprehensive system for adding various real-world confounds
to time series data, allowing for robust testing of estimators under realistic conditions.

Contamination types:
1. Trends (linear, polynomial, exponential, seasonal)
2. Artifacts (spikes, level shifts, missing data)
3. Noise (Gaussian, colored, impulsive)
4. Sampling issues (irregular sampling, aliasing)
5. Measurement errors (systematic, random)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import warnings


class ContaminationType(Enum):
    """Types of contamination that can be applied to time series."""

    TREND_LINEAR = "trend_linear"
    TREND_POLYNOMIAL = "trend_polynomial"
    TREND_EXPONENTIAL = "trend_exponential"
    TREND_SEASONAL = "trend_seasonal"
    ARTIFACT_SPIKES = "artifact_spikes"
    ARTIFACT_LEVEL_SHIFTS = "artifact_level_shifts"
    ARTIFACT_MISSING_DATA = "artifact_missing_data"
    NOISE_GAUSSIAN = "noise_gaussian"
    NOISE_COLORED = "noise_colored"
    NOISE_IMPULSIVE = "noise_impulsive"
    SAMPLING_IRREGULAR = "sampling_irregular"
    SAMPLING_ALIASING = "sampling_aliasing"
    MEASUREMENT_SYSTEMATIC = "measurement_systematic"
    MEASUREMENT_RANDOM = "measurement_random"


@dataclass
class ContaminationConfig:
    """Configuration for contamination parameters."""

    # Trend parameters
    trend_slope: float = 0.01
    trend_polynomial_degree: int = 2
    trend_exponential_rate: float = 0.1
    trend_seasonal_period: int = 100
    trend_seasonal_amplitude: float = 0.5

    # Artifact parameters
    artifact_spike_probability: float = 0.01
    artifact_spike_amplitude: float = 3.0
    artifact_level_shift_probability: float = 0.005
    artifact_level_shift_amplitude: float = 2.0
    artifact_missing_probability: float = 0.02

    # Noise parameters
    noise_gaussian_std: float = 0.1
    noise_colored_power: float = 1.0
    noise_impulsive_probability: float = 0.005
    noise_impulsive_amplitude: float = 5.0

    # Sampling parameters
    sampling_irregular_probability: float = 0.1
    sampling_aliasing_frequency: float = 0.1

    # Measurement parameters
    measurement_systematic_bias: float = 0.1
    measurement_random_std: float = 0.05


class ContaminationModel:
    """
    Base class for contamination models.

    This class provides methods to add various types of real-world confounds
    to time series data, allowing for robust testing of estimators.
    """

    def __init__(self, config: Optional[ContaminationConfig] = None):
        """
        Initialize the contamination model.

        Parameters
        ----------
        config : ContaminationConfig, optional
            Configuration for contamination parameters. If None, uses defaults.
        """
        self.config = config or ContaminationConfig()

    def add_trend_linear(
        self, data: np.ndarray, slope: Optional[float] = None
    ) -> np.ndarray:
        """
        Add a linear trend to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        slope : float, optional
            Slope of the linear trend. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with linear trend added
        """
        slope = slope or self.config.trend_slope
        n = len(data)
        trend = slope * np.arange(n)
        return data + trend

    def add_trend_polynomial(
        self, data: np.ndarray, degree: Optional[int] = None
    ) -> np.ndarray:
        """
        Add a polynomial trend to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        degree : int, optional
            Degree of polynomial. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with polynomial trend added
        """
        degree = degree or self.config.trend_polynomial_degree
        n = len(data)
        x = np.arange(n) / n  # Normalize to [0, 1]

        # Generate polynomial coefficients
        coeffs = np.random.randn(degree + 1) * 0.1
        coeffs[0] = 0  # No constant term

        trend = np.polyval(coeffs, x)
        return data + trend

    def add_trend_exponential(
        self, data: np.ndarray, rate: Optional[float] = None
    ) -> np.ndarray:
        """
        Add an exponential trend to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        rate : float, optional
            Exponential rate. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with exponential trend added
        """
        rate = rate or self.config.trend_exponential_rate
        n = len(data)
        x = np.arange(n) / n  # Normalize to [0, 1]
        trend = np.exp(rate * x) - 1
        return data + trend

    def add_trend_seasonal(
        self,
        data: np.ndarray,
        period: Optional[int] = None,
        amplitude: Optional[float] = None,
    ) -> np.ndarray:
        """
        Add a seasonal trend to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        period : int, optional
            Period of seasonal component. If None, uses config value.
        amplitude : float, optional
            Amplitude of seasonal component. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with seasonal trend added
        """
        period = period or self.config.trend_seasonal_period
        amplitude = amplitude or self.config.trend_seasonal_amplitude
        n = len(data)

        # Generate seasonal component
        t = np.arange(n)
        seasonal = amplitude * np.sin(2 * np.pi * t / period)

        # Add some harmonics for more realistic seasonality
        seasonal += 0.3 * amplitude * np.sin(4 * np.pi * t / period)

        return data + seasonal

    def add_artifact_spikes(
        self,
        data: np.ndarray,
        probability: Optional[float] = None,
        amplitude: Optional[float] = None,
    ) -> np.ndarray:
        """
        Add random spikes to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        probability : float, optional
            Probability of spike at each point. If None, uses config value.
        amplitude : float, optional
            Amplitude of spikes. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with spikes added
        """
        probability = probability or self.config.artifact_spike_probability
        amplitude = amplitude or self.config.artifact_spike_amplitude

        contaminated = data.copy()
        n = len(data)

        # Generate spike locations
        spike_mask = np.random.random(n) < probability

        # Add spikes with random signs
        spike_amplitudes = np.random.choice([-1, 1], size=n) * amplitude
        contaminated[spike_mask] += spike_amplitudes[spike_mask]

        return contaminated

    def add_artifact_level_shifts(
        self,
        data: np.ndarray,
        probability: Optional[float] = None,
        amplitude: Optional[float] = None,
    ) -> np.ndarray:
        """
        Add level shifts to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        probability : float, optional
            Probability of level shift at each point. If None, uses config value.
        amplitude : float, optional
            Amplitude of level shifts. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with level shifts added
        """
        probability = probability or self.config.artifact_level_shift_probability
        amplitude = amplitude or self.config.artifact_level_shift_amplitude

        contaminated = data.copy()
        n = len(data)

        # Generate level shift locations
        shift_mask = np.random.random(n) < probability

        # Cumulative sum of shifts
        shifts = np.cumsum(np.random.choice([-1, 1], size=n) * amplitude * shift_mask)
        contaminated += shifts

        return contaminated

    def add_artifact_missing_data(
        self, data: np.ndarray, probability: Optional[float] = None
    ) -> np.ndarray:
        """
        Add missing data (NaN values) to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        probability : float, optional
            Probability of missing data at each point. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with missing values (NaN)
        """
        probability = probability or self.config.artifact_missing_probability

        contaminated = data.copy()
        n = len(data)

        # Generate missing data mask
        missing_mask = np.random.random(n) < probability
        contaminated[missing_mask] = np.nan

        return contaminated

    def add_noise_gaussian(
        self, data: np.ndarray, std: Optional[float] = None
    ) -> np.ndarray:
        """
        Add Gaussian noise to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        std : float, optional
            Standard deviation of noise. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with Gaussian noise added
        """
        std = std or self.config.noise_gaussian_std
        n = len(data)
        noise = np.random.normal(0, std, n)
        return data + noise

    def add_noise_colored(
        self, data: np.ndarray, power: Optional[float] = None
    ) -> np.ndarray:
        """
        Add colored (1/f^power) noise to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        power : float, optional
            Power law exponent. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with colored noise added
        """
        power = power or self.config.noise_colored_power
        n = len(data)

        # Generate colored noise using FFT
        freqs = np.fft.fftfreq(n)
        freqs[0] = 1e-10  # Avoid division by zero

        # Power spectrum
        power_spectrum = 1.0 / (np.abs(freqs) ** power)
        power_spectrum[0] = 0  # Zero mean

        # Generate noise
        phase = np.random.uniform(0, 2 * np.pi, n)
        noise_fft = np.sqrt(power_spectrum) * np.exp(1j * phase)
        noise = np.real(np.fft.ifft(noise_fft))

        # Normalize
        noise = noise / np.std(noise) * 0.1

        return data + noise

    def add_noise_impulsive(
        self,
        data: np.ndarray,
        probability: Optional[float] = None,
        amplitude: Optional[float] = None,
    ) -> np.ndarray:
        """
        Add impulsive noise to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        probability : float, optional
            Probability of impulsive noise at each point. If None, uses config value.
        amplitude : float, optional
            Amplitude of impulsive noise. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with impulsive noise added
        """
        probability = probability or self.config.noise_impulsive_probability
        amplitude = amplitude or self.config.noise_impulsive_amplitude

        contaminated = data.copy()
        n = len(data)

        # Generate impulsive noise locations
        impulsive_mask = np.random.random(n) < probability

        # Add impulsive noise with random signs
        impulsive_amplitudes = np.random.choice([-1, 1], size=n) * amplitude
        contaminated[impulsive_mask] += impulsive_amplitudes[impulsive_mask]

        return contaminated

    def add_sampling_irregular(
        self, data: np.ndarray, probability: Optional[float] = None
    ) -> np.ndarray:
        """
        Simulate irregular sampling by removing some data points.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        probability : float, optional
            Probability of irregular sampling. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with irregular sampling (some points removed)
        """
        probability = probability or self.config.sampling_irregular_probability

        contaminated = data.copy()
        n = len(data)

        # Generate irregular sampling mask
        irregular_mask = np.random.random(n) < probability
        contaminated[irregular_mask] = np.nan

        return contaminated

    def add_sampling_aliasing(
        self, data: np.ndarray, frequency: Optional[float] = None
    ) -> np.ndarray:
        """
        Add aliasing effects to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        frequency : float, optional
            Aliasing frequency. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with aliasing effects
        """
        frequency = frequency or self.config.sampling_aliasing_frequency
        n = len(data)

        # Generate aliasing signal
        t = np.arange(n)
        aliasing_signal = 0.1 * np.sin(2 * np.pi * frequency * t)

        return data + aliasing_signal

    def add_measurement_systematic(
        self, data: np.ndarray, bias: Optional[float] = None
    ) -> np.ndarray:
        """
        Add systematic measurement bias to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        bias : float, optional
            Systematic bias. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with systematic bias added
        """
        bias = bias or self.config.measurement_systematic_bias
        return data + bias

    def add_measurement_random(
        self, data: np.ndarray, std: Optional[float] = None
    ) -> np.ndarray:
        """
        Add random measurement errors to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        std : float, optional
            Standard deviation of measurement errors. If None, uses config value.

        Returns
        -------
        np.ndarray
            Data with random measurement errors added
        """
        std = std or self.config.measurement_random_std
        n = len(data)
        measurement_error = np.random.normal(0, std, n)
        return data + measurement_error

    def apply_contamination(
        self, data: np.ndarray, contamination_types: List[ContaminationType], **kwargs
    ) -> np.ndarray:
        """
        Apply multiple types of contamination to the data.

        Parameters
        ----------
        data : np.ndarray
            Input time series data
        contamination_types : List[ContaminationType]
            List of contamination types to apply
        **kwargs : dict
            Additional parameters for specific contamination types

        Returns
        -------
        np.ndarray
            Contaminated data
        """
        contaminated = data.copy()

        for cont_type in contamination_types:
            if cont_type == ContaminationType.TREND_LINEAR:
                slope = kwargs.get("slope", None)
                contaminated = self.add_trend_linear(contaminated, slope=slope)
            elif cont_type == ContaminationType.TREND_POLYNOMIAL:
                degree = kwargs.get("degree", None)
                contaminated = self.add_trend_polynomial(contaminated, degree=degree)
            elif cont_type == ContaminationType.TREND_EXPONENTIAL:
                rate = kwargs.get("rate", None)
                contaminated = self.add_trend_exponential(contaminated, rate=rate)
            elif cont_type == ContaminationType.TREND_SEASONAL:
                period = kwargs.get("period", None)
                amplitude = kwargs.get("amplitude", None)
                contaminated = self.add_trend_seasonal(
                    contaminated, period=period, amplitude=amplitude
                )
            elif cont_type == ContaminationType.ARTIFACT_SPIKES:
                probability = kwargs.get("probability", None)
                amplitude = kwargs.get("amplitude", None)
                contaminated = self.add_artifact_spikes(
                    contaminated, probability=probability, amplitude=amplitude
                )
            elif cont_type == ContaminationType.ARTIFACT_LEVEL_SHIFTS:
                probability = kwargs.get("probability", None)
                amplitude = kwargs.get("amplitude", None)
                contaminated = self.add_artifact_level_shifts(
                    contaminated, probability=probability, amplitude=amplitude
                )
            elif cont_type == ContaminationType.ARTIFACT_MISSING_DATA:
                probability = kwargs.get("probability", None)
                contaminated = self.add_artifact_missing_data(
                    contaminated, probability=probability
                )
            elif cont_type == ContaminationType.NOISE_GAUSSIAN:
                std = kwargs.get("std", None)
                contaminated = self.add_noise_gaussian(contaminated, std=std)
            elif cont_type == ContaminationType.NOISE_COLORED:
                power = kwargs.get("power", None)
                contaminated = self.add_noise_colored(contaminated, power=power)
            elif cont_type == ContaminationType.NOISE_IMPULSIVE:
                probability = kwargs.get("probability", None)
                amplitude = kwargs.get("amplitude", None)
                contaminated = self.add_noise_impulsive(
                    contaminated, probability=probability, amplitude=amplitude
                )
            elif cont_type == ContaminationType.SAMPLING_IRREGULAR:
                probability = kwargs.get("probability", None)
                contaminated = self.add_sampling_irregular(
                    contaminated, probability=probability
                )
            elif cont_type == ContaminationType.SAMPLING_ALIASING:
                frequency = kwargs.get("frequency", None)
                contaminated = self.add_sampling_aliasing(
                    contaminated, frequency=frequency
                )
            elif cont_type == ContaminationType.MEASUREMENT_SYSTEMATIC:
                bias = kwargs.get("bias", None)
                contaminated = self.add_measurement_systematic(contaminated, bias=bias)
            elif cont_type == ContaminationType.MEASUREMENT_RANDOM:
                std = kwargs.get("std", None)
                contaminated = self.add_measurement_random(contaminated, std=std)
            else:
                warnings.warn(f"Unknown contamination type: {cont_type}")

        return contaminated

    def get_contamination_info(
        self, contamination_types: List[ContaminationType]
    ) -> Dict[str, str]:
        """
        Get information about the applied contaminations.

        Parameters
        ----------
        contamination_types : List[ContaminationType]
            List of contamination types

        Returns
        -------
        Dict[str, str]
            Dictionary with contamination information
        """
        info = {}

        for cont_type in contamination_types:
            if cont_type.value.startswith("trend_"):
                info[cont_type.value] = (
                    f"Added {cont_type.value.replace('_', ' ')} trend"
                )
            elif cont_type.value.startswith("artifact_"):
                info[cont_type.value] = (
                    f"Added {cont_type.value.replace('_', ' ')} artifacts"
                )
            elif cont_type.value.startswith("noise_"):
                info[cont_type.value] = (
                    f"Added {cont_type.value.replace('_', ' ')} noise"
                )
            elif cont_type.value.startswith("sampling_"):
                info[cont_type.value] = (
                    f"Applied {cont_type.value.replace('_', ' ')} effects"
                )
            elif cont_type.value.startswith("measurement_"):
                info[cont_type.value] = (
                    f"Added {cont_type.value.replace('_', ' ')} errors"
                )

        return info
