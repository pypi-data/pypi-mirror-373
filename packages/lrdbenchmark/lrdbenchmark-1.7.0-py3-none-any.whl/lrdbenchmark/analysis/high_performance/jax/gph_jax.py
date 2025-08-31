"""
JAX-optimized Geweke-Porter-Hudak (GPH) Hurst parameter estimator.

This module implements the GPH estimator for the Hurst parameter using
log-periodogram regression with JAX acceleration.
"""

import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from models.estimators.base_estimator import BaseEstimator


class GPHEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Geweke-Porter-Hudak (GPH) Hurst parameter estimator.

    This estimator uses log-periodogram regression with the regressor
    log(4*sin^2(ω/2)) to estimate the fractional differencing parameter d,
    then converts to Hurst parameter as H = d + 0.5.

    Parameters
    ----------
    min_freq_ratio : float, optional (default=0.01)
        Minimum frequency ratio (relative to Nyquist) for fitting.
    max_freq_ratio : float, optional (default=0.1)
        Maximum frequency ratio (relative to Nyquist) for fitting.
    use_welch : bool, optional (default=True)
        Whether to use Welch's method for PSD estimation.
    window_type : int, optional (default=1)
        Window function type: 0=boxcar, 1=hann, 2=hamming, 3=blackman.
    nperseg : int, optional (default=None)
        Length of each segment for Welch's method. If None, uses n/8.
    apply_bias_correction : bool, optional (default=True)
        Whether to apply bias correction for finite sample effects.
    """

    def __init__(
        self,
        min_freq_ratio=0.01,
        max_freq_ratio=0.1,
        use_welch=True,
        window_type=1,
        nperseg=None,
        apply_bias_correction=True,
    ):
        super().__init__()
        self.min_freq_ratio = min_freq_ratio
        self.max_freq_ratio = max_freq_ratio
        self.use_welch = use_welch
        self.window_type = window_type
        self.nperseg = nperseg
        self.apply_bias_correction = apply_bias_correction
        self.results = {}
        self._validate_parameters()
        self._jit_functions()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not (0 < self.min_freq_ratio < self.max_freq_ratio < 0.5):
            raise ValueError(
                "Frequency ratios must satisfy: 0 < min_freq_ratio < max_freq_ratio < 0.5"
            )

        if self.nperseg is not None and self.nperseg < 2:
            raise ValueError("nperseg must be at least 2")

        if self.window_type not in [0, 1, 2, 3]:
            raise ValueError(
                "window_type must be 0 (boxcar), 1 (hann), 2 (hamming), or 3 (blackman)"
            )

    def _jit_functions(self):
        """JIT compile the core computation functions."""
        # Remove JIT from Welch PSD to handle dynamic nperseg
        # Remove JIT from GPH regression to handle dynamic boolean indexing
        self._compute_periodogram_jax = jit(self._compute_periodogram_jax)

    def _get_window_jax(self, n, window_type):
        """Get JAX window function."""
        if window_type == 0:  # boxcar
            return jnp.ones(n)
        elif window_type == 1:  # hann
            return jnp.hanning(n)
        elif window_type == 2:  # hamming
            return jnp.hamming(n)
        elif window_type == 3:  # blackman
            return jnp.blackman(n)
        else:
            return jnp.hanning(n)

    def _compute_periodogram_jax(self, data, window_type):
        """Compute periodogram using JAX."""
        n = len(data)
        window = self._get_window_jax(n, window_type)

        # Apply window
        windowed_data = data * window

        # Compute FFT
        fft_result = jnp.fft.fft(windowed_data)

        # Compute periodogram (only positive frequencies)
        n_pos = n // 2 + 1
        periodogram = jnp.abs(fft_result[:n_pos]) ** 2

        # Normalize
        window_sum = jnp.sum(window**2)
        periodogram = periodogram / window_sum

        # Convert to density scaling
        periodogram = periodogram / (2 * np.pi)

        # Generate frequency array
        freqs = jnp.linspace(0, 0.5, n_pos)

        return freqs, periodogram

    def _compute_welch_psd_jax(self, data, window_type, nperseg):
        """Compute Welch's PSD using JAX."""
        n = len(data)

        # Calculate overlap
        noverlap = nperseg // 2

        # Calculate number of segments
        n_segments = (n - noverlap) // (nperseg - noverlap)

        if n_segments < 1:
            # Fallback to periodogram
            return self._compute_periodogram_jax(data, window_type)

        # Reshape data into segments
        start_indices = jnp.arange(n_segments) * (nperseg - noverlap)
        segments = jnp.array([data[start : start + nperseg] for start in start_indices])

        # Get window
        window = self._get_window_jax(nperseg, window_type)

        # Apply window to all segments
        windowed_segments = segments * window

        # Compute FFT for all segments
        fft_segments = jnp.fft.fft(windowed_segments, axis=1)

        # Compute periodogram for all segments
        n_pos = nperseg // 2 + 1
        periodogram_segments = jnp.abs(fft_segments[:, :n_pos]) ** 2

        # Normalize
        window_sum = jnp.sum(window**2)
        periodogram_segments = periodogram_segments / window_sum

        # Average across segments
        psd = jnp.mean(periodogram_segments, axis=0)

        # Convert to density scaling
        psd = psd / (2 * np.pi)

        # Generate frequency array
        freqs = jnp.linspace(0, 0.5, n_pos)

        return freqs, psd

    def _gph_regression_jax(
        self, freqs, psd, min_freq, max_freq, apply_bias_correction
    ):
        """Perform GPH regression using JAX."""
        # Convert to numpy for easier handling
        freqs_np = np.array(freqs)
        psd_np = np.array(psd)

        # Select frequency range for fitting
        mask = (freqs_np >= min_freq) & (freqs_np <= max_freq)
        freqs_sel = freqs_np[mask]
        psd_sel = psd_np[mask]

        # Filter out zero/negative PSD values
        valid_mask = psd_sel > 0
        freqs_sel = freqs_sel[valid_mask]
        psd_sel = psd_sel[valid_mask]

        if len(freqs_sel) < 3:
            # Return default values if insufficient data
            return 0.5, 0.0, 0.0, 0.0, jnp.array([]), jnp.array([])

        # Convert back to JAX arrays
        freqs_sel = jnp.array(freqs_sel)
        psd_sel = jnp.array(psd_sel)

        # Convert to angular frequencies
        omega = 2 * jnp.pi * freqs_sel

        # GPH regressor: log(4*sin^2(ω/2))
        regressor = jnp.log(4 * jnp.sin(omega / 2) ** 2)
        log_periodogram = jnp.log(psd_sel)

        # Linear regression using JAX
        # Center the data
        regressor_mean = jnp.mean(regressor)
        log_periodogram_mean = jnp.mean(log_periodogram)

        regressor_centered = regressor - regressor_mean
        log_periodogram_centered = log_periodogram - log_periodogram_mean

        # Compute slope
        numerator = jnp.sum(regressor_centered * log_periodogram_centered)
        denominator = jnp.sum(regressor_centered**2)

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Compute intercept
        intercept = log_periodogram_mean - slope * regressor_mean

        # Compute R-squared
        y_pred = slope * regressor + intercept
        ss_res = jnp.sum((log_periodogram - y_pred) ** 2)
        ss_tot = jnp.sum((log_periodogram - log_periodogram_mean) ** 2)

        if ss_tot == 0:
            r_squared = 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)

        d_parameter = -slope  # d = -slope

        # Apply bias correction if requested
        if apply_bias_correction:
            m = len(freqs_sel)
            # Simple bias correction for finite sample effects
            bias_correction = 0.5 * jnp.log(m) / m
            d_parameter += bias_correction

        # Convert to Hurst parameter: H = d + 0.5
        hurst = d_parameter + 0.5

        # Ensure Hurst parameter is in valid range
        hurst = jnp.clip(hurst, 0.01, 0.99)

        return hurst, d_parameter, intercept, r_squared, regressor, log_periodogram

    def estimate(self, data):
        """
        Estimate Hurst parameter using GPH method with JAX acceleration.

        Parameters
        ----------
        data : array-like
            Time series data.

        Returns
        -------
        dict
            Dictionary containing:
            - hurst_parameter: Estimated Hurst parameter
            - d_parameter: Estimated fractional differencing parameter
            - intercept: Intercept of the linear fit
            - r_squared: R-squared value of the fit
            - m: Number of frequency points used in fitting
            - log_regressor: Log regressor values
            - log_periodogram: Log periodogram values
        """
        data = jnp.asarray(data)
        n = len(data)

        if self.nperseg is None:
            self.nperseg = max(n // 8, 64)

        # Compute periodogram
        if self.use_welch:
            freqs, psd = self._compute_welch_psd_jax(
                data, self.window_type, self.nperseg
            )
        else:
            freqs, psd = self._compute_periodogram_jax(data, self.window_type)

        # Select frequency range for fitting
        nyquist = 0.5
        min_freq = self.min_freq_ratio * nyquist
        max_freq = self.max_freq_ratio * nyquist

        # Perform GPH regression
        hurst, d_parameter, intercept, r_squared, regressor, log_periodogram = (
            self._gph_regression_jax(
                freqs, psd, min_freq, max_freq, self.apply_bias_correction
            )
        )

        # Convert to numpy for results
        self.results = {
            "hurst_parameter": float(hurst),
            "d_parameter": float(d_parameter),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "m": int(len(regressor)) if len(regressor) > 0 else 0,
            "log_regressor": np.array(regressor),
            "log_periodogram": np.array(log_periodogram),
            "frequency": np.array(freqs),
            "periodogram": np.array(psd),
        }
        return self.results
