"""
NUMBA-Optimized Multifractal Detrended Fluctuation Analysis (MFDFA) estimator.

This module provides a NUMBA-optimized version of the MFDFA estimator for significantly
improved performance in multifractal analysis calculations.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats, signal
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
def _numba_calculate_profile(data: np.ndarray) -> np.ndarray:
    """
    NUMBA-optimized calculation of the profile (cumulative sum).
    
    Args:
        data: Input time series
        
    Returns:
        Profile array
    """
    n = len(data)
    profile = np.empty(n + 1, dtype=np.float64)
    profile[0] = 0.0
    
    cumulative_sum = 0.0
    for i in prange(n):
        cumulative_sum += data[i]
        profile[i + 1] = cumulative_sum
    
    return profile


@jit(nopython=True, parallel=True)
def _numba_detrend_segments(profile: np.ndarray, scales: np.ndarray, q_values: np.ndarray) -> np.ndarray:
    """
    NUMBA-optimized detrending of segments for MFDFA.
    
    Args:
        profile: Cumulative sum profile
        scales: Array of scales
        q_values: Array of q values for multifractal analysis
        
    Returns:
        Array of fluctuation functions
    """
    n_scales = len(scales)
    n_q = len(q_values)
    fluctuation_functions = np.empty((n_scales, n_q), dtype=np.float64)
    
    for i in prange(n_scales):
        scale = scales[i]
        n_segments = int(len(profile) // scale)
        
        if n_segments == 0:
            for j in range(n_q):
                fluctuation_functions[i, j] = np.nan
            continue
        
        # Calculate fluctuation for each q value
        for j in range(n_q):
            q = q_values[j]
            total_fluctuation = 0.0
            
            for seg in range(n_segments):
                start_idx = int(seg * scale)
                end_idx = int((seg + 1) * scale)
                
                if end_idx > len(profile):
                    break
                
                # Extract segment
                segment = profile[start_idx:end_idx]
                n_points = len(segment)
                
                # Linear detrending
                x = np.arange(n_points, dtype=np.float64)
                x_mean = 0.0
                y_mean = 0.0
                
                for k in range(n_points):
                    x_mean += x[k]
                    y_mean += segment[k]
                x_mean /= n_points
                y_mean /= n_points
                
                # Calculate slope and intercept
                numerator = 0.0
                denominator = 0.0
                for k in range(n_points):
                    numerator += (x[k] - x_mean) * (segment[k] - y_mean)
                    denominator += (x[k] - x_mean) ** 2
                
                if denominator == 0.0:
                    slope = 0.0
                else:
                    slope = numerator / denominator
                
                intercept = y_mean - slope * x_mean
                
                # Calculate detrended fluctuation
                fluctuation = 0.0
                for k in range(n_points):
                    detrended = segment[k] - (slope * x[k] + intercept)
                    fluctuation += detrended * detrended
                fluctuation = np.sqrt(fluctuation / n_points)
                
                # Apply q-th power
                if q == 0:
                    total_fluctuation += np.log(fluctuation)
                else:
                    total_fluctuation += fluctuation ** q
            
            # Average over segments
            if q == 0:
                fluctuation_functions[i, j] = np.exp(total_fluctuation / n_segments)
            else:
                fluctuation_functions[i, j] = (total_fluctuation / n_segments) ** (1.0 / q)
    
    return fluctuation_functions


@jit(nopython=True)
def _numba_linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """
    NUMBA-optimized linear regression for slope calculation.
    
    Args:
        x: Independent variable (log scales)
        y: Dependent variable (log fluctuations)
        
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


