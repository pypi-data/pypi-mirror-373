#!/usr/bin/env python3
"""
NUMBA-Optimized Rescaled Range (R/S) Analysis estimator.

This module provides a NUMBA-optimized version of the RSEstimator class
using JIT compilation for maximum performance.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

# Try to import numba, fall back gracefully if not available
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
def _numba_calculate_rs_single_window(window):
    """
    NUMBA-optimized R/S calculation for a single window.
    
    This function is compiled to machine code for maximum performance.
    """
    n = len(window)
    
    # Calculate mean
    mean_val = 0.0
    for i in range(n):
        mean_val += window[i]
    mean_val /= n
    
    # Calculate cumulative deviation
    cum_dev = np.empty(n)
    cum_dev[0] = window[0] - mean_val
    for i in range(1, n):
        cum_dev[i] = cum_dev[i-1] + (window[i] - mean_val)
    
    # Calculate range
    min_val = cum_dev[0]
    max_val = cum_dev[0]
    for i in range(1, n):
        if cum_dev[i] < min_val:
            min_val = cum_dev[i]
        if cum_dev[i] > max_val:
            max_val = cum_dev[i]
    R = max_val - min_val
    
    # Calculate standard deviation (sample std)
    variance = 0.0
    for i in range(n):
        diff = window[i] - mean_val
        variance += diff * diff
    variance /= (n - 1)  # Sample variance
    S = np.sqrt(variance)
    
    # Return R/S value
    if S > 0:
        return R / S
    else:
        return 0.0


@jit(nopython=True, parallel=True, cache=True)
def _numba_calculate_rs_all_windows(data, scale):
    """
    NUMBA-optimized R/S calculation for all windows of a given scale.
    """
    n = len(data)
    num_windows = n // scale
    
    if num_windows == 0:
        return 0.0
    
    rs_values = np.empty(num_windows)
    
    for i in prange(num_windows):
        start_idx = i * scale
        end_idx = start_idx + scale
        window = data[start_idx:end_idx]
        rs_values[i] = _numba_calculate_rs_single_window(window)
    
    # Calculate mean R/S value
    sum_rs = 0.0
    count = 0
    for i in range(num_windows):
        if rs_values[i] > 0:
            sum_rs += rs_values[i]
            count += 1
    
    if count > 0:
        return sum_rs / count
    else:
        return 0.0


@jit(nopython=True, cache=True)
def _numba_calculate_rs_all_scales(data, scales):
    """
    NUMBA-optimized R/S calculation for all scales.
    """
    n_scales = len(scales)
    rs_values = np.empty(n_scales)
    
    for i in range(n_scales):
        scale = scales[i]
        rs_values[i] = _numba_calculate_rs_all_windows(data, scale)
    
    return rs_values


class NumbaOptimizedRSEstimator(BaseEstimator):
    """
    NUMBA-Optimized Rescaled Range (R/S) Analysis estimator.

    This version uses NUMBA JIT compilation to achieve maximum performance
    improvements by compiling Python functions to machine code.

    Key optimizations:
    1. JIT compilation of core numerical functions
    2. Parallel processing with prange
    3. Optimized memory access patterns
    4. Minimal Python overhead in hot loops
    5. Cached compilation for repeated calls

    Parameters
    ----------
    min_window_size : int, default=10
        Minimum window size to use.
    max_window_size : int, optional
        Maximum window size to use. If None, uses n/4 where n is data length.
    window_sizes : List[int], optional
        Specific window sizes to use. If provided, overrides min/max.
    overlap : bool, default=False
        Whether to use overlapping windows.
    """

    def __init__(
        self,
        min_window_size: int = 10,
        max_window_size: int = None,
        window_sizes: List[int] = None,
        overlap: bool = False,
    ):
        super().__init__(
            min_window_size=min_window_size,
            max_window_size=max_window_size,
            window_sizes=window_sizes,
            overlap=overlap,
        )
        self._validate_parameters()
        
        if not NUMBA_AVAILABLE:
            print("Warning: NUMBA not available. Performance may be limited.")

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["window_sizes"] is not None:
            if len(self.parameters["window_sizes"]) < 3:
                raise ValueError("Need at least 3 window sizes")
            if any(w < 4 for w in self.parameters["window_sizes"]):
                raise ValueError("All window sizes must be at least 4")
            if not all(
                self.parameters["window_sizes"][i]
                < self.parameters["window_sizes"][i + 1]
                for i in range(len(self.parameters["window_sizes"]) - 1)
            ):
                raise ValueError("Window sizes must be in ascending order")
        else:
            if self.parameters["min_window_size"] < 4:
                raise ValueError("min_window_size must be at least 4")
            if (
                self.parameters["max_window_size"] is not None
                and self.parameters["max_window_size"]
                <= self.parameters["min_window_size"]
            ):
                raise ValueError("max_window_size must be greater than min_window_size")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using NUMBA-optimized R/S analysis.

        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        # Determine window sizes
        if self.parameters["window_sizes"] is not None:
            window_sizes = np.array(self.parameters["window_sizes"], dtype=np.int32)
        else:
            if self.parameters["max_window_size"] is None:
                max_window_size = len(data) // 4
            else:
                max_window_size = min(
                    self.parameters["max_window_size"], len(data) // 4
                )

            if max_window_size <= self.parameters["min_window_size"]:
                raise ValueError("Need at least 3 window sizes")

            # Generate window sizes
            window_sizes = np.logspace(
                np.log10(self.parameters["min_window_size"]),
                np.log10(max_window_size),
                20,
                dtype=int,
            )
            window_sizes = np.unique(window_sizes).astype(np.int32)

        if len(data) < min(window_sizes) * 2:
            raise ValueError(
                f"Data length ({len(data)}) must be at least {min(window_sizes) * 2}"
            )

        if len(window_sizes) < 3:
            raise ValueError("Need at least 3 window sizes")

        # Convert data to float64 for NUMBA
        data_float64 = data.astype(np.float64)

        # Use NUMBA-optimized calculation if available
        if NUMBA_AVAILABLE:
            rs_values = _numba_calculate_rs_all_scales(data_float64, window_sizes)
        else:
            # Fallback to standard implementation
            rs_values = self._calculate_rs_standard(data, window_sizes)

        # Filter out non-positive or non-finite RS values
        valid_mask = np.isfinite(rs_values) & (rs_values > 0)
        valid_window_sizes = window_sizes[valid_mask]
        valid_rs_values = rs_values[valid_mask]

        if len(valid_rs_values) < 3:
            raise ValueError("Insufficient valid R/S values for analysis")

        # Fit power law: R/S ~ scale^H
        log_scales = np.log(valid_window_sizes.astype(float))
        log_rs = np.log(valid_rs_values.astype(float))

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_scales, log_rs
        )

        # Store results
        self.results = {
            "hurst_parameter": slope,
            "window_sizes": valid_window_sizes.tolist(),
            "rs_values": valid_rs_values.tolist(),
            "r_squared": r_value**2,
            "std_error": std_err,
            "confidence_interval": (slope - 1.96 * std_err, slope + 1.96 * std_err),
            "p_value": p_value,
            "intercept": intercept,
            "slope": slope,
            "log_scales": log_scales,
            "log_rs": log_rs,
        }

        return self.results

    def _calculate_rs_standard(self, data: np.ndarray, window_sizes: np.ndarray) -> np.ndarray:
        """
        Standard R/S calculation (fallback when NUMBA is not available).
        """
        rs_values = []
        
        for scale in window_sizes:
            n = len(data)
            num_windows = n // scale

            if num_windows == 0:
                rs_values.append(0.0)
                continue

            window_rs_values = []

            for i in range(num_windows):
                start_idx = i * scale
                end_idx = start_idx + scale
                window = data[start_idx:end_idx]

                # Calculate mean
                mean_val = np.mean(window)

                # Calculate cumulative deviation
                dev = window - mean_val
                cum_dev = np.cumsum(dev)

                # Calculate range
                R = np.max(cum_dev) - np.min(cum_dev)

                # Calculate standard deviation (sample std)
                S = np.std(window, ddof=1)

                # Avoid division by zero
                if S > 0:
                    window_rs_values.append(R / S)

            # Return mean R/S value
            if window_rs_values:
                rs_values.append(np.mean(window_rs_values))
            else:
                rs_values.append(0.0)
        
        return np.array(rs_values)


def benchmark_rs_performance():
    """Benchmark the performance difference between original and NUMBA-optimized RS."""
    import time
    from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    # Generate test data
    fgn = FractionalGaussianNoise(H=0.7)
    data_sizes = [1000, 5000, 10000]
    
    print("🚀 RS NUMBA Optimization Benchmark")
    print("=" * 50)
    print(f"NUMBA Available: {NUMBA_AVAILABLE}")
    
    for size in data_sizes:
        print(f"\nData size: {size}")
        data = fgn.generate(size, seed=42)
        
        # Test original RS
        try:
            from lrdbench.analysis.temporal.rs.rs_estimator import RSEstimator
            original_rs = RSEstimator()
            
            start_time = time.time()
            result_orig = original_rs.estimate(data)
            time_orig = time.time() - start_time
            
            print(f"Original RS: {time_orig:.4f}s")
        except Exception as e:
            print(f"Original RS: Failed - {e}")
            time_orig = None
        
        # Test NUMBA-optimized RS
        try:
            numba_rs = NumbaOptimizedRSEstimator()
            
            start_time = time.time()
            result_numba = numba_rs.estimate(data)
            time_numba = time.time() - start_time
            
            print(f"NUMBA-Optimized RS: {time_numba:.4f}s")
            
            if time_orig is not None:
                speedup = time_orig / time_numba
                print(f"Speedup: {speedup:.2f}x")
            
            # Verify accuracy
            if time_orig is not None:
                h_diff = abs(result_orig['hurst_parameter'] - result_numba['hurst_parameter'])
                print(f"Hurst difference: {h_diff:.6f}")
                
        except Exception as e:
            print(f"NUMBA-Optimized RS: Failed - {e}")


if __name__ == "__main__":
    benchmark_rs_performance()
