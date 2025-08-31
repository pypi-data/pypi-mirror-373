"""
Numba-optimized Geweke-Porter-Hudak (GPH) Hurst parameter estimator.

This module implements the GPH estimator for the Hurst parameter using
log-periodogram regression with Numba JIT compilation.
"""

import numpy as np
from numba import jit, prange
from scipy import stats
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, cache=True)
def _get_window_numba(n, window_type):
    """Get Numba window function."""
    window = np.empty(n)

    if window_type == 0:  # boxcar
        for i in range(n):
            window[i] = 1.0
    elif window_type == 1:  # hann
        for i in range(n):
            window[i] = 0.5 * (1.0 - np.cos(2.0 * np.pi * i / (n - 1)))
    elif window_type == 2:  # hamming
        for i in range(n):
            window[i] = 0.54 - 0.46 * np.cos(2.0 * np.pi * i / (n - 1))
    elif window_type == 3:  # blackman
        for i in range(n):
            window[i] = (
                0.42
                - 0.5 * np.cos(2.0 * np.pi * i / (n - 1))
                + 0.08 * np.cos(4.0 * np.pi * i / (n - 1))
            )
    else:  # default to hann
        for i in range(n):
            window[i] = 0.5 * (1.0 - np.cos(2.0 * np.pi * i / (n - 1)))

    return window


@jit(nopython=True, cache=True)
def _dft_numba(data):
    """Compute Discrete Fourier Transform manually for Numba compatibility."""
    n = len(data)
    real_part = np.zeros(n)
    imag_part = np.zeros(n)

    for k in range(n):
        for j in range(n):
            angle = -2.0 * np.pi * k * j / n
            real_part[k] += data[j] * np.cos(angle)
            imag_part[k] += data[j] * np.sin(angle)

    return real_part, imag_part


@jit(nopython=True, cache=True)
def _compute_periodogram_numba(data, window_type):
    """Compute periodogram using Numba."""
    n = len(data)
    window = _get_window_numba(n, window_type)

    # Apply window
    windowed_data = np.empty(n)
    for i in range(n):
        windowed_data[i] = data[i] * window[i]

    # Compute FFT manually
    real_part, imag_part = _dft_numba(windowed_data)

    # Compute periodogram (only positive frequencies)
    n_pos = n // 2 + 1
    periodogram = np.empty(n_pos)
    for i in range(n_pos):
        periodogram[i] = real_part[i] ** 2 + imag_part[i] ** 2

    # Normalize
    window_sum = 0.0
    for i in range(n):
        window_sum += window[i] ** 2

    for i in range(n_pos):
        periodogram[i] = periodogram[i] / window_sum

    # Convert to density scaling
    for i in range(n_pos):
        periodogram[i] = periodogram[i] / (2.0 * np.pi)

    # Generate frequency array
    freqs = np.empty(n_pos)
    for i in range(n_pos):
        freqs[i] = i / (2.0 * (n_pos - 1))

    return freqs, periodogram


@jit(nopython=True, cache=True)
def _compute_welch_psd_numba(data, window_type, nperseg):
    """Compute Welch's PSD using Numba."""
    n = len(data)

    # Calculate overlap
    noverlap = nperseg // 2

    # Calculate number of segments
    n_segments = (n - noverlap) // (nperseg - noverlap)

    if n_segments < 1:
        # Fallback to periodogram
        return _compute_periodogram_numba(data, window_type)

    # Get window
    window = _get_window_numba(nperseg, window_type)

    # Initialize arrays for segments
    n_pos = nperseg // 2 + 1
    periodogram_sum = np.zeros(n_pos)

    # Process each segment
    for seg in range(n_segments):
        start = seg * (nperseg - noverlap)
        end = start + nperseg

        # Extract segment
        segment = np.empty(nperseg)
        for i in range(nperseg):
            segment[i] = data[start + i]

        # Apply window
        windowed_segment = np.empty(nperseg)
        for i in range(nperseg):
            windowed_segment[i] = segment[i] * window[i]

        # Compute FFT manually
        real_part, imag_part = _dft_numba(windowed_segment)

        # Add to periodogram sum
        for i in range(n_pos):
            periodogram_sum[i] += real_part[i] ** 2 + imag_part[i] ** 2

    # Average across segments
    psd = np.empty(n_pos)
    for i in range(n_pos):
        psd[i] = periodogram_sum[i] / n_segments

    # Normalize
    window_sum = 0.0
    for i in range(nperseg):
        window_sum += window[i] ** 2

    for i in range(n_pos):
        psd[i] = psd[i] / window_sum

    # Convert to density scaling
    for i in range(n_pos):
        psd[i] = psd[i] / (2.0 * np.pi)

    # Generate frequency array
    freqs = np.empty(n_pos)
    for i in range(n_pos):
        freqs[i] = i / (2.0 * (n_pos - 1))

    return freqs, psd


