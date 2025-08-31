"""
Numba-optimized Whittle-based Hurst parameter estimator.

This module provides a Numba JIT-compiled version of the Whittle estimator for improved
single-threaded performance on CPU.
"""

import numpy as np
from numba import jit, prange
from scipy import optimize
from typing import Dict, Any, Tuple
import sys
import os

# Add the project root to the path to import BaseEstimator
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, cache=True)
def _fgn_spectrum_numba(
    freqs: np.ndarray, hurst: float, scale: float = 1.0
) -> np.ndarray:
    """
    Compute fGn power spectrum using Numba.

    Parameters
    ----------
    freqs : np.ndarray
        Frequency array
    hurst : float
        Hurst parameter
    scale : float
        Scale parameter

    Returns
    -------
    np.ndarray
        Power spectrum
    """
    n = len(freqs)
    spectrum = np.zeros(n)

    for i in range(n):
        spectrum[i] = scale * np.abs(2 * np.sin(np.pi * freqs[i])) ** (2 * hurst - 2)

    return spectrum


@jit(nopython=True, cache=True)
def _local_whittle_likelihood_numba(
    params: np.ndarray, freqs: np.ndarray, psd: np.ndarray
) -> float:
    """
    Compute local Whittle likelihood using Numba.

    Parameters
    ----------
    params : np.ndarray
        Parameters [hurst, scale]
    freqs : np.ndarray
        Frequency array
    psd : np.ndarray
        Power spectral density

    Returns
    -------
    float
        Negative log-likelihood
    """
    hurst, scale = params

    # Check bounds
    if hurst <= 0 or hurst >= 1 or scale <= 0:
        return np.inf

    model_spectrum = _fgn_spectrum_numba(freqs, hurst, scale)

    # Local Whittle likelihood
    log_lik = 0.0
    for i in range(len(freqs)):
        log_lik += np.log(model_spectrum[i]) + psd[i] / model_spectrum[i]

    return log_lik


