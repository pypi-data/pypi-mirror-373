#!/usr/bin/env python3
"""
NUMBA-Optimized Periodogram Estimator for LRDBench

This module provides a NUMBA-optimized version of the Periodogram estimator
using JIT compilation for maximum performance improvements.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

# Try to import NUMBA, fall back gracefully if not available
try:
    import numba
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    print("Warning: NUMBA not available. Using standard implementation.")

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, parallel=True, cache=True)
def _numba_calculate_periodogram(data, frequencies):
    """
    NUMBA-optimized periodogram calculation.
    
    Parameters
    ----------
    data : np.ndarray
        Time series data
    frequencies : np.ndarray
        Array of frequencies to evaluate
        
    Returns
    -------
    np.ndarray
        Array of periodogram values
    """
    n = len(data)
    periodogram = np.zeros(len(frequencies))
    
    for i, freq in enumerate(frequencies):
        if freq <= 0:
            periodogram[i] = np.nan
            continue
            
        # Calculate periodogram at this frequency
        sum_real = 0.0
        sum_imag = 0.0
        
        for t in prange(n):
            phase = 2.0 * np.pi * freq * t
            sum_real += data[t] * np.cos(phase)
            sum_imag += data[t] * np.sin(phase)
        
        # Calculate power
        power = (sum_real**2 + sum_imag**2) / n
        periodogram[i] = power
    
    return periodogram


@jit(nopython=True, parallel=True, cache=True)
def _numba_calculate_periodogram_statistics(log_frequencies, log_periodogram):
    """
    NUMBA-optimized periodogram statistics calculation.
    
    Parameters
    ----------
    log_frequencies : np.ndarray
        Log of frequencies
    log_periodogram : np.ndarray
        Log of periodogram values
        
    Returns
    -------
    tuple
        (slope, intercept, r_squared)
    """
    n = len(log_frequencies)
    
    # Calculate sums
    sum_x = np.sum(log_frequencies)
    sum_y = np.sum(log_periodogram)
    sum_xy = np.sum(log_frequencies * log_periodogram)
    sum_x2 = np.sum(log_frequencies**2)
    
    # Calculate regression coefficients
    denominator = n * sum_x2 - sum_x**2
    if abs(denominator) < 1e-10:
        return np.nan, np.nan, 0.0
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    # Calculate R-squared
    y_pred = slope * log_frequencies + intercept
    ss_res = np.sum((log_periodogram - y_pred)**2)
    ss_tot = np.sum((log_periodogram - np.mean(log_periodogram))**2)
    
    if ss_tot < 1e-10:
        r_squared = 0.0
    else:
        r_squared = 1.0 - ss_res / ss_tot
    
    return slope, intercept, r_squared


class NumbaOptimizedPeriodogramEstimator(BaseEstimator):
    """
    NUMBA-Optimized Periodogram Estimator for analyzing long-range dependence.

    This version uses NUMBA JIT compilation to achieve maximum performance
    improvements while maintaining perfect accuracy.

    Key optimizations:
    1. JIT compilation of core calculation functions
    2. Parallel processing with prange
    3. Optimized memory access patterns
    4. Reduced Python overhead

    Parameters
    ----------
    min_freq : float, default=0.01
        Minimum frequency for analysis.
    max_freq : float, optional
        Maximum frequency for analysis. If None, uses 0.5.
    num_freqs : int, default=100
        Number of frequencies to use.
    """

    def __init__(
        self,
        min_freq: float = 0.01,
        max_freq: float = None,
        num_freqs: int = 100,
    ):
        super().__init__(
            min_freq=min_freq,
            max_freq=max_freq,
            num_freqs=num_freqs,
        )
        self._validate_parameters()
        
        if not NUMBA_AVAILABLE:
            print("Warning: NUMBA not available. Performance may be limited.")

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_freq = self.parameters["min_freq"]
        max_freq = self.parameters["max_freq"]
        num_freqs = self.parameters["num_freqs"]
        
        if min_freq <= 0:
            raise ValueError("min_freq must be positive")
        
        if max_freq is not None and max_freq <= min_freq:
            raise ValueError("max_freq must be greater than min_freq")
        
        if num_freqs < 10:
            raise ValueError("num_freqs must be at least 10")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using NUMBA-optimized Periodogram method.

        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        n = len(data)
        
        # Determine frequency range
        min_freq = self.parameters["min_freq"]
        max_freq = self.parameters["max_freq"] or 0.5
        num_freqs = self.parameters["num_freqs"]
        
        # Create frequency array
        frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), num_freqs)
        
        # Use NUMBA-optimized calculation if available
        if NUMBA_AVAILABLE:
            periodogram = _numba_calculate_periodogram(data, frequencies)
        else:
            # Fallback to standard implementation
            periodogram = self._calculate_periodogram_standard(data, frequencies)
        
        # Filter out non-positive or non-finite periodogram values
        valid_mask = np.isfinite(periodogram) & (periodogram > 0)
        valid_frequencies = frequencies[valid_mask]
        valid_periodogram = periodogram[valid_mask]
        
        if len(valid_periodogram) < 10:
            raise ValueError("Insufficient valid data points for Periodogram analysis")
        
        # Calculate log values
        log_frequencies = np.log(valid_frequencies)
        log_periodogram = np.log(valid_periodogram)
        
        # Use NUMBA-optimized regression if available
        if NUMBA_AVAILABLE:
            slope, intercept, r_squared = _numba_calculate_periodogram_statistics(
                log_frequencies, log_periodogram
            )
        else:
            # Fallback to standard regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                log_frequencies, log_periodogram
            )
            r_squared = r_value**2
        
        # Hurst parameter is related to the slope
        # For Periodogram method: H = (1 - slope) / 2
        H = (1 - slope) / 2
        
        # Store results
        self.results = {
            "hurst_parameter": H,
            "intercept": intercept,
            "r_squared": r_squared,
            "slope": slope,
            "frequencies": valid_frequencies.tolist(),
            "periodogram": valid_periodogram.tolist(),
            "log_frequencies": log_frequencies,
            "log_periodogram": log_periodogram,
            "n_points": len(valid_periodogram),
        }
        
        return self.results

    def _calculate_periodogram_standard(self, data: np.ndarray, frequencies: np.ndarray) -> np.ndarray:
        """
        Standard periodogram calculation (fallback when NUMBA is not available).
        """
        n = len(data)
        periodogram = np.zeros(len(frequencies))
        
        for i, freq in enumerate(frequencies):
            if freq <= 0:
                periodogram[i] = np.nan
                continue
                
            # Calculate periodogram at this frequency
            sum_real = 0.0
            sum_imag = 0.0
            
            for t in range(n):
                phase = 2.0 * np.pi * freq * t
                sum_real += data[t] * np.cos(phase)
                sum_imag += data[t] * np.sin(phase)
            
            # Calculate power
            power = (sum_real**2 + sum_imag**2) / n
            periodogram[i] = power
        
        return periodogram


def benchmark_periodogram_performance():
    """Benchmark the performance difference between original and NUMBA-optimized Periodogram."""
    import time
    from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    # Generate test data
    fgn = FractionalGaussianNoise(H=0.7)
    data_sizes = [1000, 5000, 10000]
    
    print("🚀 Periodogram NUMBA Optimization Benchmark")
    print("=" * 50)
    print(f"NUMBA Available: {NUMBA_AVAILABLE}")
    
    for size in data_sizes:
        print(f"\nData size: {size}")
        data = fgn.generate(size, seed=42)
        
        # Test original Periodogram
        try:
            from lrdbench.analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
            original_periodogram = PeriodogramEstimator()
            
            start_time = time.time()
            result_orig = original_periodogram.estimate(data)
            time_orig = time.time() - start_time
            
            print(f"Original Periodogram: {time_orig:.4f}s")
        except Exception as e:
            print(f"Original Periodogram: Failed - {e}")
            time_orig = None
        
        # Test NUMBA-optimized Periodogram
        try:
            numba_periodogram = NumbaOptimizedPeriodogramEstimator()
            
            start_time = time.time()
            result_numba = numba_periodogram.estimate(data)
            time_numba = time.time() - start_time
            
            print(f"NUMBA-Optimized Periodogram: {time_numba:.4f}s")
            
            if time_orig is not None:
                speedup = time_orig / time_numba
                print(f"Speedup: {speedup:.2f}x")
            
            # Verify accuracy
            if time_orig is not None:
                h_diff = abs(result_orig['hurst_parameter'] - result_numba['hurst_parameter'])
                print(f"Hurst difference: {h_diff:.6f}")
                
        except Exception as e:
            print(f"NUMBA-Optimized Periodogram: Failed - {e}")


if __name__ == "__main__":
    benchmark_periodogram_performance()
