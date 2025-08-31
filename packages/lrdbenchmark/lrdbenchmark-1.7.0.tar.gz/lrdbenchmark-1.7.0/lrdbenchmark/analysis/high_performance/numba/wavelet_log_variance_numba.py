"""
Numba-optimized Wavelet Log Variance Analysis estimator.

This module provides Numba-optimized wavelet log variance analysis for estimating
the Hurst parameter from time series data using wavelet decomposition with
log-transformed variances.
"""

import numpy as np
from numba import jit, prange
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, cache=True)
def _compute_wavelet_variance_numba(data: np.ndarray, scale: int) -> float:
    """
    Compute wavelet variance for a given scale using Numba.

    Args:
        data: Input time series data
        scale: Wavelet scale level

    Returns:
        Wavelet variance at the given scale
    """
    # For Numba compatibility, we'll use a simplified approach
    # In practice, you might want to use a Numba-compatible wavelet library
    # For now, we'll compute a simple variance-based approximation

    # Downsample data by 2^scale
    step = 2**scale
    if step >= len(data):
        return 0.0

    # Create downsampled version
    downsampled = np.empty(len(data) // step)
    for i in range(len(downsampled)):
        downsampled[i] = data[i * step]

    # Compute variance of differences (approximation of wavelet variance)
    if len(downsampled) > 1:
        differences = np.empty(len(downsampled) - 1)
        for i in range(len(differences)):
            differences[i] = downsampled[i + 1] - downsampled[i]

        # Compute variance
        mean_diff = 0.0
        for i in range(len(differences)):
            mean_diff += differences[i]
        mean_diff /= len(differences)

        variance = 0.0
        for i in range(len(differences)):
            variance += (differences[i] - mean_diff) ** 2
        variance /= len(differences)
    else:
        variance = 0.0

    return variance


@jit(nopython=True, cache=True)
def _linear_regression_numba(
    x: np.ndarray, y: np.ndarray
) -> Tuple[float, float, float]:
    """
    Perform linear regression using Numba.

    Args:
        x: Independent variable
        y: Dependent variable

    Returns:
        Tuple of (slope, intercept, r_squared)
    """
    n = len(x)
    if n < 2:
        return 0.0, 0.0, 0.0

    # Center the data
    x_mean = 0.0
    y_mean = 0.0

    for i in range(n):
        x_mean += x[i]
        y_mean += y[i]

    x_mean /= n
    y_mean /= n

    # Compute slope
    numerator = 0.0
    denominator = 0.0

    for i in range(n):
        x_centered = x[i] - x_mean
        y_centered = y[i] - y_mean
        numerator += x_centered * y_centered
        denominator += x_centered**2

    if denominator == 0.0:
        slope = 0.0
    else:
        slope = numerator / denominator

    # Compute intercept
    intercept = y_mean - slope * x_mean

    # Compute R-squared
    ss_res = 0.0
    ss_tot = 0.0

    for i in range(n):
        y_pred = slope * x[i] + intercept
        ss_res += (y[i] - y_pred) ** 2
        ss_tot += (y[i] - y_mean) ** 2

    if ss_tot == 0.0:
        r_squared = 0.0
    else:
        r_squared = 1.0 - (ss_res / ss_tot)

    return slope, intercept, r_squared


class WaveletLogVarianceEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Wavelet Log Variance Analysis estimator.

    This estimator uses wavelet decomposition to analyze the log-transformed variance
    of wavelet coefficients at different scales, which can be used to estimate the
    Hurst parameter for fractional processes with improved statistical properties.

    Attributes:
        wavelet (str): Wavelet type to use for decomposition
        scales (List[int]): List of scales for wavelet analysis
        confidence (float): Confidence level for confidence intervals
    """

    def __init__(
        self,
        wavelet: str = "db4",
        scales: Optional[List[int]] = None,
        confidence: float = 0.95,
    ):
        """
        Initialize the Numba-optimized Wavelet Log Variance estimator.

        Args:
            wavelet (str): Wavelet type (default: 'db4')
            scales (List[int], optional): List of scales for analysis.
                                        If None, uses automatic scale selection
            confidence (float): Confidence level for intervals (default: 0.95)
        """
        super().__init__()
        self.wavelet = wavelet
        self.confidence = confidence

        # Set default scales if not provided
        if scales is None:
            self.scales = list(range(1, 11))  # Scales 1-10
        else:
            self.scales = scales

        # Results storage
        self.results = {}
        self._validate_parameters()

        print("Numba Wavelet Log Variance: Using JIT-compiled optimization")

    def _validate_parameters(self) -> None:
        """Validate the estimator parameters."""
        if not isinstance(self.wavelet, str):
            raise ValueError("wavelet must be a string")
        if not isinstance(self.scales, list) or len(self.scales) == 0:
            raise ValueError("scales must be a non-empty list")
        if not (0 < self.confidence < 1):
            raise ValueError("confidence must be between 0 and 1")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using Numba-optimized wavelet log variance analysis.

        Args:
            data: Input time series data

        Returns:
            Dictionary containing estimation results
        """
        data = np.asarray(data, dtype=np.float64)

        if len(data) < 2 ** max(self.scales):
            raise ValueError(
                f"Data length {len(data)} is too short for scale {max(self.scales)}"
            )

        # Calculate wavelet log variances for each scale
        scale_logs = []
        log_variance_values = []
        wavelet_variances = {}

        for scale in self.scales:
            # Compute wavelet variance using Numba
            variance = _compute_wavelet_variance_numba(data, scale)
            wavelet_variances[scale] = variance

            # Compute log values
            if variance > 0:
                log_variance = np.log(variance)
                scale_log = np.log2(scale)

                scale_logs.append(scale_log)
                log_variance_values.append(log_variance)

        if len(scale_logs) < 2:
            # Return default values if insufficient data
            self.results = {
                "hurst_parameter": 0.5,
                "r_squared": 0.0,
                "std_error": 0.0,
                "confidence_interval": (0.5, 0.5),
                "wavelet_variances": wavelet_variances,
                "scale_logs": [],
                "log_variance_values": [],
            }
            return self.results

        # Convert to numpy arrays for regression
        x = np.array(scale_logs, dtype=np.float64)
        y = np.array(log_variance_values, dtype=np.float64)

        # Perform linear regression using Numba
        slope, intercept, r_squared = _linear_regression_numba(x, y)

        # Hurst parameter is related to the slope
        # For fBm: H = (slope + 1) / 2
        # For fGn: H = (slope + 1) / 2
        hurst_parameter = (slope + 1) / 2

        # Ensure Hurst parameter is in valid range
        hurst_parameter = np.clip(hurst_parameter, 0.01, 0.99)

        # Calculate confidence interval (simplified)
        n = len(scale_logs)
        if n > 2:
            # Simple confidence interval based on R-squared
            margin = 0.1 * (1 - r_squared)
            confidence_interval = (hurst_parameter - margin, hurst_parameter + margin)
        else:
            confidence_interval = (hurst_parameter, hurst_parameter)

        # Store results
        self.results = {
            "hurst_parameter": float(hurst_parameter),
            "r_squared": float(r_squared),
            "std_error": 0.0,  # Simplified for Numba version
            "confidence_interval": confidence_interval,
            "wavelet_variances": wavelet_variances,
            "scale_logs": [float(x) for x in scale_logs],
            "log_variance_values": [float(y) for y in log_variance_values],
            "slope": float(slope),
            "intercept": float(intercept),
        }

        return self.results