@jit(nopython=True, cache=True)
def _compute_welch_psd_numba(
    data: np.ndarray, window_type: int, nperseg: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Welch's PSD using Numba operations.

    Parameters
    ----------
    data : np.ndarray
        Input data
    window_type : int
        Window type (0=hann, 1=hamming, 2=blackman, 3=rectangular)
    nperseg : int
        Length of each segment

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Frequencies and PSD
    """
    n = len(data)

    # Ensure nperseg is not larger than data length
    nperseg = min(nperseg, n)

    # Calculate number of segments
    n_segments = n // nperseg

    # Truncate data to fit integer number of segments
    data = data[: n_segments * nperseg]

    # Create window
    window = np.zeros(nperseg)
    if window_type == 0:  # Hann
        for i in range(nperseg):
            window[i] = 0.5 * (1 - np.cos(2 * np.pi * i / (nperseg - 1)))
    elif window_type == 1:  # Hamming
        for i in range(nperseg):
            window[i] = 0.54 - 0.46 * np.cos(2 * np.pi * i / (nperseg - 1))
    elif window_type == 2:  # Blackman
        for i in range(nperseg):
            window[i] = (
                0.42
                - 0.5 * np.cos(2 * np.pi * i / (nperseg - 1))
                + 0.08 * np.cos(4 * np.pi * i / (nperseg - 1))
            )
    else:  # Rectangular
        for i in range(nperseg):
            window[i] = 1.0

    # Normalize window
    window_sum = 0.0
    for i in range(nperseg):
        window_sum += window[i] * window[i]
    window_norm = np.sqrt(window_sum / nperseg)
    for i in range(nperseg):
        window[i] /= window_norm

    # Compute PSD for each segment
    psd_segments = np.zeros((n_segments, nperseg))

    for seg in range(n_segments):
        start_idx = seg * nperseg
        end_idx = start_idx + nperseg
        segment = data[start_idx:end_idx]

        # Apply window
        windowed_segment = np.zeros(nperseg)
        for i in range(nperseg):
            windowed_segment[i] = segment[i] * window[i]

        # Compute FFT manually (simple DFT)
        fft_real = np.zeros(nperseg)
        fft_imag = np.zeros(nperseg)

        for k in range(nperseg):
            real_sum = 0.0
            imag_sum = 0.0
            for j in range(nperseg):
                angle = -2 * np.pi * k * j / nperseg
                real_sum += windowed_segment[j] * np.cos(angle)
                imag_sum += windowed_segment[j] * np.sin(angle)
            fft_real[k] = real_sum
            fft_imag[k] = imag_sum

        # Compute PSD
        for i in range(nperseg):
            psd_segments[seg, i] = (fft_real[i] ** 2 + fft_imag[i] ** 2) / nperseg

    # Average across segments
    psd_avg = np.zeros(nperseg)
    for i in range(nperseg):
        sum_val = 0.0
        for seg in range(n_segments):
            sum_val += psd_segments[seg, i]
        psd_avg[i] = sum_val / n_segments

    # Generate frequencies
    freqs = np.zeros(nperseg)
    for i in range(nperseg):
        freqs[i] = i / nperseg

    # Return only positive frequencies
    n_positive = nperseg // 2
    freqs_positive = np.zeros(n_positive)
    psd_positive = np.zeros(n_positive)

    for i in range(n_positive):
        freqs_positive[i] = freqs[i + 1]  # Skip DC component
        psd_positive[i] = psd_avg[i + 1]

    return freqs_positive, psd_positive


@jit(nopython=True, cache=True)
def _compute_periodogram_numba(
    data: np.ndarray, window_type: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute periodogram using Numba operations.

    Parameters
    ----------
    data : np.ndarray
        Input data
    window_type : int
        Window type (0=hann, 1=hamming, 2=blackman, 3=rectangular)

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Frequencies and PSD
    """
    n = len(data)

    # Create window
    window = np.zeros(n)
    if window_type == 0:  # Hann
        for i in range(n):
            window[i] = 0.5 * (1 - np.cos(2 * np.pi * i / (n - 1)))
    elif window_type == 1:  # Hamming
        for i in range(n):
            window[i] = 0.54 - 0.46 * np.cos(2 * np.pi * i / (n - 1))
    elif window_type == 2:  # Blackman
        for i in range(n):
            window[i] = (
                0.42
                - 0.5 * np.cos(2 * np.pi * i / (n - 1))
                + 0.08 * np.cos(4 * np.pi * i / (n - 1))
            )
    else:  # Rectangular
        for i in range(n):
            window[i] = 1.0

    # Apply window
    windowed_data = np.zeros(n)
    for i in range(n):
        windowed_data[i] = data[i] * window[i]

    # Compute FFT manually (simple DFT)
    fft_real = np.zeros(n)
    fft_imag = np.zeros(n)

    for k in range(n):
        real_sum = 0.0
        imag_sum = 0.0
        for j in range(n):
            angle = -2 * np.pi * k * j / n
            real_sum += windowed_data[j] * np.cos(angle)
            imag_sum += windowed_data[j] * np.sin(angle)
        fft_real[k] = real_sum
        fft_imag[k] = imag_sum

    # Compute PSD
    psd = np.zeros(n)
    for i in range(n):
        psd[i] = (fft_real[i] ** 2 + fft_imag[i] ** 2) / n

    # Generate frequencies
    freqs = np.zeros(n)
    for i in range(n):
        freqs[i] = i / n

    # Return only positive frequencies
    n_positive = n // 2
    freqs_positive = np.zeros(n_positive)
    psd_positive = np.zeros(n_positive)

    for i in range(n_positive):
        freqs_positive[i] = freqs[i + 1]  # Skip DC component
        psd_positive[i] = psd[i + 1]

    return freqs_positive, psd_positive


class WhittleEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Whittle-based Hurst parameter estimator.

    This version uses Numba JIT compilation for improved single-threaded performance.
    It maintains the same interface as the original Whittle estimator but with
    significant performance improvements, especially for large datasets.

    Parameters
    ----------
    min_freq_ratio : float, optional (default=0.01)
        Minimum frequency ratio (relative to Nyquist) for fitting.
    max_freq_ratio : float, optional (default=0.1)
        Maximum frequency ratio (relative to Nyquist) for fitting.
    use_local_whittle : bool, optional (default=True)
        Whether to use local Whittle estimation (more robust).
    use_welch : bool, optional (default=True)
        Whether to use Welch's method for PSD estimation.
    window : str, optional (default='hann')
        Window function for Welch's method.
    nperseg : int, optional (default=None)
        Length of each segment for Welch's method. If None, uses n/8.
    """

    def __init__(
        self,
        min_freq_ratio=0.01,
        max_freq_ratio=0.1,
        use_local_whittle=True,
        use_welch=True,
        window="hann",
        nperseg=None,
    ):
        """
        Initialize the Numba-optimized Whittle estimator.

        Parameters
        ----------
        min_freq_ratio : float, optional
            Minimum frequency ratio (relative to Nyquist) for fitting.
        max_freq_ratio : float, optional
            Maximum frequency ratio (relative to Nyquist) for fitting.
        use_local_whittle : bool, optional
            Whether to use local Whittle estimation (more robust).
        use_welch : bool, optional
            Whether to use Welch's method for PSD estimation.
        window : str, optional
            Window function for Welch's method.
        nperseg : int, optional
            Length of each segment for Welch's method. If None, uses n/8.
        """
        super().__init__()
        self.min_freq_ratio = min_freq_ratio
        self.max_freq_ratio = max_freq_ratio
        self.use_local_whittle = use_local_whittle
        self.use_welch = use_welch
        self.window = window
        self.nperseg = nperseg
        self.results = {}

        print("Numba Whittle: Using JIT-compiled optimization")

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not (0 < self.min_freq_ratio < self.max_freq_ratio < 0.5):
            raise ValueError(
                "Frequency ratios must satisfy: 0 < min_freq_ratio < max_freq_ratio < 0.5"
            )

        if self.nperseg is not None and self.nperseg < 2:
            raise ValueError("nperseg must be at least 2")

    def _get_window_type(self, window_name: str) -> int:
        """Convert window name to integer type for Numba."""
        if window_name == "hann":
            return 0
        elif window_name == "hamming":
            return 1
        elif window_name == "blackman":
            return 2
        else:
            return 3  # rectangular

    def estimate(self, data):
        """
        Estimate Hurst parameter using Numba-optimized Whittle likelihood.

        Parameters
        ----------
        data : array-like
            Time series data.

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        data = np.asarray(data, dtype=np.float64)
        n = len(data)

        if self.nperseg is None:
            self.nperseg = max(n // 8, 64)

        # Convert window name to type
        window_type = self._get_window_type(self.window)

        # Compute periodogram using Numba
        if self.use_welch:
            freqs, psd = _compute_welch_psd_numba(data, window_type, self.nperseg)
        else:
            freqs, psd = _compute_periodogram_numba(data, window_type)

        # Select frequency range for fitting
        nyquist = 0.5
        min_freq = self.min_freq_ratio * nyquist
        max_freq = self.max_freq_ratio * nyquist

        mask = (freqs >= min_freq) & (freqs <= max_freq)
        freqs_sel = freqs[mask]
        psd_sel = psd[mask]

        if len(freqs_sel) < 3:
            raise ValueError("Insufficient frequency points for fitting")

        # Filter out zero/negative PSD values
        valid_mask = psd_sel > 0
        freqs_sel = freqs_sel[valid_mask]
        psd_sel = psd_sel[valid_mask]

        if len(freqs_sel) < 3:
            raise ValueError("Insufficient valid PSD points for fitting")

        # Estimate using scipy optimization with Numba likelihood
        hurst, scale, log_lik = self._whittle_estimate_numba(freqs_sel, psd_sel)

        # Compute R-squared for the fit
        log_model = np.log(_fgn_spectrum_numba(freqs_sel, hurst, scale))
        log_periodogram = np.log(psd_sel)

        # Use numpy's polyfit for regression
        coeffs = np.polyfit(log_model, log_periodogram, 1)
        slope = coeffs[0]
        intercept = coeffs[1]

        # Calculate R-squared
        y_pred = slope * log_model + intercept
        ss_res = np.sum((log_periodogram - y_pred) ** 2)
        ss_tot = np.sum((log_periodogram - np.mean(log_periodogram)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        self.results = {
            "hurst_parameter": float(hurst),
            "d_parameter": float(hurst - 0.5),  # d = H - 0.5 for fGn
            "scale_parameter": float(scale),
            "log_likelihood": float(log_lik),
            "r_squared": float(r_squared),
            "m": int(len(freqs_sel)),
            "log_model": log_model.tolist(),
            "log_periodogram": log_periodogram.tolist(),
            "frequency": freqs_sel.tolist(),
            "periodogram": psd_sel.tolist(),
            "optimization": "Numba",
        }
        return self.results

    def _whittle_estimate_numba(
        self, freqs: np.ndarray, psd: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Estimate using Numba-optimized Whittle likelihood.

        Parameters
        ----------
        freqs : np.ndarray
            Frequency array
        psd : np.ndarray
            Power spectral density

        Returns
        -------
        Tuple[float, float, float]
            hurst, scale, log_likelihood
        """
        # Initial guess
        x0 = np.array([0.5, np.mean(psd)])

        # Define bounds
        bounds = [(0.01, 0.99), (1e-6, None)]

        # Optimize using scipy with Numba likelihood function
        result = optimize.minimize(
            lambda params: _local_whittle_likelihood_numba(params, freqs, psd),
            x0,
            method="L-BFGS-B",
            bounds=bounds,
        )

        if result.success:
            hurst, scale = result.x
            log_lik = -result.fun
        else:
            # Fallback to simple regression
            hurst, scale, log_lik = self._fallback_estimate_numba(freqs, psd)

        return float(hurst), float(scale), float(log_lik)

    def _fallback_estimate_numba(
        self, freqs: np.ndarray, psd: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Fallback estimation using simple regression.

        Parameters
        ----------
        freqs : np.ndarray
            Frequency array
        psd : np.ndarray
            Power spectral density

        Returns
        -------
        Tuple[float, float, float]
            hurst, scale, log_likelihood
        """
        # Simple regression-based estimation
        log_freqs = np.log(freqs)
        log_psd = np.log(psd)

        # Linear regression
        coeffs = np.polyfit(log_freqs, log_psd, 1)
        slope = coeffs[0]
        intercept = coeffs[1]

        # Convert slope to Hurst parameter
        hurst = 0.5 - slope / 2

        # Ensure bounds
        hurst = np.clip(hurst, 0.01, 0.99)

        # Estimate scale
        scale = np.exp(intercept)

        # Compute log-likelihood
        model_spectrum = _fgn_spectrum_numba(freqs, hurst, scale)
        log_lik = np.sum(np.log(model_spectrum) + psd / model_spectrum)

        return float(hurst), float(scale), float(log_lik)

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for estimated parameters.

        Parameters
        ----------
        confidence_level : float, optional
            Confidence level (default: 0.95)

        Returns
        -------
        dict
            Dictionary containing confidence intervals
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # For Whittle estimation, we can use the Fisher information matrix
        # For now, return simple confidence intervals based on standard errors
        H = self.results["hurst_parameter"]
        m = self.results["m"]

        # Approximate standard error (simplified)
        std_error = 1.0 / np.sqrt(m)

        # Use normal approximation
        z_score = 1.96  # 95% confidence for normal distribution
        margin_of_error = z_score * std_error

        ci_lower = H - margin_of_error
        ci_upper = H + margin_of_error

        return {"hurst_parameter": (float(ci_lower), float(ci_upper))}

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the estimation.

        Returns
        -------
        dict
            Dictionary containing quality metrics
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        return {
            "r_squared": self.results["r_squared"],
            "log_likelihood": self.results["log_likelihood"],
            "m": self.results["m"],
            "optimization": self.results["optimization"],
        }

    def plot_spectrum(self, save_path: str = None, show: bool = True) -> None:
        """
        Plot the spectrum and model fit.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot (default: None)
        show : bool, optional
            Whether to display the plot (default: True)
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        # Switch to non-interactive backend for CI compatibility
        plt.switch_backend("Agg")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot periodogram
        ax.scatter(
            self.results["frequency"],
            self.results["periodogram"],
            alpha=0.6,
            label="Periodogram",
            s=20,
        )

        # Plot model spectrum
        freqs = np.array(self.results["frequency"])
        hurst = self.results["hurst_parameter"]
        scale = self.results["scale_parameter"]
        model_spectrum = scale * np.abs(2 * np.sin(np.pi * freqs)) ** (2 * hurst - 2)

        ax.plot(
            freqs, model_spectrum, "r-", linewidth=2, label=f"Model (H = {hurst:.3f})"
        )

        ax.set_xlabel("Frequency")
        ax.set_ylabel("Power Spectral Density")
        ax.set_title(
            f'Whittle Spectrum (Numba Optimized)\nH = {hurst:.3f}, R² = {self.results["r_squared"]:.3f}'
        )
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_yscale("log")
        ax.set_xscale("log")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        if show:
            plt.show()

        plt.close(fig)