class NumbaOptimizedMFDFAEstimator(BaseEstimator):
    """
    NUMBA-Optimized Multifractal Detrended Fluctuation Analysis (MFDFA) estimator.

    This estimator uses NUMBA-optimized MFDFA to analyze the multifractal scaling behavior
    of time series data and estimate the Hurst parameter with significantly improved performance.

    Attributes:
        scales (np.ndarray): Array of scales for analysis
        q_values (np.ndarray): Array of q values for multifractal analysis
        confidence (float): Confidence level for confidence intervals
        optimization_level (str): Optimization level used
    """

    def __init__(
        self,
        scales: Optional[np.ndarray] = None,
        q_values: Optional[np.ndarray] = None,
        confidence: float = 0.95,
    ):
        """
        Initialize the NUMBA-optimized MFDFA estimator.

        Args:
            scales (np.ndarray, optional): Array of scales for analysis.
                                         If None, uses automatic scale selection
            q_values (np.ndarray, optional): Array of q values for multifractal analysis.
                                           If None, uses default q values
            confidence (float): Confidence level for intervals (default: 0.95)
        """
        super().__init__()
        self.confidence = confidence
        self.optimization_level = "NUMBA" if NUMBA_AVAILABLE else "Standard"

        # Set default scales if not provided
        if scales is None:
            self.scales = np.array([16, 32, 64, 128, 256, 512])
        else:
            self.scales = scales

        # Set default q values if not provided
        if q_values is None:
            self.q_values = np.array([-5, -3, -1, 0, 1, 3, 5])
        else:
            self.q_values = q_values

        # Results storage
        self.profile = None
        self.fluctuation_functions = None
        self.hurst_exponents = {}
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
        if not isinstance(self.scales, np.ndarray) or len(self.scales) == 0:
            raise ValueError("scales must be a non-empty numpy array")
        if not isinstance(self.q_values, np.ndarray) or len(self.q_values) == 0:
            raise ValueError("q_values must be a non-empty numpy array")
        if not (0 < self.confidence < 1):
            raise ValueError("confidence must be between 0 and 1")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using NUMBA-optimized MFDFA analysis.

        Args:
            data (np.ndarray): Input time series data

        Returns:
            Dict[str, Any]: Dictionary containing estimation results
        """
        start_time = time.time()
        
        if len(data) < 100:
            raise ValueError("Data length must be at least 100 for MFDFA analysis")

        # Validate parameters
        self._validate_parameters()

        # Remove mean from data
        data_detrended = data - np.mean(data)

        # NUMBA-optimized profile calculation
        self.profile = _numba_calculate_profile(data_detrended)

        # NUMBA-optimized detrending and fluctuation calculation
        self.fluctuation_functions = _numba_detrend_segments(
            self.profile, self.scales, self.q_values
        )

        # Calculate Hurst exponents for each q value
        log_scales = np.log10(self.scales)
        
        for i, q in enumerate(self.q_values):
            log_fluctuations = np.log10(self.fluctuation_functions[:, i])
            
            # Remove NaN values
            valid_indices = ~np.isnan(log_fluctuations)
            if np.sum(valid_indices) < 2:
                self.hurst_exponents[q] = np.nan
                continue
            
            x_valid = log_scales[valid_indices]
            y_valid = log_fluctuations[valid_indices]
            
            # NUMBA-optimized linear regression
            slope, intercept, r_squared = _numba_linear_regression(x_valid, y_valid)
            self.hurst_exponents[q] = slope

        # Use q=2 for the main Hurst parameter estimate (standard DFA)
        if 2 in self.q_values:
            q2_index = np.where(self.q_values == 2)[0][0]
            self.estimated_hurst = self.hurst_exponents[2]
        else:
            # Use the average of available Hurst exponents
            valid_hurst = [h for h in self.hurst_exponents.values() if not np.isnan(h)]
            self.estimated_hurst = np.mean(valid_hurst) if valid_hurst else np.nan

        # Calculate confidence interval for q=2
        if 2 in self.q_values and not np.isnan(self.estimated_hurst):
            q2_index = np.where(self.q_values == 2)[0][0]
            log_fluctuations = np.log10(self.fluctuation_functions[:, q2_index])
            valid_indices = ~np.isnan(log_fluctuations)
            
            if np.sum(valid_indices) >= 3:
                x_valid = log_scales[valid_indices]
                y_valid = log_fluctuations[valid_indices]
                self.confidence_interval = self._calculate_confidence_interval(
                    x_valid, y_valid, self.estimated_hurst, 0.0
                )
            else:
                self.confidence_interval = (self.estimated_hurst, self.estimated_hurst)
        else:
            self.confidence_interval = (self.estimated_hurst, self.estimated_hurst)

        # Calculate execution time
        self.execution_time = time.time() - start_time

        return {
            'hurst_parameter': self.estimated_hurst,
            'confidence_interval': self.confidence_interval,
            'hurst_exponents': self.hurst_exponents,
            'q_values': self.q_values,
            'scales': self.scales,
            'fluctuation_functions': self.fluctuation_functions,
            'profile': self.profile,
            'optimization_level': self.optimization_level,
            'execution_time': self.execution_time,
            'method': 'MFDFA (NUMBA-Optimized)'
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
            y: Log fluctuations
            slope: Regression slope
            intercept: Regression intercept
            
        Returns:
            Confidence interval tuple
        """
        n = len(x)
        if n < 3:
            return (slope, slope)
        
        # Calculate residuals
        residuals = np.zeros(n)
        for i in range(n):
            y_pred = slope * x[i] + intercept
            residuals[i] = y[i] - y_pred
        
        # Calculate standard error of the slope
        x_mean = np.mean(x)
        ss_x = np.sum((x - x_mean) ** 2)
        
        if ss_x == 0:
            return (slope, slope)
        
        mse = np.sum(residuals ** 2) / (n - 2)
        se_slope = np.sqrt(mse / ss_x)
        
        # Calculate t-statistic for confidence interval
        t_value = stats.t.ppf((1 + self.confidence) / 2, n - 2)
        
        # Confidence interval for slope
        slope_ci = t_value * se_slope
        
        return (slope - slope_ci, slope + slope_ci)

    def plot_scaling_behavior(self, save_path: Optional[str] = None) -> None:
        """
        Plot the scaling behavior and multifractal spectrum.
        
        Args:
            save_path (str, optional): Path to save the plot
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Plot 1: Log-log plot of scale vs fluctuation for different q values
            log_scales = np.log10(self.scales)
            
            for i, q in enumerate(self.q_values):
                log_fluctuations = np.log10(self.fluctuation_functions[:, i])
                valid_indices = ~np.isnan(log_fluctuations)
                
                if np.sum(valid_indices) > 0:
                    ax1.plot(log_scales[valid_indices], log_fluctuations[valid_indices], 
                            'o-', label=f'q={q}')
            
            ax1.set_xlabel('log(Scale)')
            ax1.set_ylabel('log(F(q,s))')
            ax1.set_title('MFDFA Scaling Behavior')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Plot 2: Multifractal spectrum (H(q) vs q)
            valid_q = []
            valid_h = []
            for q, h in self.hurst_exponents.items():
                if not np.isnan(h):
                    valid_q.append(q)
                    valid_h.append(h)
            
            if valid_q:
                ax2.plot(valid_q, valid_h, 'bo-', label='H(q)')
                ax2.axhline(y=self.estimated_hurst, color='r', linestyle='--', 
                           label=f'H(2)={self.estimated_hurst:.3f}')
                ax2.set_xlabel('q')
                ax2.set_ylabel('H(q)')
                ax2.set_title('Multifractal Spectrum')
                ax2.grid(True, alpha=0.3)
                ax2.legend()
            
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
            'method': 'MFDFA (NUMBA-Optimized)'
        }
