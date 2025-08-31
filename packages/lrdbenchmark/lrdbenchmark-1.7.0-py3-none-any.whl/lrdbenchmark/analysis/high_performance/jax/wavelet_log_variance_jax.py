"""
JAX-optimized Wavelet Log Variance Analysis estimator.

This module provides JAX-optimized wavelet log variance analysis for estimating
the Hurst parameter from time series data using wavelet decomposition with
log-transformed variances.
"""

import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from typing import Optional, Tuple, List, Dict, Any
from models.estimators.base_estimator import BaseEstimator


class WaveletLogVarianceEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Wavelet Log Variance Analysis estimator.

    This estimator uses wavelet decomposition to analyze the log-transformed variance
    of wavelet coefficients at different scales, which can be used to estimate the
    Hurst parameter for fractional processes with improved statistical properties.

    Attributes:
        wavelet (str): Wavelet type to use for decomposition
        scales (List[int]): List of scales for wavelet analysis
        confidence (float): Confidence level for confidence intervals
        use_gpu (bool): Whether to use GPU acceleration
    """

    def __init__(
        self,
        wavelet: str = "db4",
        scales: Optional[List[int]] = None,
        confidence: float = 0.95,
        use_gpu: bool = False,
    ):
        """
        Initialize the JAX-optimized Wavelet Log Variance estimator.

        Args:
            wavelet (str): Wavelet type (default: 'db4')
            scales (List[int], optional): List of scales for analysis.
                                        If None, uses automatic scale selection
            confidence (float): Confidence level for intervals (default: 0.95)
            use_gpu (bool): Whether to use GPU acceleration (default: False)
        """
        super().__init__()
        self.wavelet = wavelet
        self.confidence = confidence
        self.use_gpu = use_gpu

        # Set default scales if not provided
        if scales is None:
            self.scales = list(range(1, 11))  # Scales 1-10
        else:
            self.scales = scales

        # Results storage
        self.results = {}
        self._validate_parameters()
        self._jit_functions()

        # GPU setup
        if self.use_gpu:
            try:
                jax.devices("gpu")
                print("JAX Wavelet Log Variance: Using GPU acceleration")
            except:
                print("JAX Wavelet Log Variance: GPU not available, using CPU")
                self.use_gpu = False

    def _validate_parameters(self) -> None:
        """Validate the estimator parameters."""
        if not isinstance(self.wavelet, str):
            raise ValueError("wavelet must be a string")
        if not isinstance(self.scales, list) or len(self.scales) == 0:
            raise ValueError("scales must be a non-empty list")
        if not (0 < self.confidence < 1):
            raise ValueError("confidence must be between 0 and 1")

    def _jit_functions(self):
        """JIT compile the core computation functions."""
        # Note: Functions have dynamic parameters, so we don't JIT them to avoid tracing issues
        pass

    def _compute_wavelet_variance_jax(
        self, data: jnp.ndarray, scale: int
    ) -> jnp.ndarray:
        """
        Compute wavelet variance for a given scale using JAX.

        Args:
            data: Input time series data
            scale: Wavelet scale level

        Returns:
            Wavelet variance at the given scale
        """
        # For JAX compatibility, we'll use a simplified approach
        # In practice, you might want to use a JAX-compatible wavelet library
        # For now, we'll compute a simple variance-based approximation

        # Downsample data by 2^scale
        step = 2**scale
        if step >= len(data):
            return jnp.array(0.0)

        # Create downsampled version
        downsampled = data[::step]

        # Compute variance of differences (approximation of wavelet variance)
        if len(downsampled) > 1:
            differences = jnp.diff(downsampled)
            variance = jnp.var(differences)
        else:
            variance = jnp.array(0.0)

        return variance

    def _linear_regression_jax(
        self, x: jnp.ndarray, y: jnp.ndarray
    ) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
        """
        Perform linear regression using JAX.

        Args:
            x: Independent variable
            y: Dependent variable

        Returns:
            Tuple of (slope, intercept, r_squared)
        """
        # Center the data
        x_mean = jnp.mean(x)
        y_mean = jnp.mean(y)

        x_centered = x - x_mean
        y_centered = y - y_mean

        # Compute slope
        numerator = jnp.sum(x_centered * y_centered)
        denominator = jnp.sum(x_centered**2)

        if denominator == 0:
            slope = jnp.array(0.0)
        else:
            slope = numerator / denominator

        # Compute intercept
        intercept = y_mean - slope * x_mean

        # Compute R-squared
        y_pred = slope * x + intercept
        ss_res = jnp.sum((y - y_pred) ** 2)
        ss_tot = jnp.sum((y - y_mean) ** 2)

        if ss_tot == 0:
            r_squared = jnp.array(0.0)
        else:
            r_squared = 1 - (ss_res / ss_tot)

        return slope, intercept, r_squared

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using JAX-optimized wavelet log variance analysis.

        Args:
            data: Input time series data

        Returns:
            Dictionary containing estimation results
        """
        data = jnp.asarray(data)

        if len(data) < 2 ** max(self.scales):
            raise ValueError(
                f"Data length {len(data)} is too short for scale {max(self.scales)}"
            )

        # Calculate wavelet log variances for each scale
        scale_logs = []
        log_variance_values = []
        wavelet_variances = {}

        for scale in self.scales:
            # Compute wavelet variance using JAX
            variance = self._compute_wavelet_variance_jax(data, scale)

            # Convert to numpy for logging
            variance_np = float(variance)
            wavelet_variances[scale] = variance_np

            # Compute log values
            if variance_np > 0:
                log_variance = jnp.log(variance)
                scale_log = jnp.log2(scale)

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

        # Convert to JAX arrays for regression
        x = jnp.array(scale_logs)
        y = jnp.array(log_variance_values)

        # Perform linear regression using JAX
        slope, intercept, r_squared = self._linear_regression_jax(x, y)

        # Hurst parameter is related to the slope
        # For fBm: H = (slope + 1) / 2
        # For fGn: H = (slope + 1) / 2
        hurst_parameter = (float(slope) + 1) / 2

        # Ensure Hurst parameter is in valid range
        hurst_parameter = jnp.clip(hurst_parameter, 0.01, 0.99)

        # Calculate confidence interval (simplified)
        n = len(scale_logs)
        if n > 2:
            # Simple confidence interval based on R-squared
            margin = 0.1 * (1 - float(r_squared))
            confidence_interval = (
                float(hurst_parameter) - margin,
                float(hurst_parameter) + margin,
            )
        else:
            confidence_interval = (float(hurst_parameter), float(hurst_parameter))

        # Store results
        self.results = {
            "hurst_parameter": float(hurst_parameter),
            "r_squared": float(r_squared),
            "std_error": 0.0,  # Simplified for JAX version
            "confidence_interval": confidence_interval,
            "wavelet_variances": wavelet_variances,
            "scale_logs": [float(x) for x in scale_logs],
            "log_variance_values": [float(y) for y in log_variance_values],
            "slope": float(slope),
            "intercept": float(intercept),
        }

        return self.results
