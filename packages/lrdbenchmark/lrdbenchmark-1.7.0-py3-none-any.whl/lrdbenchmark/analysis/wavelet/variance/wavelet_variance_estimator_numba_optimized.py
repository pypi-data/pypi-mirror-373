"""
NUMBA-Optimized Wavelet Variance Analysis estimator.

This module provides a NUMBA-optimized version of the Wavelet Variance estimator for significantly
improved performance in wavelet variance calculations.
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
def _numba_wavelet_decomposition(data: np.ndarray, wavelet: str, level: int) -> List[np.ndarray]:
    """
    NUMBA-optimized wavelet decomposition.
    
    Args:
        data: Input time series
        wavelet: Wavelet type
        level: Decomposition level
        
    Returns:
        List of wavelet coefficients
    """
    # This is a simplified version - in practice, we'll use pywt for the actual decomposition
    # and NUMBA for the variance calculations
    coeffs = []
    current_data = data.copy()
    
    for i in range(level):
        # Simplified wavelet transform (this would be replaced with actual pywt call)
        n = len(current_data)
        half = n // 2
        
        # Approximate coefficients (low-pass)
        approx = np.empty(half)
        for j in prange(half):
            if 2*j + 1 < n:
                approx[j] = (current_data[2*j] + current_data[2*j + 1]) / 2.0
            else:
                approx[j] = current_data[2*j]
        
        # Detail coefficients (high-pass)
        detail = np.empty(half)
        for j in prange(half):
            if 2*j + 1 < n:
                detail[j] = (current_data[2*j] - current_data[2*j + 1]) / 2.0
            else:
                detail[j] = 0.0
        
        coeffs.append(detail)
        current_data = approx
    
    coeffs.append(current_data)
    return coeffs


@jit(nopython=True, parallel=True)
def _numba_calculate_wavelet_variance(coeffs: List[np.ndarray]) -> np.ndarray:
    """
    NUMBA-optimized calculation of wavelet variance at each scale.
    
    Args:
        coeffs: List of wavelet coefficients
        
    Returns:
        Array of wavelet variances
    """
    n_scales = len(coeffs) - 1  # Exclude the approximation coefficients
    variances = np.empty(n_scales, dtype=np.float64)
    
    for i in prange(n_scales):
        detail_coeffs = coeffs[i]
        n_coeffs = len(detail_coeffs)
        
        if n_coeffs == 0:
            variances[i] = 0.0
            continue
        
        # Calculate mean
        mean_val = 0.0
        for j in range(n_coeffs):
            mean_val += detail_coeffs[j]
        mean_val /= n_coeffs
        
        # Calculate variance
        variance = 0.0
        for j in range(n_coeffs):
            diff = detail_coeffs[j] - mean_val
            variance += diff * diff
        variance /= n_coeffs
        
        variances[i] = variance
    
    return variances


@jit(nopython=True)
def _numba_linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """
    NUMBA-optimized linear regression for slope calculation.
    
    Args:
        x: Independent variable (log scales)
        y: Dependent variable (log variances)
        
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


