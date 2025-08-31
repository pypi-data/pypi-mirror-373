"""
Wavelet Whittle Analysis estimator.

This module provides wavelet Whittle analysis for estimating the Hurst parameter
from time series data using wavelet-based Whittle likelihood estimation.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats, optimize
import pywt
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class WaveletWhittleEstimator(BaseEstimator):
    """
    Wavelet Whittle Analysis estimator.

    This estimator combines wavelet decomposition with Whittle likelihood estimation
    to provide robust estimation of the Hurst parameter for fractional processes.

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
        Initialize the Wavelet Whittle estimator.

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
        self.wavelet_coeffs = {}
        self.periodogram_values = {}
        self.theoretical_spectrum = {}
        self.estimated_hurst = None
        self.confidence_interval = None
        self.whittle_likelihood = None

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

    def _theoretical_spectrum_fgn(
        self, frequencies: np.ndarray, H: float, sigma: float = 1.0
    ) -> np.ndarray:
        """
        Calculate theoretical spectrum for fractional Gaussian noise.

        Args:
            frequencies (np.ndarray): Frequency array
            H (float): Hurst parameter
            sigma (float): Scale parameter

        Returns:
            np.ndarray: Theoretical power spectrum
        """
        # Theoretical spectrum for fGn
        # S(f) = sigma^2 * |f|^(1-2H) for f != 0
        spectrum = np.zeros_like(frequencies)
        nonzero_freq = frequencies != 0
        spectrum[nonzero_freq] = sigma**2 * np.abs(frequencies[nonzero_freq]) ** (
            1 - 2 * H
        )

        # Handle zero frequency (DC component)
        if np.any(frequencies == 0):
            spectrum[frequencies == 0] = sigma**2

        return spectrum

    def _whittle_likelihood(
        self, H: float, wavelet_coeffs: List[np.ndarray], scales: List[int]
    ) -> float:
        """
        Calculate Whittle likelihood for given Hurst parameter.

        Args:
            H (float): Hurst parameter
            wavelet_coeffs (List[np.ndarray]): Wavelet coefficients at each scale
            scales (List[int]): Corresponding scales

        Returns:
            float: Negative log-likelihood (to be minimized)
        """
        total_likelihood = 0.0

        for i, (coeffs, scale) in enumerate(zip(wavelet_coeffs, scales)):
            # Calculate periodogram of wavelet coefficients
            fft_coeffs = np.fft.fft(coeffs)
            periodogram = np.abs(fft_coeffs) ** 2 / len(coeffs)

            # Calculate frequencies
            freqs = np.fft.fftfreq(len(coeffs))

            # Theoretical spectrum at this scale
            theoretical = self._theoretical_spectrum_fgn(freqs, H)

            # Whittle likelihood contribution
            # L = sum(log(S(f)) + I(f)/S(f))
            valid_indices = theoretical > 0
            if np.any(valid_indices):
                log_spectrum = np.log(theoretical[valid_indices])
                ratio = periodogram[valid_indices] / theoretical[valid_indices]
                total_likelihood += np.sum(log_spectrum + ratio)

        return total_likelihood

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using wavelet Whittle analysis.

        Args:
            data (np.ndarray): Input time series data

        Returns:
            Dict[str, Any]: Dictionary containing estimation results
        """
        if len(data) < 2 ** max(self.scales):
            raise ValueError(
                f"Data length {len(data)} is too short for scale {max(self.scales)}"
            )

        # Perform wavelet decomposition at all scales
        self.wavelet_coeffs = {}
        wavelet_coeffs_list = []

        for scale in self.scales:
            coeffs = pywt.wavedec(data, self.wavelet, level=scale)
            detail_coeffs = coeffs[1]  # Detail coefficients at scale level
            self.wavelet_coeffs[scale] = detail_coeffs
            wavelet_coeffs_list.append(detail_coeffs)

        # Optimize Whittle likelihood to find best Hurst parameter
        def objective(H):
            return self._whittle_likelihood(H, wavelet_coeffs_list, self.scales)

        # Use bounded optimization to ensure H is in [0, 1]
        result = optimize.minimize_scalar(
            objective, bounds=(0.01, 0.99), method="bounded"  # Avoid exact 0 and 1
        )

        if not result.success:
            raise RuntimeError(f"Optimization failed: {result.message}")

        self.estimated_hurst = result.x
        self.whittle_likelihood = result.fun

        # Calculate confidence interval using Hessian approximation
        self.confidence_interval = self.get_confidence_interval()

        # Return results dictionary
        results = {
            "hurst_parameter": self.estimated_hurst,
            "confidence_interval": self.confidence_interval,
            "whittle_likelihood": self.whittle_likelihood,
            "scales": self.scales,
            "wavelet_type": self.wavelet,
            "optimization_success": result.success,
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

        # Simple approximation using likelihood ratio test
        # This is a simplified approach - in practice, more sophisticated methods
        # like profile likelihood or bootstrap would be used

        # Calculate approximate standard error
        # This is a rough approximation based on the curvature of the likelihood
        H_range = np.linspace(
            self.estimated_hurst - 0.1, self.estimated_hurst + 0.1, 21
        )
        likelihoods = []

        wavelet_coeffs_list = list(self.wavelet_coeffs.values())
        scales_list = list(self.wavelet_coeffs.keys())

        for H in H_range:
            likelihoods.append(
                self._whittle_likelihood(H, wavelet_coeffs_list, scales_list)
            )

        # Fit quadratic to approximate curvature
        coeffs = np.polyfit(H_range, likelihoods, 2)
        curvature = 2 * coeffs[0]  # Second derivative

        if curvature > 0:
            std_error = np.sqrt(1 / curvature)
        else:
            std_error = 0.1  # Fallback value

        # Calculate confidence interval
        z_score = stats.norm.ppf((1 + confidence) / 2)
        margin = z_score * std_error

        return (self.estimated_hurst - margin, self.estimated_hurst + margin)

    def plot_analysis(self, figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        Plot the wavelet Whittle analysis results.

        Args:
            figsize (Tuple[int, int]): Figure size (width, height)
        """
        import matplotlib.pyplot as plt

        if self.estimated_hurst is None:
            raise ValueError("Must call estimate() before plotting")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Plot 1: Wavelet coefficients variance vs scales
        variances = [np.var(coeffs) for coeffs in self.wavelet_coeffs.values()]
        ax1.loglog(self.scales, variances, "bo-", label="Wavelet Coefficient Variances")
        ax1.set_xlabel("Scale")
        ax1.set_ylabel("Variance")
        ax1.set_title("Wavelet Coefficient Variance vs Scale")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot 2: Likelihood function around estimated H
        H_range = np.linspace(
            max(0.01, self.estimated_hurst - 0.2),
            min(0.99, self.estimated_hurst + 0.2),
            50,
        )
        likelihoods = []

        wavelet_coeffs_list = list(self.wavelet_coeffs.values())
        scales_list = list(self.wavelet_coeffs.keys())

        for H in H_range:
            likelihoods.append(
                self._whittle_likelihood(H, wavelet_coeffs_list, scales_list)
            )

        ax2.plot(H_range, likelihoods, "b-", label="Whittle Likelihood")
        ax2.axvline(
            self.estimated_hurst,
            color="r",
            linestyle="--",
            label=f"Estimated H={self.estimated_hurst:.3f}",
        )
        ax2.set_xlabel("Hurst Parameter (H)")
        ax2.set_ylabel("Negative Log-Likelihood")
        ax2.set_title("Whittle Likelihood Function")
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
            "whittle_likelihood": self.whittle_likelihood,
            "wavelet_type": self.wavelet,
            "scales_used": self.scales,
            "num_scales": len(self.scales),
            "method": "Wavelet Whittle Analysis",
        }
