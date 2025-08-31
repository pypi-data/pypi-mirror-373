#!/usr/bin/env python3
"""
JAX-Optimized DFA Estimator for LRDBench

This module provides a JAX-optimized version of the DFA estimator
using GPU acceleration and vectorized operations.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

# Try to import JAX, fall back gracefully if not available
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap
    JAX_AVAILABLE = True
    print(f"JAX available: {jax.devices()}")
except ImportError:
    JAX_AVAILABLE = False
    print("Warning: JAX not available. Using standard implementation.")

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


@jit
def _jax_calculate_fluctuation(cumsum, box_size, n_boxes, polynomial_order):
    """
    JAX-optimized fluctuation calculation.
    
    This function is compiled and can run on GPU if available.
    """
    def process_box(i):
        start_idx = i * box_size
        end_idx = start_idx + box_size
        segment = cumsum[start_idx:end_idx]
        
        if polynomial_order == 0:
            # Constant trend (mean)
            trend = jnp.mean(segment)
            detrended = segment - trend
        else:
            # Linear trend (polynomial_order == 1)
            x = jnp.arange(box_size, dtype=jnp.float32)
            n_points = box_size
            
            sum_x = jnp.sum(x)
            sum_y = jnp.sum(segment)
            sum_xy = jnp.sum(x * segment)
            sum_x2 = jnp.sum(x * x)
            
            # Calculate slope and intercept
            slope = (n_points * sum_xy - sum_x * sum_y) / (n_points * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n_points
            
            # Calculate trend
            trend = slope * x + intercept
            detrended = segment - trend
        
        return jnp.mean(detrended * detrended)
    
    # Vectorize over all boxes
    box_fluctuations = vmap(process_box)(jnp.arange(n_boxes))
    return jnp.sqrt(jnp.mean(box_fluctuations))


@jit
def _jax_calculate_fluctuations_all_sizes(cumsum, box_sizes, polynomial_order):
    """
    JAX-optimized calculation for all box sizes.
    """
    n = len(cumsum)
    
    def process_box_size(box_size):
        # Use JAX conditional functions instead of Python if statements
        n_boxes = jax.lax.cond(
            box_size > n,
            lambda _: 0,  # If box_size > n, return 0 boxes
            lambda _: n // box_size,  # Otherwise, calculate n_boxes
            operand=None
        )
        
        return jax.lax.cond(
            n_boxes == 0,
            lambda _: jnp.nan,  # If no boxes, return NaN
            lambda _: _jax_calculate_fluctuation(cumsum, box_size, n_boxes, polynomial_order),  # Otherwise, calculate
            operand=None
        )
    
    # Vectorize over all box sizes
    return vmap(process_box_size)(box_sizes)


class JaxOptimizedDFAEstimator(BaseEstimator):
    """
    JAX-Optimized Detrended Fluctuation Analysis (DFA) estimator.

    This version uses JAX for GPU acceleration and vectorized operations
    to achieve maximum performance improvements.

    Key optimizations:
    1. GPU acceleration (if available)
    2. JIT compilation of core functions
    3. Vectorized operations with vmap
    4. Automatic differentiation capabilities
    5. Efficient memory management

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
        
        if not JAX_AVAILABLE:
            print("Warning: JAX not available. Performance may be limited.")

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_box_size = self.parameters["min_box_size"]
        polynomial_order = self.parameters["polynomial_order"]

        if min_box_size < 2:
            raise ValueError("min_box_size must be at least 2")

        if polynomial_order < 0:
            raise ValueError("polynomial_order must be non-negative")
        
        if polynomial_order > 1:
            print("Warning: JAX optimization currently supports polynomial_order <= 1")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using JAX-optimized DFA.

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
        cumsum = np.cumsum(data - np.mean(data)).astype(np.float32)
        polynomial_order = self.parameters["polynomial_order"]

        # Use JAX-optimized calculation if available
        if JAX_AVAILABLE:
            # Convert to JAX arrays
            cumsum_jax = jnp.array(cumsum)
            box_sizes_jax = jnp.array(box_sizes)
            
            # Calculate fluctuations using JAX
            fluctuations_jax = _jax_calculate_fluctuations_all_sizes(cumsum_jax, box_sizes_jax, polynomial_order)
            fluctuations = np.array(fluctuations_jax)
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
        Standard fluctuation calculation (fallback when JAX is not available).
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
    """Benchmark the performance difference between original and JAX-optimized DFA."""
    import time
    from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    # Generate test data
    fgn = FractionalGaussianNoise(H=0.7)
    data_sizes = [1000, 5000, 10000]
    
    print("🚀 DFA JAX Optimization Benchmark")
    print("=" * 50)
    print(f"JAX Available: {JAX_AVAILABLE}")
    
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
        
        # Test JAX-optimized DFA
        try:
            jax_dfa = JaxOptimizedDFAEstimator()
            
            start_time = time.time()
            result_jax = jax_dfa.estimate(data)
            time_jax = time.time() - start_time
            
            print(f"JAX-Optimized DFA: {time_jax:.4f}s")
            
            if time_orig is not None:
                speedup = time_orig / time_jax
                print(f"Speedup: {speedup:.2f}x")
            
            # Verify accuracy
            if time_orig is not None:
                h_diff = abs(result_orig['hurst_parameter'] - result_jax['hurst_parameter'])
                print(f"Hurst difference: {h_diff:.6f}")
                
        except Exception as e:
            print(f"JAX-Optimized DFA: Failed - {e}")


if __name__ == "__main__":
    benchmark_dfa_performance()
