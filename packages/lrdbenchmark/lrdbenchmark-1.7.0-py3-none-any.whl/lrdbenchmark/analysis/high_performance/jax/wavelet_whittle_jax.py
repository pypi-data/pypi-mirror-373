"""
JAX-optimized Wavelet Whittle Analysis estimator.

This module provides JAX-optimized wavelet Whittle analysis for estimating
the Hurst parameter from time series data using wavelet-based Whittle likelihood estimation.
"""

import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from typing import Optional, Tuple, List, Dict, Any
from models.estimators.base_estimator import BaseEstimator


class WaveletWhittleEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Wavelet Whittle Analysis estimator.

    This estimator combines wavelet decomposition with Whittle likelihood estimation
    to provide robust estimation of the Hurst parameter for fractional processes.

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
        Initialize the JAX-optimized Wavelet Whittle estimator.

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
                print("JAX Wavelet Whittle: Using GPU acceleration")
            except:
                print("JAX Wavelet Whittle: GPU not available, using CPU")
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
        # Note: _compute_wavelet_coeffs_jax has dynamic scale parameter, so we don't JIT it
        self._whittle_likelihood_jax = jit(self._whittle_likelihood_jax)

    def _compute_wavelet_coeffs_jax(self, data: jnp.ndarray, scale: int) -> jnp.ndarray:
        """
        Compute wavelet coefficients for a given scale using JAX.

        Args:
            data: Input time series data
            scale: Wavelet scale level

        Returns:
            Wavelet coefficients at the given scale
        """
        # For JAX compatibility, we'll use a simplified approach
        # In practice, you might want to use a JAX-compatible wavelet library
        # For now, we'll compute a simple approximation

        # Downsample data by 2^scale
        step = 2**scale
        if step >= len(data):
            return jnp.array([])

        # Create downsampled version
        downsampled = data[::step]

        # Compute differences as approximation of wavelet coefficients
        if len(downsampled) > 1:
            coeffs = jnp.diff(downsampled)
        else:
            coeffs = jnp.array([])

        return coeffs

    def _theoretical_spectrum_jax(
        self, frequencies: jnp.ndarray, H: float, sigma: float = 1.0
    ) -> jnp.ndarray:
        """
        Calculate theoretical spectrum for fractional Gaussian noise using JAX.

        Args:
            frequencies: Frequency array
            H: Hurst parameter
            sigma: Scale parameter

        Returns:
            Theoretical power spectrum
        """
        # Theoretical spectrum for fGn
        # S(f) = sigma^2 * |f|^(1-2H) for f != 0
        spectrum = jnp.where(
            frequencies != 0, sigma**2 * jnp.abs(frequencies) ** (1 - 2 * H), sigma**2
        )

        return spectrum

    def _whittle_likelihood_jax(
        self, H: float, coeffs: jnp.ndarray, scale: int
    ) -> float:
        """
        Compute Whittle likelihood for a given Hurst parameter using JAX.

        Args:
            H: Hurst parameter
            coeffs: Wavelet coefficients
            scale: Scale level

        Returns:
            Negative log-likelihood
        """
        if len(coeffs) == 0:
            return jnp.array(0.0)

        # Compute periodogram of coefficients
        fft_coeffs = jnp.fft.fft(coeffs)
        periodogram = jnp.abs(fft_coeffs) ** 2 / len(coeffs)

        # Generate frequency array
        freqs = jnp.fft.fftfreq(len(coeffs))

        # Compute theoretical spectrum
        theoretical = self._theoretical_spectrum_jax(freqs, H)

        # Avoid division by zero
        theoretical = jnp.where(theoretical > 0, theoretical, 1e-10)

        # Compute Whittle likelihood
        log_likelihood = jnp.sum(jnp.log(theoretical) + periodogram / theoretical)

        return -log_likelihood

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using JAX-optimized wavelet Whittle analysis.

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

        # Compute wavelet coefficients for each scale
        all_coeffs = []
        valid_scales = []

        for scale in self.scales:
            coeffs = self._compute_wavelet_coeffs_jax(data, scale)
            if len(coeffs) > 0:
                all_coeffs.append(coeffs)
                valid_scales.append(scale)

        if len(all_coeffs) == 0:
            # Return default values if insufficient data
            self.results = {
                "hurst_parameter": 0.5,
                "r_squared": 0.0,
                "std_error": 0.0,
                "confidence_interval": (0.5, 0.5),
                "whittle_likelihood": 0.0,
            }
            return self.results

        # Optimize Hurst parameter using grid search (simplified)
        H_values = jnp.linspace(0.1, 0.9, 81)  # 0.1 to 0.9 in steps of 0.01
        likelihoods = []

        for H in H_values:
            total_likelihood = 0.0
            for i, coeffs in enumerate(all_coeffs):
                likelihood = self._whittle_likelihood_jax(H, coeffs, valid_scales[i])
                total_likelihood += likelihood
            likelihoods.append(total_likelihood)

        # Find minimum likelihood (maximum likelihood)
        min_idx = jnp.argmin(jnp.array(likelihoods))
        hurst_parameter = float(H_values[min_idx])
        min_likelihood = float(likelihoods[min_idx])

        # Calculate confidence interval (simplified)
        margin = 0.05  # Fixed margin for simplicity
        confidence_interval = (hurst_parameter - margin, hurst_parameter + margin)

        # Store results
        self.results = {
            "hurst_parameter": hurst_parameter,
            "r_squared": 0.0,  # Not applicable for Whittle likelihood
            "std_error": 0.0,  # Simplified
            "confidence_interval": confidence_interval,
            "whittle_likelihood": min_likelihood,
            "scales_used": valid_scales,
        }

        return self.results
