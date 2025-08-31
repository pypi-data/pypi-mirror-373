"""
Continuous Wavelet Transform (CWT) Analysis estimator.

This module provides Continuous Wavelet Transform analysis for estimating the Hurst parameter
from time series data using continuous wavelet decomposition.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats, signal
import pywt
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class CWTEstimator(BaseEstimator):
    """
    Continuous Wavelet Transform (CWT) Analysis estimator.

    This estimator uses continuous wavelet transforms to analyze the scaling behavior
    of time series data and estimate the Hurst parameter for fractional processes.

    Attributes:
        wavelet (str): Wavelet type to use for continuous transform
        scales (np.ndarray): Array of scales for wavelet analysis
        confidence (float): Confidence level for confidence intervals
    """

    def __init__(
        self,
        wavelet: str = "cmor1.5-1.0",
        scales: Optional[np.ndarray] = None,
        confidence: float = 0.95,
    ):
        """
        Initialize the CWT estimator.

        Args:
            wavelet (str): Wavelet type for continuous transform (default: 'cmor1.5-1.0')
            scales (np.ndarray, optional): Array of scales for analysis.
                                         If None, uses automatic scale selection
            confidence (float): Confidence level for intervals (default: 0.95)
        """
        super().__init__()
        self.wavelet = wavelet
        self.confidence = confidence

        # Set default scales if not provided
        if scales is None:
            self.scales = np.logspace(1, 4, 20)  # Logarithmically spaced scales
        else:
            self.scales = scales

        # Results storage
        self.wavelet_coeffs = None
        self.power_spectrum = None
        self.scale_powers = {}
        self.estimated_hurst = None
        self.confidence_interval = None
        self.r_squared = None

    def _validate_parameters(self) -> None:
        """
        Validate the estimator parameters.

        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(self.wavelet, str):
            raise ValueError("wavelet must be a string")
        if not isinstance(self.scales, np.ndarray) or len(self.scales) == 0:
            raise ValueError("scales must be a non-empty numpy array")
        if not (0 < self.confidence < 1):
            raise ValueError("confidence must be between 0 and 1")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using Continuous Wavelet Transform analysis.

        Args:
            data (np.ndarray): Input time series data

        Returns:
            Dict[str, Any]: Dictionary containing estimation results
        """
        if len(data) < 50:
            raise ValueError("Data length must be at least 50 for CWT analysis")
        
        # Adjust scales for shorter data
        if len(data) < 100:
            # Use fewer scales for shorter data
            max_scale = min(max(self.scales), len(data) // 4)
            self.scales = [s for s in self.scales if s <= max_scale]
            if len(self.scales) < 2:
                raise ValueError("Insufficient scales available for data length")

        # Perform continuous wavelet transform
        self.wavelet_coeffs, frequencies = pywt.cwt(data, self.scales, self.wavelet)

        # Calculate power spectrum (squared magnitude of coefficients)
        self.power_spectrum = np.abs(self.wavelet_coeffs) ** 2

        # Calculate average power at each scale
        self.scale_powers = {}
        scale_logs = []
        power_logs = []

        for i, scale in enumerate(self.scales):
            # Average power across time at this scale
            avg_power = np.mean(self.power_spectrum[i, :])
            self.scale_powers[scale] = avg_power

            scale_logs.append(np.log2(scale))
            power_logs.append(np.log2(avg_power))

        # Fit linear regression to log-log plot
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            scale_logs, power_logs
        )

        # Hurst parameter is related to the slope
        # For fBm: H = (slope + 1) / 2
        # For fGn: H = (slope + 1) / 2
        self.estimated_hurst = (slope + 1) / 2
        self.r_squared = r_value**2

        # Calculate confidence interval
        self.confidence_interval = self.get_confidence_interval()

        # Return results dictionary
        results = {
            "hurst_parameter": self.estimated_hurst,
            "confidence_interval": self.confidence_interval,
            "r_squared": self.r_squared,
            "scales": self.scales,
            "wavelet_type": self.wavelet,
            "slope": slope,
            "intercept": intercept,
        }

        return results

    def get_confidence_interval(
        self, confidence: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for the Hurst parameter estimate.

        Args:
            confidence (float, optional): Confidence level. Uses instance default if None

        Returns:
            Tuple[float, float]: Lower and upper bounds of confidence interval
        """
        if confidence is None:
            confidence = self.confidence

        if self.estimated_hurst is None:
            raise ValueError("Must call estimate() before getting confidence interval")

        # Calculate standard error of the slope
        scale_logs = [np.log2(scale) for scale in self.scales]
        power_logs = [np.log2(power) for power in self.scale_powers.values()]

        n = len(scale_logs)
        x_var = np.var(scale_logs, ddof=1)

        # Residual standard error
        residuals = np.array(power_logs) - (
            np.array(scale_logs) * (2 * self.estimated_hurst - 1)
            + np.mean(power_logs)
            - np.mean(scale_logs) * (2 * self.estimated_hurst - 1)
        )
        mse = np.sum(residuals**2) / (n - 2)

        # Standard error of slope
        slope_se = np.sqrt(mse / (n * x_var))

        # Convert to Hurst parameter standard error
        hurst_se = slope_se / 2

        # Calculate confidence interval
        t_value = stats.t.ppf((1 + confidence) / 2, df=n - 2)
        margin = t_value * hurst_se

        return (self.estimated_hurst - margin, self.estimated_hurst + margin)

    def plot_analysis(
        self, data: np.ndarray, figsize: Tuple[int, int] = (15, 10)
    ) -> None:
        """
        Plot the CWT analysis results.

        Args:
            data (np.ndarray): Original time series data
            figsize (Tuple[int, int]): Figure size (width, height)
        """
        import matplotlib.pyplot as plt

        if self.estimated_hurst is None:
            raise ValueError("Must call estimate() before plotting")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        # Plot 1: Original time series
        ax1.plot(data, "b-", alpha=0.7)
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Amplitude")
        ax1.set_title("Original Time Series")
        ax1.grid(True, alpha=0.3)

        # Plot 2: Wavelet scalogram
        im = ax2.imshow(
            np.log10(self.power_spectrum),
            aspect="auto",
            extent=[0, len(data), np.log2(self.scales[0]), np.log2(self.scales[-1])],
        )
        ax2.set_xlabel("Time")
        ax2.set_ylabel("log2(Scale)")
        ax2.set_title("Wavelet Scalogram")
        plt.colorbar(im, ax=ax2, label="log10(Power)")

        # Plot 3: Power vs scale
        ax3.loglog(
            self.scales, list(self.scale_powers.values()), "bo-", label="Scale Powers"
        )
        ax3.set_xlabel("Scale")
        ax3.set_ylabel("Power")
        ax3.set_title("Power vs Scale")
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Plot 4: Log-log plot with regression line
        scale_logs = [np.log2(scale) for scale in self.scales]
        power_logs = [np.log2(power) for power in self.scale_powers.values()]

        ax4.scatter(scale_logs, power_logs, color="blue", label="Data Points")

        # Plot regression line
        x_line = np.array([min(scale_logs), max(scale_logs)])
        y_line = (
            (2 * self.estimated_hurst - 1) * x_line
            + np.mean(power_logs)
            - np.mean(scale_logs) * (2 * self.estimated_hurst - 1)
        )
        ax4.plot(
            x_line, y_line, "r--", label=f"Regression (H={self.estimated_hurst:.3f})"
        )

        ax4.set_xlabel("log2(Scale)")
        ax4.set_ylabel("log2(Power)")
        ax4.set_title("Log-Log Plot with Regression")
        ax4.grid(True, alpha=0.3)
        ax4.legend()

        plt.tight_layout()
        plt.show()

    def get_results_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the estimation results.

        Returns:
            Dict[str, Any]: Dictionary containing estimation results
        """
        if self.estimated_hurst is None:
            raise ValueError("Must call estimate() before getting results summary")

        return {
            "estimated_hurst": self.estimated_hurst,
            "confidence_interval": self.confidence_interval,
            "r_squared": self.r_squared,
            "wavelet_type": self.wavelet,
            "scales_used": self.scales.tolist(),
            "num_scales": len(self.scales),
            "scale_powers": self.scale_powers,
            "method": "Continuous Wavelet Transform (CWT) Analysis",
        }