@jit(nopython=True, cache=True)
def _gph_regression_numba(freqs, psd, min_freq, max_freq, apply_bias_correction):
    """Perform GPH regression using Numba."""
    n = len(freqs)

    # Count valid points
    valid_count = 0
    for i in range(n):
        if freqs[i] >= min_freq and freqs[i] <= max_freq and psd[i] > 0:
            valid_count += 1

    if valid_count < 3:
        # Return default values if insufficient data
        # Create empty arrays with proper types for Numba
        empty_array = np.zeros(0, dtype=np.float64)
        return 0.5, 0.0, 0.0, 0.0, empty_array, empty_array

    # Extract valid points
    freqs_sel = np.empty(valid_count)
    psd_sel = np.empty(valid_count)

    idx = 0
    for i in range(n):
        if freqs[i] >= min_freq and freqs[i] <= max_freq and psd[i] > 0:
            freqs_sel[idx] = freqs[i]
            psd_sel[idx] = psd[i]
            idx += 1

    # Convert to angular frequencies
    omega = np.empty(valid_count)
    for i in range(valid_count):
        omega[i] = 2.0 * np.pi * freqs_sel[i]

    # GPH regressor: log(4*sin^2(ω/2))
    regressor = np.empty(valid_count)
    log_periodogram = np.empty(valid_count)

    for i in range(valid_count):
        regressor[i] = np.log(4.0 * np.sin(omega[i] / 2.0) ** 2)
        log_periodogram[i] = np.log(psd_sel[i])

    # Linear regression using Numba
    # Center the data
    regressor_mean = 0.0
    log_periodogram_mean = 0.0

    for i in range(valid_count):
        regressor_mean += regressor[i]
        log_periodogram_mean += log_periodogram[i]

    regressor_mean /= valid_count
    log_periodogram_mean /= valid_count

    # Compute slope
    numerator = 0.0
    denominator = 0.0

    for i in range(valid_count):
        reg_centered = regressor[i] - regressor_mean
        log_centered = log_periodogram[i] - log_periodogram_mean
        numerator += reg_centered * log_centered
        denominator += reg_centered**2

    if denominator == 0.0:
        slope = 0.0
    else:
        slope = numerator / denominator

    # Compute intercept
    intercept = log_periodogram_mean - slope * regressor_mean

    # Compute R-squared
    ss_res = 0.0
    ss_tot = 0.0

    for i in range(valid_count):
        y_pred = slope * regressor[i] + intercept
        ss_res += (log_periodogram[i] - y_pred) ** 2
        ss_tot += (log_periodogram[i] - log_periodogram_mean) ** 2

    if ss_tot == 0.0:
        r_squared = 0.0
    else:
        r_squared = 1.0 - (ss_res / ss_tot)

    d_parameter = -slope  # d = -slope

    # Apply bias correction if requested
    if apply_bias_correction:
        bias_correction = 0.5 * np.log(valid_count) / valid_count
        d_parameter += bias_correction

    # Convert to Hurst parameter: H = d + 0.5
    hurst = d_parameter + 0.5

    # Ensure Hurst parameter is in valid range
    if hurst < 0.01:
        hurst = 0.01
    elif hurst > 0.99:
        hurst = 0.99

    return hurst, d_parameter, intercept, r_squared, regressor, log_periodogram


class GPHEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Geweke-Porter-Hudak (GPH) Hurst parameter estimator.

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

    def estimate(self, data):
        """
        Estimate Hurst parameter using GPH method with Numba acceleration.

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
        data = np.asarray(data)
        n = len(data)

        if self.nperseg is None:
            self.nperseg = max(n // 8, 64)

        # Compute periodogram
        if self.use_welch:
            freqs, psd = _compute_welch_psd_numba(data, self.window_type, self.nperseg)
        else:
            freqs, psd = _compute_periodogram_numba(data, self.window_type)

        # Select frequency range for fitting
        nyquist = 0.5
        min_freq = self.min_freq_ratio * nyquist
        max_freq = self.max_freq_ratio * nyquist

        # Perform GPH regression
        hurst, d_parameter, intercept, r_squared, regressor, log_periodogram = (
            _gph_regression_numba(
                freqs, psd, min_freq, max_freq, self.apply_bias_correction
            )
        )

        self.results = {
            "hurst_parameter": float(hurst),
            "d_parameter": float(d_parameter),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "m": int(len(regressor)) if len(regressor) > 0 else 0,
            "log_regressor": regressor,
            "log_periodogram": log_periodogram,
            "frequency": freqs,
            "periodogram": psd,
        }
        return self.results
