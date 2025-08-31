"""
Periodogram-based Hurst parameter estimator.

This module implements a periodogram-based estimator for the Hurst parameter
using power spectral density analysis. The estimator fits a power law to the
low-frequency portion of the periodogram.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats, signal
# Import base estimator
try:
    from models.estimators.base_estimator import BaseEstimator
except ImportError:
    # Fallback if base estimator not available
    class BaseEstimator:
        def __init__(self, **kwargs):
            self.parameters = kwargs


class PeriodogramEstimator(BaseEstimator):
    """
    Periodogram-based Hurst parameter estimator.

    This estimator computes the power spectral density (PSD) of the time series
    and fits a power law to the low-frequency portion to estimate the Hurst
    parameter. The relationship is: PSD(f) ~ f^(-beta) where beta = 2H - 1.

    Parameters
    ----------
    min_freq_ratio : float, optional (default=0.01)
        Minimum frequency ratio (relative to Nyquist) for fitting.
    max_freq_ratio : float, optional (default=0.1)
        Maximum frequency ratio (relative to Nyquist) for fitting.
    use_welch : bool, optional (default=True)
        Whether to use Welch's method for PSD estimation.
    window : str, optional (default='hann')
        Window function for Welch's method.
    nperseg : int, optional (default=None)
        Length of each segment for Welch's method. If None, uses n/8.
    use_multitaper : bool, optional (default=False)
        Whether to use multi-taper method for PSD estimation.
    n_tapers : int, optional (default=3)
        Number of tapers for multi-taper method.
    """

    def __init__(
        self,
        min_freq_ratio=0.01,
        max_freq_ratio=0.1,
        use_welch=True,
        window="hann",
        nperseg=None,
        use_multitaper=False,
        n_tapers=3,
    ):
        super().__init__()
        self.min_freq_ratio = min_freq_ratio
        self.max_freq_ratio = max_freq_ratio
        self.use_welch = use_welch
        self.window = window
        self.nperseg = nperseg
        self.use_multitaper = use_multitaper
        self.n_tapers = n_tapers
        self.results = {}
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not (0 < self.min_freq_ratio < self.max_freq_ratio < 0.5):
            raise ValueError(
                "Frequency ratios must satisfy: 0 < min_freq_ratio < max_freq_ratio < 0.5"
            )

        if self.n_tapers < 1:
            raise ValueError("n_tapers must be at least 1")

        if self.nperseg is not None and self.nperseg < 2:
            raise ValueError("nperseg must be at least 2")

    def estimate(self, data):
        """
        Estimate Hurst parameter using periodogram analysis.

        Parameters
        ----------
        data : array-like
            Time series data.

        Returns
        -------
        dict
            Dictionary containing:
            - hurst_parameter: Estimated Hurst parameter
            - beta: Power law exponent (beta = 2H - 1)
            - intercept: Intercept of the linear fit
            - r_squared: R-squared value of the fit
            - m: Number of frequency points used in fitting
            - log_freq: Log frequencies used in fitting
            - log_psd: Log PSD values used in fitting
            - frequency: Original frequencies
            - periodogram: Original PSD values
        """
        data = np.asarray(data)
        n = len(data)

        if self.nperseg is None:
            # Ensure nperseg is not larger than data length
            self.nperseg = min(max(n // 8, 64), n)

        # Compute PSD
        if self.use_multitaper:
            freqs, psd = self._compute_multitaper_psd(data)
        elif self.use_welch:
            freqs, psd = signal.welch(
                data, window=self.window, nperseg=self.nperseg, scaling="density"
            )
        else:
            freqs, psd = signal.periodogram(data, window=self.window, scaling="density")

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

        # Fit power law: log(PSD) = -beta * log(f) + c
        log_f = np.log(freqs_sel)
        log_I = np.log(psd_sel)

        slope, intercept, r_value, p_value, std_err = stats.linregress(log_f, log_I)
        beta = -slope  # PSD ~ f^{-beta}
        hurst = (beta + 1) / 2  # H = (beta + 1) / 2

        self.results = {
            "hurst_parameter": float(hurst),
            "beta": float(beta),
            "intercept": float(intercept),
            "slope": float(slope),
            "r_squared": float(r_value**2),
            "p_value": float(p_value),
            "std_error": float(std_err),
            "m": int(len(freqs_sel)),
            "log_freq": log_f,
            "log_psd": log_I,
            # For plotting PSD alongside log-log
            "frequency": freqs_sel,
            "periodogram": psd_sel,
            "frequency_all": freqs,
            "periodogram_all": psd,
        }
        return self.results

    def _compute_multitaper_psd(self, data):
        """Compute PSD using multi-taper method."""
        from scipy.signal import windows

        n = len(data)
        # Create DPSS tapers
        tapers = windows.dpss(n, NW=self.n_tapers, Kmax=self.n_tapers)

        # Apply tapers and compute periodograms
        psd_sum = np.zeros(n // 2 + 1)
        for taper in tapers:
            tapered_data = data * taper
            freqs, psd = signal.periodogram(tapered_data, scaling="density")
            psd_sum += psd

        return freqs, psd_sum / self.n_tapers

    def plot_scaling(self, save_path=None):
        """Plot the scaling relationship and PSD."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        plt.figure(figsize=(15, 4))

        # Log-log scaling relationship
        plt.subplot(1, 3, 1)
        log_f = self.results["log_freq"]
        log_I = self.results["log_psd"]

        plt.scatter(log_f, log_I, s=40, alpha=0.7, label="Data points")

        # Plot fitted line
        x_fit = np.linspace(min(log_f), max(log_f), 100)
        y_fit = -self.results["beta"] * x_fit + self.results["intercept"]
        plt.plot(x_fit, y_fit, "r--", label=f"Fit (β={self.results['beta']:.3f})")

        plt.xlabel("log(Frequency)")
        plt.ylabel("log(Periodogram)")
        plt.title("Periodogram Scaling Relationship")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Log-log PSD
        plt.subplot(1, 3, 2)
        freqs = np.exp(log_f)
        psd = np.exp(log_I)
        plt.loglog(freqs, psd, "o", alpha=0.7, label="Low-freq points")
        plt.xlabel("Frequency")
        plt.ylabel("Periodogram")
        plt.title("Periodogram (log-log)")
        plt.grid(True, which="both", ls=":", alpha=0.3)
        plt.legend()

        # Linear-frequency PSD over full range
        plt.subplot(1, 3, 3)
        freq_all = self.results.get("frequency_all")
        psd_all = self.results.get("periodogram_all")
        if freq_all is not None and psd_all is not None:
            plt.plot(freq_all, psd_all, alpha=0.7)
        else:
            plt.plot(freqs, psd, alpha=0.7)
        plt.xlabel("Frequency")
        plt.ylabel("Periodogram")
        plt.title("PSD (linear scale)")
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()
