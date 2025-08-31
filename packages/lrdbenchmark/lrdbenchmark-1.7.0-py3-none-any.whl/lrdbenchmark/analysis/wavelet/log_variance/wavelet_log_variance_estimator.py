"""
Wavelet Log Variance Analysis estimator.

This module provides wavelet log variance analysis for estimating the Hurst parameter
from time series data using wavelet decomposition with log-transformed variances.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats
import pywt
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class WaveletLogVarianceEstimator(BaseEstimator):
    """
    Wavelet Log Variance Analysis estimator.

    This estimator uses wavelet decomposition to analyze the log-transformed variance
    of wavelet coefficients at different scales, which can be used to estimate the
    Hurst parameter for fractional processes with improved statistical properties.

    Attributes:
        wavelet (str): Wavelet type to use for decomposition
        scales (List[int]): List of scales for wavelet analysis
        confidence (float): Confidence level for confidence intervals
    """

    def __init__(
        self,
        wavelet: str = "db4",
        scales: Optional[List[int]] = None,
        confidence: float = 0.95,
    ):
        """
        Initialize the Wavelet Log Variance estimator.

        Args:
            wavelet (str): Wavelet type (default: 'db4')
            scales (List[int], optional): List of scales for analysis.
                                        If None, uses automatic scale selection
            confidence (float): Confidence level for intervals (default: 0.95)
        """
        super().__init__()
        self.wavelet = wavelet
        self.confidence = confidence

        # Set default scales if not provided
        if scales is None:
            self.scales = list(range(1, 11))  # Scales 1-10
        else:
            self.scales = scales

        # Results storage
        self.wavelet_variances = {}
        self.log_variances = {}
        self.scale_logs = []
        self.log_variance_values = []
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
        if not isinstance(self.scales, list) or len(self.scales) == 0:
            raise ValueError("scales must be a non-empty list")
        if not (0 < self.confidence < 1):
            raise ValueError("confidence must be between 0 and 1")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using wavelet log variance analysis.

        Args:
            data (np.ndarray): Input time series data

        Returns:
            Dict[str, Any]: Dictionary containing estimation results
        """
        if len(data) < 2 ** max(self.scales):
            raise ValueError(
                f"Data length {len(data)} is too short for scale {max(self.scales)}"
            )

        # Calculate wavelet log variances for each scale
        self.wavelet_variances = {}
        self.log_variances = {}
        self.scale_logs = []
        self.log_variance_values = []

        for scale in self.scales:
            # Perform wavelet decomposition
            coeffs = pywt.wavedec(data, self.wavelet, level=scale)

            # Calculate variance of detail coefficients at this scale
            detail_coeffs = coeffs[1]  # Detail coefficients at scale level
            variance = np.var(detail_coeffs)

            # Store both raw variance and log variance
            self.wavelet_variances[scale] = variance
            log_variance = np.log(variance)
            self.log_variances[scale] = log_variance

            self.scale_logs.append(np.log2(scale))
            self.log_variance_values.append(log_variance)

        # Fit linear regression to log-scale vs log-variance plot
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            np.array(self.scale_logs), np.array(self.log_variance_values)
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
            "wavelet_variances": self.wavelet_variances,
            "log_variances": self.log_variances,
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
        n = len(self.scale_logs)
        x_var = np.var(self.scale_logs, ddof=1)

        # Residual standard error
        residuals = np.array(self.log_variance_values) - (
            np.array(self.scale_logs) * (2 * self.estimated_hurst - 1)
            + np.mean(self.log_variance_values)
            - np.mean(self.scale_logs) * (2 * self.estimated_hurst - 1)
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

    def plot_analysis(self, figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        Plot the wavelet log variance analysis results.

        Args:
            figsize (Tuple[int, int]): Figure size (width, height)
        """
        import matplotlib.pyplot as plt

        if self.estimated_hurst is None:
            raise ValueError("Must call estimate() before plotting")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Plot 1: Log variances vs scales
        ax1.semilogx(
            self.scales, list(self.log_variances.values()), "bo-", label="Log Variances"
        )
        ax1.set_xlabel("Scale")
        ax1.set_ylabel("Log Variance")
        ax1.set_title("Log Variance vs Scale")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot 2: Log-log plot with regression line
        ax2.scatter(
            self.scale_logs, self.log_variance_values, color="blue", label="Data Points"
        )

        # Plot regression line
        x_line = np.array([min(self.scale_logs), max(self.scale_logs)])
        y_line = (
            (2 * self.estimated_hurst - 1) * x_line
            + np.mean(self.log_variance_values)
            - np.mean(self.scale_logs) * (2 * self.estimated_hurst - 1)
        )
        ax2.plot(
            x_line, y_line, "r--", label=f"Regression (H={self.estimated_hurst:.3f})"
        )

        ax2.set_xlabel("log2(Scale)")
        ax2.set_ylabel("Log Variance")
        ax2.set_title("Log-Log Plot with Regression")
        ax2.grid(True, alpha=0.3)
        ax2.legend()

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
            "scales_used": self.scales,
            "num_scales": len(self.scales),
            "wavelet_variances": self.wavelet_variances,
            "log_variances": self.log_variances,
            "method": "Wavelet Log Variance Analysis",
        }
