#!/usr/bin/env python3
"""
Ultra-Optimized DFA Estimator for LRDBench

This module provides an ultra-optimized version of the DFA estimator
using the most efficient NumPy operations and minimal function calls.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class UltraOptimizedDFAEstimator(BaseEstimator):
    """
    Ultra-Optimized Detrended Fluctuation Analysis (DFA) estimator.

    This ultra-optimized version uses the most efficient NumPy operations
    and minimal function calls to achieve maximum performance improvements.

    Key optimizations:
    1. Direct NumPy polyfit instead of matrix operations
    2. Pre-allocated arrays for minimal memory allocation
    3. Vectorized operations wherever possible
    4. Minimal function call overhead
    5. Efficient array slicing and broadcasting

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

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_box_size = self.parameters["min_box_size"]
        polynomial_order = self.parameters["polynomial_order"]

        if min_box_size < 2:
            raise ValueError("min_box_size must be at least 2")

        if polynomial_order < 0:
            raise ValueError("polynomial_order must be non-negative")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using ultra-optimized DFA.

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
            box_sizes = np.array(self.parameters["box_sizes"])
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
            )

        # Calculate fluctuations using ultra-optimized method
        fluctuations = self._calculate_fluctuations_ultra_optimized(data, box_sizes)

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

    def _calculate_fluctuations_ultra_optimized(self, data: np.ndarray, box_sizes: np.ndarray) -> np.ndarray:
        """
        Ultra-optimized fluctuation calculation for all box sizes.
        
        This version uses the most efficient NumPy operations and minimal
        function calls for maximum performance.
        """
        n = len(data)
        polynomial_order = self.parameters["polynomial_order"]
        
        # Calculate cumulative sum once
        cumsum = np.cumsum(data - np.mean(data))
        
        # Pre-allocate array for results
        fluctuations = np.full(len(box_sizes), np.nan)
        
        # Process each box size
        for i, box_size in enumerate(box_sizes):
            if box_size > n:
                continue
            
            # Number of boxes
            n_boxes = n // box_size
            
            if n_boxes == 0:
                fluctuations[i] = 0.0
                continue
            
            # Calculate fluctuation using ultra-optimized method
            f = self._calculate_single_fluctuation_ultra_optimized(cumsum, box_size, n_boxes, polynomial_order)
            fluctuations[i] = f
        
        return fluctuations

    def _calculate_single_fluctuation_ultra_optimized(self, cumsum: np.ndarray, box_size: int, n_boxes: int, polynomial_order: int) -> float:
        """
        Ultra-optimized single fluctuation calculation.
        
        This version uses direct NumPy polyfit and minimal operations
        for maximum performance.
        """
        # Pre-allocate array for fluctuations
        fluctuations = np.empty(n_boxes)
        
        # Create x-coordinates once
        x = np.arange(box_size)
        
        # Process each box
        for i in range(n_boxes):
            start_idx = i * box_size
            end_idx = start_idx + box_size
            
            # Extract segment (view, no copy)
            segment = cumsum[start_idx:end_idx]
            
            # Ultra-fast polynomial fitting
            if polynomial_order == 0:
                # Constant trend (mean) - fastest possible
                trend = segment.mean()
            else:
                # Direct polyfit - much faster than matrix operations
                coeffs = np.polyfit(x, segment, polynomial_order)
                trend = np.polyval(coeffs, x)
            
            # Detrend and calculate fluctuation
            detrended = segment - trend
            fluctuations[i] = (detrended ** 2).mean()
        
        # Return root mean square fluctuation
        return np.sqrt(fluctuations.mean())


def benchmark_dfa_performance():
    """Benchmark the performance difference between original and ultra-optimized DFA."""
    import time
    from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    # Generate test data
    fgn = FractionalGaussianNoise(H=0.7)
    data_sizes = [1000, 5000, 10000]
    
    print("🚀 DFA Ultra-Optimization Benchmark")
    print("=" * 50)
    
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
        
        # Test ultra-optimized DFA
        try:
            ultra_optimized_dfa = UltraOptimizedDFAEstimator()
            
            start_time = time.time()
            result_ultra = ultra_optimized_dfa.estimate(data)
            time_ultra = time.time() - start_time
            
            print(f"Ultra-Optimized DFA: {time_ultra:.4f}s")
            
            if time_orig is not None:
                speedup = time_orig / time_ultra
                print(f"Speedup: {speedup:.2f}x")
            
            # Verify accuracy
            if time_orig is not None:
                h_diff = abs(result_orig['hurst_parameter'] - result_ultra['hurst_parameter'])
                print(f"Hurst difference: {h_diff:.6f}")
                
        except Exception as e:
            print(f"Ultra-Optimized DFA: Failed - {e}")


if __name__ == "__main__":
    benchmark_dfa_performance()