class NumbaOptimizedWaveletVarianceEstimator(BaseEstimator):
    """
    NUMBA-Optimized Wavelet Variance Analysis estimator.

    This estimator uses NUMBA-optimized wavelet variance analysis to estimate the Hurst parameter
    from time series data with significantly improved performance.

    Attributes:
        wavelet (str): Wavelet type to use for decomposition
        level (int): Maximum decomposition level
        confidence (float): Confidence level for confidence intervals
        optimization_level (str): Optimization level used
    """

    def __init__(
        self,
        wavelet: str = "db4",
        level: Optional[int] = None,
        confidence: float = 0.95,
    ):
        """
        Initialize the NUMBA-optimized Wavelet Variance estimator.

        Args:
            wavelet (str): Wavelet type for decomposition (default: 'db4')
            level (int, optional): Maximum decomposition level.
                                 If None, uses automatic level selection
            confidence (float): Confidence level for intervals (default: 0.95)
        """
        super().__init__()
        self.wavelet = wavelet
        self.confidence = confidence
        self.optimization_level = "NUMBA" if NUMBA_AVAILABLE else "Standard"

        # Set default level if not provided
        if level is None:
            self.level = None  # Will be set automatically
        else:
            self.level = level

        # Results storage
        self.wavelet_coeffs = None
        self.wavelet_variances = {}
        self.scales = None
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
        if self.level is not None and (not isinstance(self.level, int) or self.level <= 0):
            raise ValueError("level must be a positive integer")
        if not (0 < self.confidence < 1):
            raise ValueError("confidence must be between 0 and 1")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using NUMBA-optimized Wavelet Variance analysis.

        Args:
            data (np.ndarray): Input time series data

        Returns:
            Dict[str, Any]: Dictionary containing estimation results
        """
        start_time = time.time()
        
        if len(data) < 100:
            raise ValueError("Data length must be at least 100 for wavelet variance analysis")

        # Validate parameters
        self._validate_parameters()

        # Determine decomposition level if not specified
        if self.level is None:
            self.level = pywt.dwt_max_level(len(data), pywt.Wavelet(self.wavelet).dec_len)

        # Perform wavelet decomposition using pywt
        self.wavelet_coeffs = pywt.wavedec(data, self.wavelet, level=self.level)

        # NUMBA-optimized variance calculation
        variance_array = _numba_calculate_wavelet_variance(self.wavelet_coeffs)

        # Create scales array (powers of 2)
        self.scales = np.array([2**i for i in range(1, len(variance_array) + 1)])

        # Store wavelet variances
        for i, scale in enumerate(self.scales):
            self.wavelet_variances[scale] = variance_array[i]

        # Prepare data for linear regression (log-log plot)
        log_scales = np.log10(self.scales)
        log_variances = np.log10(variance_array)

        # NUMBA-optimized linear regression
        slope, intercept, r_squared = _numba_linear_regression(log_scales, log_variances)

        # Calculate Hurst parameter from slope
        # For fractional processes: H = (slope + 1) / 2
        self.estimated_hurst = (slope + 1) / 2
        self.r_squared = r_squared

        # Calculate confidence interval
        self.confidence_interval = self._calculate_confidence_interval(
            log_scales, log_variances, slope, intercept
        )

        # Calculate execution time
        self.execution_time = time.time() - start_time

        return {
            'hurst_parameter': self.estimated_hurst,
            'confidence_interval': self.confidence_interval,
            'r_squared': self.r_squared,
            'slope': slope,
            'intercept': intercept,
            'wavelet_variances': self.wavelet_variances,
            'scales': self.scales,
            'wavelet_coeffs': self.wavelet_coeffs,
            'level': self.level,
            'optimization_level': self.optimization_level,
            'execution_time': self.execution_time,
            'method': 'Wavelet Variance (NUMBA-Optimized)'
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
            y: Log variances
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
        Plot the scaling behavior and wavelet coefficients.
        
        Args:
            save_path (str, optional): Path to save the plot
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Plot 1: Log-log plot of scale vs variance
            scales = list(self.wavelet_variances.keys())
            variances = list(self.wavelet_variances.values())
            
            ax1.loglog(scales, variances, 'bo-', label='Data')
            ax1.set_xlabel('Scale')
            ax1.set_ylabel('Wavelet Variance')
            ax1.set_title('Wavelet Variance Scaling Behavior')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Add regression line
            log_scales = np.log10(scales)
            log_variances = np.log10(variances)
            slope, intercept, _ = _numba_linear_regression(log_scales, log_variances)
            y_pred = slope * log_scales + intercept
            ax1.loglog(scales, 10**y_pred, 'r--', 
                      label=f'Fit (H={self.estimated_hurst:.3f})')
            ax1.legend()
            
            # Plot 2: Wavelet coefficients
            for i, coeffs in enumerate(self.wavelet_coeffs[1:], 1):
                ax2.plot(coeffs, label=f'Level {i}')
            ax2.set_xlabel('Time')
            ax2.set_ylabel('Coefficient Value')
            ax2.set_title('Wavelet Detail Coefficients')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
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
            'method': 'Wavelet Variance (NUMBA-Optimized)'
        }
