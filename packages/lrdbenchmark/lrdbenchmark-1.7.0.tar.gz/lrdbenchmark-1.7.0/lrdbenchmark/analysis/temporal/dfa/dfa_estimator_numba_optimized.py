#!/usr/bin/env python3
"""
NUMBA-Optimized DFA Estimator for LRDBench

This module provides a NUMBA-optimized version of the DFA estimator
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
def _numba_calculate_fluctuation(cumsum, box_size, n_boxes, polynomial_order):
    """
    NUMBA-optimized fluctuation calculation.
    
    This function is compiled to machine code for maximum performance.
    """
    fluctuations = np.empty(n_boxes)
    x = np.arange(box_size, dtype=np.float64)
    
    for i in prange(n_boxes):
        start_idx = i * box_size
        end_idx = start_idx + box_size
        
        # Extract segment
        segment = cumsum[start_idx:end_idx]
        
        # Fast polynomial fitting
        if polynomial_order == 0:
            # Constant trend (mean)
            trend = np.mean(segment)
            detrended = segment - trend
        else:
            # Linear trend (polynomial_order == 1)
            # Use simple linear regression for speed
            n_points = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(segment)
            sum_xy = np.sum(x * segment)
            sum_x2 = np.sum(x * x)
            
            # Calculate slope and intercept
            slope = (n_points * sum_xy - sum_x * sum_y) / (n_points * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n_points
            
            # Calculate trend
            trend = slope * x + intercept
            detrended = segment - trend
        
        # Calculate fluctuation
        fluctuations[i] = np.mean(detrended * detrended)
    
    return np.sqrt(np.mean(fluctuations))


@jit(nopython=True, cache=True)
def _numba_calculate_fluctuations_all_sizes(cumsum, box_sizes, polynomial_order):
    """
    NUMBA-optimized calculation for all box sizes.
    """
    n = len(cumsum)
    n_sizes = len(box_sizes)
    fluctuations = np.full(n_sizes, np.nan)
    
    for i in range(n_sizes):
        box_size = box_sizes[i]
        
        if box_size > n:
            continue
        
        n_boxes = n // box_size
        
        if n_boxes == 0:
            fluctuations[i] = 0.0
            continue
        
        f = _numba_calculate_fluctuation(cumsum, box_size, n_boxes, polynomial_order)
        fluctuations[i] = f
    
    return fluctuations


class NumbaOptimizedDFAEstimator(BaseEstimator):
    """
    NUMBA-Optimized Detrended Fluctuation Analysis (DFA) estimator.

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
    min_box_size : int, default=4
        Minimum box size for analysis.
    max_box_size : int, optional
        Maximum box size for analysis. If None, uses n/4 where n is data length.
    box_sizes : List[int], optional
        Specific box sizes to use. If provided, overrides min/max.
    polynomial_order : int, default=1
        Order of polynomial for detrending.
    """

    def __init__(
        self,
        min_box_size: int = 4,
        max_box_size: int = None,
        box_sizes: List[int] = None,
        polynomial_order: int = 1,
    ):
        super().__init__(
            min_box_size=min_box_size,
            max_box_size=max_box_size,
            box_sizes=box_sizes,
            polynomial_order=polynomial_order,
        )
        self._validate_parameters()
        
        if not NUMBA_AVAILABLE:
            print("Warning: NUMBA not available. Performance may be limited.")

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_box_size = self.parameters["min_box_size"]
        polynomial_order = self.parameters["polynomial_order"]

        if min_box_size < 2:
            raise ValueError("min_box_size must be at least 2")

        if polynomial_order < 0:
            raise ValueError("polynomial_order must be non-negative")
        
        if polynomial_order > 1:
            print("Warning: NUMBA optimization currently supports polynomial_order <= 1")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using NUMBA-optimized DFA.

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

        # Determine box sizes
        if self.parameters["box_sizes"] is not None:
            box_sizes = np.array(self.parameters["box_sizes"], dtype=np.int32)
        else:
            min_size = self.parameters["min_box_size"]
            max_size = self.parameters["max_box_size"] or n // 4

            # Create box sizes with approximately equal spacing in log space
            box_sizes = np.unique(
                np.logspace(
                    np.log10(min_size),
                    np.log10(max_size),
                    num=min(20, max_size - min_size + 1),
                    dtype=int,
                )
            ).astype(np.int32)

        # Calculate cumulative sum once
        cumsum = np.cumsum(data - np.mean(data)).astype(np.float64)
        polynomial_order = self.parameters["polynomial_order"]

        # Use NUMBA-optimized calculation if available
        if NUMBA_AVAILABLE:
            fluctuations = _numba_calculate_fluctuations_all_sizes(cumsum, box_sizes, polynomial_order)
        else:
            # Fallback to standard implementation
            fluctuations = self._calculate_fluctuations_standard(cumsum, box_sizes, polynomial_order)

        # Filter out non-positive or non-finite fluctuations
        valid_mask = np.isfinite(fluctuations) & (fluctuations > 0)
        valid_box_sizes = box_sizes[valid_mask]
        valid_fluctuations = fluctuations[valid_mask]

        if len(valid_fluctuations) < 3:
            raise ValueError("Insufficient valid data points for DFA analysis")

        # Linear regression in log-log space
        log_sizes = np.log(valid_box_sizes.astype(float))
        log_fluctuations = np.log(valid_fluctuations.astype(float))

        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_sizes, log_fluctuations
        )

        # Hurst parameter is the slope
        H = slope

        # Store results
        self.results = {
            "hurst_parameter": H,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_error": std_err,
            "box_sizes": valid_box_sizes.tolist(),
            "fluctuations": valid_fluctuations.tolist(),
            "log_sizes": log_sizes,
            "log_fluctuations": log_fluctuations,
            "slope": slope,
            "n_points": len(valid_fluctuations),
        }

        return self.results

    def _calculate_fluctuations_standard(self, cumsum: np.ndarray, box_sizes: np.ndarray, polynomial_order: int) -> np.ndarray:
        """
        Standard fluctuation calculation (fallback when NUMBA is not available).
        """
        n = len(cumsum)
        fluctuations = np.full(len(box_sizes), np.nan)
        
        for i, box_size in enumerate(box_sizes):
            if box_size > n:
                continue
            
            n_boxes = n // box_size
            
            if n_boxes == 0:
                fluctuations[i] = 0.0
                continue
            
            # Calculate fluctuation for this box size
            box_fluctuations = []
            x = np.arange(box_size)
            
            for j in range(n_boxes):
                start_idx = j * box_size
                end_idx = start_idx + box_size
                segment = cumsum[start_idx:end_idx]
                
                if polynomial_order == 0:
                    trend = np.mean(segment)
                else:
                    coeffs = np.polyfit(x, segment, polynomial_order)
                    trend = np.polyval(coeffs, x)
                
                detrended = segment - trend
                box_fluctuations.append(np.mean(detrended**2))
            
            fluctuations[i] = np.sqrt(np.mean(box_fluctuations))
        
        return fluctuations


def benchmark_dfa_performance():
    """Benchmark the performance difference between original and NUMBA-optimized DFA."""
    import time
    from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    # Generate test data
    fgn = FractionalGaussianNoise(H=0.7)
    data_sizes = [1000, 5000, 10000]
    
    print("🚀 DFA NUMBA Optimization Benchmark")
    print("=" * 50)
    print(f"NUMBA Available: {NUMBA_AVAILABLE}")
    
    for size in data_sizes:
        print(f"\nData size: {size}")
        data = fgn.generate(size, seed=42)
        
        # Test original DFA
        try:
            from lrdbench.analysis.temporal.dfa.dfa_estimator import DFAEstimator
            original_dfa = DFAEstimator()
            
            start_time = time.time()
            result_orig = original_dfa.estimate(data)
            time_orig = time.time() - start_time
            
            print(f"Original DFA: {time_orig:.4f}s")
        except Exception as e:
            print(f"Original DFA: Failed - {e}")
            time_orig = None
        
        # Test NUMBA-optimized DFA
        try:
            numba_dfa = NumbaOptimizedDFAEstimator()
            
            start_time = time.time()
            result_numba = numba_dfa.estimate(data)
            time_numba = time.time() - start_time
            
            print(f"NUMBA-Optimized DFA: {time_numba:.4f}s")
            
            if time_orig is not None:
                speedup = time_orig / time_numba
                print(f"Speedup: {speedup:.2f}x")
            
            # Verify accuracy
            if time_orig is not None:
                h_diff = abs(result_orig['hurst_parameter'] - result_numba['hurst_parameter'])
                print(f"Hurst difference: {h_diff:.6f}")
                
        except Exception as e:
            print(f"NUMBA-Optimized DFA: Failed - {e}")


if __name__ == "__main__":
    benchmark_dfa_performance()
