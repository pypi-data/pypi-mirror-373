"""
Geweke-Porter-Hudak (GPH) Hurst parameter estimator.

This module implements the GPH estimator for the Hurst parameter using
log-periodogram regression with a specific regressor.
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


class GPHEstimator(BaseEstimator):
    """
    Geweke-Porter-Hudak (GPH) Hurst parameter estimator.

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
    window : str, optional (default='hann')
        Window function for Welch's method.
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
        window="hann",
        nperseg=None,
        apply_bias_correction=True,
    ):
        super().__init__()
        self.min_freq_ratio = min_freq_ratio
        self.max_freq_ratio = max_freq_ratio
        self.use_welch = use_welch
        self.window = window
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

    def estimate(self, data):
        """
        Estimate Hurst parameter using GPH method.

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
            # Ensure nperseg is not larger than data length
            self.nperseg = min(max(n // 8, 64), n)

        # Compute periodogram
        if self.use_welch:
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

        # Convert to angular frequencies
        omega = 2 * np.pi * freqs_sel

        # GPH regressor: log(4*sin^2(ω/2))
        regressor = np.log(4 * np.sin(omega / 2) ** 2)
        log_periodogram = np.log(psd_sel)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            regressor, log_periodogram
        )
        d_parameter = -slope  # d = -slope

        # Apply bias correction if requested
        if self.apply_bias_correction:
            m = len(freqs_sel)
            # Simple bias correction for finite sample effects
            bias_correction = 0.5 * np.log(m) / m
            d_parameter += bias_correction

        # Convert to Hurst parameter: H = d + 0.5
        hurst = d_parameter + 0.5

        # Ensure Hurst parameter is in valid range
        hurst = np.clip(hurst, 0.01, 0.99)

        self.results = {
            "hurst_parameter": float(hurst),
            "d_parameter": float(d_parameter),
            "intercept": float(intercept),
            "slope": float(slope),
            "r_squared": float(r_value**2),
            "p_value": float(p_value),
            "std_error": float(std_err),
            "m": int(len(freqs_sel)),
            "log_regressor": regressor,
            "log_periodogram": log_periodogram,
            "frequency": freqs_sel,
            "periodogram": psd_sel,
        }
        return self.results

    def plot_scaling(self, save_path=None):
        """Plot the scaling relationship and PSD."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        plt.figure(figsize=(15, 4))

        # Log-log scaling relationship
        plt.subplot(1, 3, 1)
        x = self.results["log_regressor"]
        y = self.results["log_periodogram"]

        plt.scatter(x, y, s=40, alpha=0.7, label="Data points")

        # Plot fitted line
        slope, intercept, _, _, _ = stats.linregress(x, y)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept
        plt.plot(x_fit, y_fit, "r--", label="Linear fit")

        plt.xlabel("log(4 sin²(ω/2))")
        plt.ylabel("log(Periodogram)")
        plt.title("GPH Regression")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Log-log components
        plt.subplot(1, 3, 2)
        plt.scatter(np.exp(x), np.exp(y), s=30, alpha=0.7)
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Regressor")
        plt.ylabel("Periodogram")
        plt.title("GPH Components (log-log)")
        plt.grid(True, which="both", ls=":", alpha=0.3)

        # Plain PSD view for context
        try:
            import numpy as _np

            n_points = len(y)
            freq_axis = _np.linspace(0, 0.5, n_points)
            plt.subplot(1, 3, 3)
            plt.plot(freq_axis, _np.exp(y), alpha=0.7)
            plt.xlabel("Frequency (proxy)")
            plt.ylabel("Periodogram")
            plt.title("PSD (linear scale, proxy)")
            plt.grid(True, alpha=0.3)
        except Exception:
            pass

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()
