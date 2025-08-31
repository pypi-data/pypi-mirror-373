import numpy as np
from numba import jit, prange
from scipy import stats, signal
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, cache=True)
def _compute_periodogram_numba(
    data: np.ndarray, window_type: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute periodogram using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    window_type : int
        Window type: 0=hann, 1=hamming, 2=blackman, 3=rectangular.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Frequencies and power spectral density.
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

    # Compute FFT
    fft_real = np.zeros(n)
    fft_imag = np.zeros(n)

    # Simple FFT implementation using direct computation
    for k in range(n):
        real_sum = 0.0
        imag_sum = 0.0
        for j in range(n):
            angle = -2 * np.pi * k * j / n
            real_sum += windowed_data[j] * np.cos(angle)
            imag_sum += windowed_data[j] * np.sin(angle)
        fft_real[k] = real_sum
        fft_imag[k] = imag_sum

    # Compute power spectral density
    psd = np.zeros(n)
    for i in range(n):
        psd[i] = (fft_real[i] ** 2 + fft_imag[i] ** 2) / n

    # Generate frequencies
    freqs = np.zeros(n)
    for i in range(n):
        freqs[i] = i / n

    # Take only positive frequencies up to Nyquist
    n_half = n // 2
    freqs_positive = np.zeros(n_half)
    psd_positive = np.zeros(n_half)

    for i in range(n_half):
        freqs_positive[i] = freqs[i]
        psd_positive[i] = psd[i]

    return freqs_positive, psd_positive


@jit(nopython=True, cache=True)
def _compute_welch_psd_numba(
    data: np.ndarray, nperseg: int, window_type: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Welch's PSD estimate using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    nperseg : int
        Length of each segment.
    window_type : int
        Window type: 0=hann, 1=hamming, 2=blackman, 3=rectangular.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Frequencies and power spectral density.
    """
    n = len(data)
    n_segments = n // nperseg

    if n_segments == 0:
        return _compute_periodogram_numba(data, window_type)

    # Create window for segments
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
        window_sum += window[i] ** 2
    window_norm = np.sqrt(window_sum / nperseg)
    for i in range(nperseg):
        window[i] /= window_norm

    # Compute PSD for each segment
    n_half = nperseg // 2
    psd_sum = np.zeros(n_half)

    for seg in range(n_segments):
        start_idx = seg * nperseg
        end_idx = start_idx + nperseg

        # Extract segment and apply window
        segment = np.zeros(nperseg)
        for i in range(nperseg):
            segment[i] = data[start_idx + i] * window[i]

        # Compute FFT for this segment
        fft_real = np.zeros(nperseg)
        fft_imag = np.zeros(nperseg)

        for k in range(nperseg):
            real_sum = 0.0
            imag_sum = 0.0
            for j in range(nperseg):
                angle = -2 * np.pi * k * j / nperseg
                real_sum += segment[j] * np.cos(angle)
                imag_sum += segment[j] * np.sin(angle)
            fft_real[k] = real_sum
            fft_imag[k] = imag_sum

        # Add to sum
        for i in range(n_half):
            psd_sum[i] += (fft_real[i] ** 2 + fft_imag[i] ** 2) / nperseg

    # Average across segments
    psd_avg = np.zeros(n_half)
    for i in range(n_half):
        psd_avg[i] = psd_sum[i] / n_segments

    # Generate frequencies
    freqs = np.zeros(n_half)
    for i in range(n_half):
        freqs[i] = i / nperseg

    return freqs, psd_avg


@jit(nopython=True, cache=True)
def _fit_power_law_numba(
    log_freqs: np.ndarray, log_psd: np.ndarray
) -> Tuple[float, float, float]:
    """
    Fit power law using Numba JIT compilation.

    Parameters
    ----------
    log_freqs : np.ndarray
        Log frequencies.
    log_psd : np.ndarray
        Log power spectral density.

    Returns
    -------
    Tuple[float, float, float]
        Slope, intercept, and R-squared.
    """
    n = len(log_freqs)

    # Compute means
    mean_x = 0.0
    mean_y = 0.0
    for i in range(n):
        mean_x += log_freqs[i]
        mean_y += log_psd[i]
    mean_x /= n
    mean_y /= n

    # Compute slope and intercept
    numerator = 0.0
    denominator = 0.0
    for i in range(n):
        numerator += (log_freqs[i] - mean_x) * (log_psd[i] - mean_y)
        denominator += (log_freqs[i] - mean_x) ** 2

    if denominator == 0:
        return 0.0, mean_y, 0.0

    slope = numerator / denominator
    intercept = mean_y - slope * mean_x

    # Compute R-squared
    ss_res = 0.0
    ss_tot = 0.0
    for i in range(n):
        y_pred = slope * log_freqs[i] + intercept
        ss_res += (log_psd[i] - y_pred) ** 2
        ss_tot += (log_psd[i] - mean_y) ** 2

    if ss_tot == 0:
        r_squared = 0.0
    else:
        r_squared = 1 - ss_res / ss_tot

    return slope, intercept, r_squared


class PeriodogramEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Periodogram estimator for Hurst parameter.

    This implementation uses Numba JIT compilation for significant CPU performance
    improvements, especially for large datasets.

    Parameters
    ----------
    min_freq_ratio : float, default=0.01
        Minimum frequency ratio (relative to Nyquist) for fitting.
    max_freq_ratio : float, default=0.1
        Maximum frequency ratio (relative to Nyquist) for fitting.
    use_welch : bool, default=True
        Whether to use Welch's method for PSD estimation.
    window : str, default='hann'
        Window function for PSD estimation.
    nperseg : int, optional
        Length of each segment for Welch's method. If None, uses n/8.
    """

    def __init__(
        self,
        min_freq_ratio: float = 0.01,
        max_freq_ratio: float = 0.1,
        use_welch: bool = True,
        window: str = "hann",
        nperseg: int = None,
    ):
        super().__init__(
            min_freq_ratio=min_freq_ratio,
            max_freq_ratio=max_freq_ratio,
            use_welch=use_welch,
            window=window,
            nperseg=nperseg,
        )
        self._validate_parameters()
        self._setup_window_type()

    def _setup_window_type(self) -> None:
        """Setup window type for Numba functions."""
        window_map = {"hann": 0, "hamming": 1, "blackman": 2, "rectangular": 3}
        self.window_type = window_map.get(self.parameters["window"], 0)

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not (
            0
            < self.parameters["min_freq_ratio"]
            < self.parameters["max_freq_ratio"]
            < 0.5
        ):
            raise ValueError(
                "Frequency ratios must satisfy: 0 < min_freq_ratio < max_freq_ratio < 0.5"
            )

        if self.parameters["nperseg"] is not None and self.parameters["nperseg"] < 2:
            raise ValueError("nperseg must be at least 2")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using Numba-optimized periodogram analysis.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing estimation results.
        """
        if len(data) < 8:
            raise ValueError("Data length must be at least 8 for periodogram analysis")

        # Determine nperseg
        nperseg = self.parameters["nperseg"]
        if nperseg is None:
            nperseg = max(len(data) // 8, 64)

        # Compute PSD using Numba
        if self.parameters["use_welch"]:
            freqs, psd = _compute_welch_psd_numba(data, nperseg, self.window_type)
        else:
            freqs, psd = _compute_periodogram_numba(data, self.window_type)

        # Select frequency range for fitting
        nyquist = 0.5
        min_freq = self.parameters["min_freq_ratio"] * nyquist
        max_freq = self.parameters["max_freq_ratio"] * nyquist

        # Find indices in frequency range
        valid_indices = []
        for i in range(len(freqs)):
            if min_freq <= freqs[i] <= max_freq and psd[i] > 0:
                valid_indices.append(i)

        if len(valid_indices) < 3:
            raise ValueError("Insufficient frequency points for fitting")

        # Extract valid data
        freqs_sel = np.array([freqs[i] for i in valid_indices])
        psd_sel = np.array([psd[i] for i in valid_indices])

        # Compute log values
        log_freqs = np.log(freqs_sel)
        log_psd = np.log(psd_sel)

        # Fit power law using Numba
        slope, intercept, r_squared = _fit_power_law_numba(log_freqs, log_psd)

        beta = -slope  # PSD ~ f^{-beta}
        hurst = (beta + 1) / 2  # H = (beta + 1) / 2

        self.results = {
            "hurst_parameter": hurst,
            "beta": beta,
            "intercept": intercept,
            "r_squared": r_squared,
            "m": len(freqs_sel),
            "log_freq": log_freqs,
            "log_psd": log_psd,
            "frequency": freqs_sel,
            "periodogram": psd_sel,
            "frequency_all": freqs,
            "periodogram_all": psd,
        }

        return self.results

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for the estimated parameters.

        Parameters
        ----------
        confidence_level : float, default=0.95
            Confidence level for the intervals.

        Returns
        -------
        Dict[str, Tuple[float, float]]
            Dictionary containing confidence intervals.
        """
        if not self.results:
            return {}

        # Calculate confidence interval for Hurst parameter
        n_points = len(self.results["log_freq"])
        t_critical = stats.t.ppf((1 + confidence_level) / 2, n_points - 2)

        # Estimate standard error from R-squared
        std_err = np.sqrt((1 - self.results["r_squared"]) / (n_points - 2))

        H = self.results["hurst_parameter"]
        ci_lower = H - t_critical * std_err
        ci_upper = H + t_critical * std_err

        return {"hurst_parameter": (ci_lower, ci_upper)}

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the estimation.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing quality metrics.
        """
        if not self.results:
            return {}

        return {
            "r_squared": self.results["r_squared"],
            "std_error": np.sqrt(
                (1 - self.results["r_squared"]) / (self.results["m"] - 2)
            ),
            "n_frequencies": self.results["m"],
        }

    def plot_scaling(self, save_path: str = None) -> None:
        """
        Plot the periodogram scaling relationship.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot. If None, displays the plot.
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Log-log scaling relationship
        log_freq = self.results["log_freq"]
        log_psd = self.results["log_psd"]
        beta = self.results["beta"]
        r_squared = self.results["r_squared"]

        ax1.scatter(log_freq, log_psd, color="blue", alpha=0.7, label="Data points")

        # Plot fitted line
        x_fit = np.array([min(log_freq), max(log_freq)])
        y_fit = -beta * x_fit + self.results["intercept"]
        ax1.plot(
            x_fit,
            y_fit,
            "r--",
            linewidth=2,
            label=f"Fit: β = {beta:.3f} (R² = {r_squared:.3f})",
        )

        ax1.set_xlabel("log(Frequency)")
        ax1.set_ylabel("log(Periodogram)")
        ax1.set_title("Periodogram Scaling Relationship (Numba)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: PSD vs frequency (linear scale)
        freq = self.results["frequency"]
        psd = self.results["periodogram"]
        H = self.results["hurst_parameter"]

        ax2.scatter(freq, psd, color="green", alpha=0.7, label="Data points")

        # Plot fitted curve
        x_fit_linear = np.linspace(min(freq), max(freq), 100)
        y_fit_linear = np.exp(self.results["intercept"]) * (x_fit_linear ** (-beta))
        ax2.plot(
            x_fit_linear,
            y_fit_linear,
            "r--",
            linewidth=2,
            label=f"Power law fit: H = {H:.3f}",
        )

        ax2.set_xlabel("Frequency")
        ax2.set_ylabel("Power Spectral Density")
        ax2.set_title("Power Spectral Density vs Frequency")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Add text box with results
        textstr = f"Hurst Parameter: {H:.3f}\nβ: {beta:.3f}\nR²: {r_squared:.3f}"
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        ax2.text(
            0.05,
            0.95,
            textstr,
            transform=ax2.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=props,
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {save_path}")
        else:
            plt.show()

        plt.close()
