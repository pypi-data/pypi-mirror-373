"""
NUMBA-Optimized Continuous Wavelet Transform (CWT) Analysis estimator.

This module provides a NUMBA-optimized version of the CWT estimator for significantly
improved performance in continuous wavelet transform calculations.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats, signal
import pywt
import sys
import os
import time

# Try to import NUMBA for optimization
try:
    import numba
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Define dummy decorators if NUMBA is not available
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def prange(*args):
        return range(*args)

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, parallel=True)
def _numba_calculate_power_spectrum(wavelet_coeffs: np.ndarray) -> np.ndarray:
    """
    NUMBA-optimized calculation of power spectrum from wavelet coefficients.
    
    Args:
        wavelet_coeffs: Complex wavelet coefficients
        
    Returns:
        Power spectrum (squared magnitude)
    """
    n_scales, n_points = wavelet_coeffs.shape
    power_spectrum = np.empty((n_scales, n_points), dtype=np.float64)
    
    for i in prange(n_scales):
        for j in prange(n_points):
            real_part = wavelet_coeffs[i, j].real
            imag_part = wavelet_coeffs[i, j].imag
            power_spectrum[i, j] = real_part * real_part + imag_part * imag_part
    
    return power_spectrum


@jit(nopython=True, parallel=True)
def _numba_calculate_scale_powers(power_spectrum: np.ndarray) -> np.ndarray:
    """
    NUMBA-optimized calculation of average power at each scale.
    
    Args:
        power_spectrum: Power spectrum array
        
    Returns:
        Average power at each scale
    """
    n_scales, n_points = power_spectrum.shape
    scale_powers = np.empty(n_scales, dtype=np.float64)
    
    for i in prange(n_scales):
        total_power = 0.0
        for j in prange(n_points):
            total_power += power_spectrum[i, j]
        scale_powers[i] = total_power / n_points
    
    return scale_powers


@jit(nopython=True)
def _numba_linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """
    NUMBA-optimized linear regression for slope calculation.
    
    Args:
        x: Independent variable (log scales)
        y: Dependent variable (log powers)
        
    Returns:
        Tuple of (slope, intercept, r_squared)
    """
    n = len(x)
    if n < 2:
        return 0.0, 0.0, 0.0
    
    # Calculate means
    x_mean = 0.0
    y_mean = 0.0
    for i in range(n):
        x_mean += x[i]
        y_mean += y[i]
    x_mean /= n
    y_mean /= n
    
    # Calculate slope and intercept
    numerator = 0.0
    denominator = 0.0
    for i in range(n):
        numerator += (x[i] - x_mean) * (y[i] - y_mean)
        denominator += (x[i] - x_mean) ** 2
    
    if denominator == 0.0:
        return 0.0, y_mean, 0.0
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    # Calculate R-squared
    ss_tot = 0.0
    ss_res = 0.0
    for i in range(n):
        y_pred = slope * x[i] + intercept
        ss_tot += (y[i] - y_mean) ** 2
        ss_res += (y[i] - y_pred) ** 2
    
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0.0 else 0.0
    
    return slope, intercept, r_squared


class NumbaOptimizedCWTEstimator(BaseEstimator):
    """
    NUMBA-Optimized Continuous Wavelet Transform (CWT) Analysis estimator.

    This estimator uses NUMBA-optimized continuous wavelet transforms to analyze 
    the scaling behavior of time series data and estimate the Hurst parameter 
    for fractional processes with significantly improved performance.

    Attributes:
        wavelet (str): Wavelet type to use for continuous transform
        scales (np.ndarray): Array of scales for wavelet analysis
        confidence (float): Confidence level for confidence intervals
        optimization_level (str): Optimization level used
    """

    def __init__(
        self,
        wavelet: str = "cmor1.5-1.0",
        scales: Optional[np.ndarray] = None,
        confidence: float = 0.95,
    ):
        """
        Initialize the NUMBA-optimized CWT estimator.

        Args:
            wavelet (str): Wavelet type for continuous transform (default: 'cmor1.5-1.0')
            scales (np.ndarray, optional): Array of scales for analysis.
                                         If None, uses automatic scale selection
            confidence (float): Confidence level for intervals (default: 0.95)
        """
        super().__init__()
        self.wavelet = wavelet
        self.confidence = confidence
        self.optimization_level = "NUMBA" if NUMBA_AVAILABLE else "Standard"

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
        self.execution_time = None

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
        Estimate the Hurst parameter using NUMBA-optimized Continuous Wavelet Transform analysis.

        Args:
            data (np.ndarray): Input time series data

        Returns:
            Dict[str, Any]: Dictionary containing estimation results
        """
        start_time = time.time()
        
        if len(data) < 100:
            raise ValueError("Data length must be at least 100 for CWT analysis")

        # Validate parameters
        self._validate_parameters()

        # Perform continuous wavelet transform (using pywt for the transform)
        self.wavelet_coeffs, frequencies = pywt.cwt(data, self.scales, self.wavelet)

        # NUMBA-optimized power spectrum calculation
        self.power_spectrum = _numba_calculate_power_spectrum(self.wavelet_coeffs)

        # NUMBA-optimized scale power calculation
        scale_powers_array = _numba_calculate_scale_powers(self.power_spectrum)
        
        # Store scale powers
        for i, scale in enumerate(self.scales):
            self.scale_powers[scale] = scale_powers_array[i]

        # Prepare data for linear regression
        log_scales = np.log10(self.scales)
        log_powers = np.log10(scale_powers_array)

        # NUMBA-optimized linear regression
        slope, intercept, r_squared = _numba_linear_regression(log_scales, log_powers)

        # Calculate Hurst parameter from slope
        # For fractional processes: H = (slope + 1) / 2
        self.estimated_hurst = (slope + 1) / 2
        self.r_squared = r_squared

        # Calculate confidence interval
        self.confidence_interval = self._calculate_confidence_interval(
            log_scales, log_powers, slope, intercept
        )

        # Calculate execution time
        self.execution_time = time.time() - start_time

        return {
            'hurst_parameter': self.estimated_hurst,
            'confidence_interval': self.confidence_interval,
            'r_squared': self.r_squared,
            'slope': slope,
            'intercept': intercept,
            'scale_powers': self.scale_powers,
            'scales': self.scales,
            'wavelet_coeffs': self.wavelet_coeffs,
            'power_spectrum': self.power_spectrum,
            'optimization_level': self.optimization_level,
            'execution_time': self.execution_time,
            'method': 'CWT (NUMBA-Optimized)'
        }

    def _calculate_confidence_interval(
        self, 
        x: np.ndarray, 
        y: np.ndarray, 
        slope: float, 
        intercept: float
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for the Hurst parameter estimate.
        
        Args:
            x: Log scales
            y: Log powers
            slope: Regression slope
            intercept: Regression intercept
            
        Returns:
            Confidence interval tuple
        """
        n = len(x)
        if n < 3:
            return (self.estimated_hurst, self.estimated_hurst)
        
        # Calculate residuals
        residuals = np.zeros(n)
        for i in range(n):
            y_pred = slope * x[i] + intercept
            residuals[i] = y[i] - y_pred
        
        # Calculate standard error of the slope
        x_mean = np.mean(x)
        ss_x = np.sum((x - x_mean) ** 2)
        
        if ss_x == 0:
            return (self.estimated_hurst, self.estimated_hurst)
        
        mse = np.sum(residuals ** 2) / (n - 2)
        se_slope = np.sqrt(mse / ss_x)
        
        # Calculate t-statistic for confidence interval
        t_value = stats.t.ppf((1 + self.confidence) / 2, n - 2)
        
        # Confidence interval for slope
        slope_ci = t_value * se_slope
        
        # Convert to Hurst parameter confidence interval
        hurst_lower = (slope - slope_ci + 1) / 2
        hurst_upper = (slope + slope_ci + 1) / 2
        
        return (hurst_lower, hurst_upper)

    def plot_scaling_behavior(self, save_path: Optional[str] = None) -> None:
        """
        Plot the scaling behavior and power spectrum.
        
        Args:
            save_path (str, optional): Path to save the plot
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Plot 1: Log-log plot of scale vs power
            scales = list(self.scale_powers.keys())
            powers = list(self.scale_powers.values())
            
            ax1.loglog(scales, powers, 'bo-', label='Data')
            ax1.set_xlabel('Scale')
            ax1.set_ylabel('Power')
            ax1.set_title('CWT Scaling Behavior')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Add regression line
            log_scales = np.log10(scales)
            log_powers = np.log10(powers)
            slope, intercept, _ = _numba_linear_regression(log_scales, log_powers)
            y_pred = slope * log_scales + intercept
            ax1.loglog(scales, 10**y_pred, 'r--', 
                      label=f'Fit (H={self.estimated_hurst:.3f})')
            ax1.legend()
            
            # Plot 2: Power spectrum heatmap
            im = ax2.imshow(np.log10(self.power_spectrum), 
                           aspect='auto', cmap='viridis')
            ax2.set_xlabel('Time')
            ax2.set_ylabel('Scale Index')
            ax2.set_title('CWT Power Spectrum (log scale)')
            plt.colorbar(im, ax=ax2)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.show()
            
        except ImportError:
            print("Matplotlib not available for plotting")

    def get_optimization_info(self) -> Dict[str, Any]:
        """
        Get information about the optimization level and performance.
        
        Returns:
            Dictionary with optimization information
        """
        return {
            'optimization_level': self.optimization_level,
            'numba_available': NUMBA_AVAILABLE,
            'execution_time': self.execution_time,
            'method': 'CWT (NUMBA-Optimized)'
        }
