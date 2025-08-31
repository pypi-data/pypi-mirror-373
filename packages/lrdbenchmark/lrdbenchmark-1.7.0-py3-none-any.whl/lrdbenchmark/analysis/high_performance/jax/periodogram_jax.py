import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from scipy import stats, signal
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


def _compute_periodogram_jax(
    data: jnp.ndarray, window: str = "hann"
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """
    Compute periodogram using JAX FFT operations.

    Parameters
    ----------
    data : jnp.ndarray
        Input time series data.
    window : str
        Window function to apply.

    Returns
    -------
    Tuple[jnp.ndarray, jnp.ndarray]
        Frequencies and power spectral density.
    """
    n = len(data)

    # Apply window
    if window == "hann":
        window_vals = jnp.hanning(n)
    elif window == "hamming":
        window_vals = jnp.hamming(n)
    elif window == "blackman":
        window_vals = jnp.blackman(n)
    else:
        window_vals = jnp.ones(n)

    # Apply window and compute FFT
    windowed_data = data * window_vals
    fft_vals = jnp.fft.fft(windowed_data)

    # Compute power spectral density
    psd = jnp.abs(fft_vals) ** 2 / n

    # Take only positive frequencies
    freqs = jnp.fft.fftfreq(n)
    positive_mask = freqs > 0
    freqs = freqs[positive_mask]
    psd = psd[positive_mask]

    return freqs, psd


def _compute_welch_psd_jax(
    data: jnp.ndarray, nperseg: int, window: str = "hann"
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """
    Compute Welch's PSD estimate using JAX.

    Parameters
    ----------
    data : jnp.ndarray
        Input time series data.
    nperseg : int
        Length of each segment.
    window : str
        Window function to apply.

    Returns
    -------
    Tuple[jnp.ndarray, jnp.ndarray]
        Frequencies and power spectral density.
    """
    n = len(data)
    n_segments = n // nperseg

    if n_segments == 0:
        return _compute_periodogram_jax(data, window)

    # Create window
    if window == "hann":
        window_vals = jnp.hanning(nperseg)
    elif window == "hamming":
        window_vals = jnp.hamming(nperseg)
    elif window == "blackman":
        window_vals = jnp.blackman(nperseg)
    else:
        window_vals = jnp.ones(nperseg)

    # Normalize window
    window_vals = window_vals / jnp.sqrt(jnp.mean(window_vals**2))

    # Reshape data into segments to avoid dynamic slicing
    segments = data.reshape(n_segments, nperseg)

    # Apply window to all segments at once
    windowed_segments = segments * window_vals

    # Compute FFT for all segments
    fft_vals = jnp.fft.fft(windowed_segments, axis=1)

    # Compute power spectral density
    psd = jnp.abs(fft_vals) ** 2 / nperseg

    # Get frequencies (same for all segments)
    freqs = jnp.fft.fftfreq(nperseg)
    positive_mask = freqs > 0
    freqs = freqs[positive_mask]
    psd = psd[:, positive_mask]

    # Average across segments
    psd_avg = jnp.mean(psd, axis=0)

    return freqs, psd_avg


def _fit_power_law_jax(
    log_freqs: jnp.ndarray, log_psd: jnp.ndarray
) -> Tuple[float, float, float]:
    """
    Fit power law using JAX linear algebra operations.

    Parameters
    ----------
    log_freqs : jnp.ndarray
        Log frequencies.
    log_psd : jnp.ndarray
        Log power spectral density.

    Returns
    -------
    Tuple[float, float, float]
        Slope, intercept, and R-squared.
    """
    # Add constant term for linear regression
    X = jnp.column_stack([log_freqs, jnp.ones_like(log_freqs)])
    y = log_psd

    # Solve least squares problem
    coeffs, residuals, rank, s = jnp.linalg.lstsq(X, y, rcond=None)
    slope, intercept = coeffs

    # Compute R-squared
    y_pred = X @ coeffs
    ss_res = jnp.sum((y - y_pred) ** 2)
    ss_tot = jnp.sum((y - jnp.mean(y)) ** 2)
    r_squared = 1 - ss_res / ss_tot

    return slope, intercept, r_squared


class PeriodogramEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Periodogram estimator for Hurst parameter.

    This implementation uses JAX for GPU acceleration and vectorized computations,
    providing significant performance improvements for large datasets.

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
    use_gpu : bool, default=False
        Whether to use GPU acceleration if available.
    """

    def __init__(
        self,
        min_freq_ratio: float = 0.01,
        max_freq_ratio: float = 0.1,
        use_welch: bool = True,
        window: str = "hann",
        nperseg: int = None,
        use_gpu: bool = False,
    ):
        super().__init__(
            min_freq_ratio=min_freq_ratio,
            max_freq_ratio=max_freq_ratio,
            use_welch=use_welch,
            window=window,
            nperseg=nperseg,
            use_gpu=use_gpu,
        )
        self._validate_parameters()
        self._setup_jax()

    def _setup_jax(self) -> None:
        """Setup JAX configuration for GPU acceleration if requested."""
        if self.parameters["use_gpu"]:
            try:
                # Check if GPU is available
                devices = jax.devices()
                gpu_devices = [d for d in devices if d.platform == "gpu"]
                if gpu_devices:
                    print(f"Using GPU acceleration with {len(gpu_devices)} device(s)")
                    # Set default device to first GPU
                    jax.config.update("jax_platform_name", "gpu")
                else:
                    print("GPU requested but not available, falling back to CPU")
                    self.parameters["use_gpu"] = False
            except Exception as e:
                print(f"GPU setup failed: {e}, falling back to CPU")
                self.parameters["use_gpu"] = False

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
        Estimate the Hurst parameter using JAX-optimized periodogram analysis.

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

        # Convert to JAX array
        data_jax = jnp.array(data, dtype=jnp.float32)

        # Determine nperseg
        nperseg = self.parameters["nperseg"]
        if nperseg is None:
            nperseg = max(len(data) // 8, 64)

        # Compute PSD using JAX
        if self.parameters["use_welch"]:
            freqs, psd = _compute_welch_psd_jax(
                data_jax, nperseg, self.parameters["window"]
            )
        else:
            freqs, psd = _compute_periodogram_jax(data_jax, self.parameters["window"])

        # Convert back to numpy for frequency selection
        freqs_np = np.array(freqs)
        psd_np = np.array(psd)

        # Select frequency range for fitting
        nyquist = 0.5
        min_freq = self.parameters["min_freq_ratio"] * nyquist
        max_freq = self.parameters["max_freq_ratio"] * nyquist

        mask = (freqs_np >= min_freq) & (freqs_np <= max_freq)
        freqs_sel = freqs_np[mask]
        psd_sel = psd_np[mask]

        if len(freqs_sel) < 3:
            raise ValueError("Insufficient frequency points for fitting")

        # Filter out zero/negative PSD values
        valid_mask = psd_sel > 0
        freqs_sel = freqs_sel[valid_mask]
        psd_sel = psd_sel[valid_mask]

        if len(freqs_sel) < 3:
            raise ValueError("Insufficient valid PSD points for fitting")

        # Convert to JAX arrays for fitting
        log_freqs_jax = jnp.array(np.log(freqs_sel), dtype=jnp.float32)
        log_psd_jax = jnp.array(np.log(psd_sel), dtype=jnp.float32)

        # Fit power law using JAX
        slope, intercept, r_squared = _fit_power_law_jax(log_freqs_jax, log_psd_jax)

        # Convert results
        slope = float(slope)
        intercept = float(intercept)
        r_squared = float(r_squared)

        beta = -slope  # PSD ~ f^{-beta}
        hurst = (beta + 1) / 2  # H = (beta + 1) / 2

        self.results = {
            "hurst_parameter": hurst,
            "beta": beta,
            "intercept": intercept,
            "r_squared": r_squared,
            "m": len(freqs_sel),
            "log_freq": np.array(log_freqs_jax),
            "log_psd": np.array(log_psd_jax),
            "frequency": freqs_sel,
            "periodogram": psd_sel,
            "frequency_all": freqs_np,
            "periodogram_all": psd_np,
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
        # This is a simplified approach - in practice, you'd want more sophisticated error estimation
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
        ax1.set_title("Periodogram Scaling Relationship (JAX)")
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
