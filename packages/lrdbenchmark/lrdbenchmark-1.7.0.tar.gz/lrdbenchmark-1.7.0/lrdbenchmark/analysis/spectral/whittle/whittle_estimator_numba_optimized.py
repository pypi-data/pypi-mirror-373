#!/usr/bin/env python3
"""
NUMBA-Optimized Whittle Estimator for LRDBench

This module provides a NUMBA-optimized version of the Whittle estimator
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
def _numba_calculate_whittle_likelihood(hurst, frequencies, periodogram):
    """
    NUMBA-optimized Whittle likelihood calculation.
    
    Parameters
    ----------
    hurst : float
        Hurst parameter
    frequencies : np.ndarray
        Array of frequencies
    periodogram : np.ndarray
        Array of periodogram values
        
    Returns
    -------
    float
        Negative log-likelihood
    """
    n = len(frequencies)
    likelihood = 0.0
    
    for i in prange(n):
        freq = frequencies[i]
        if freq <= 0:
            continue
            
        # Theoretical spectrum for fractional Gaussian noise
        # S(f) = |f|^(-2H + 1)
        theoretical_spectrum = freq**(-2.0 * hurst + 1.0)
        
        # Whittle likelihood
        likelihood += np.log(theoretical_spectrum) + periodogram[i] / theoretical_spectrum
    
    return likelihood


@jit(nopython=True, parallel=True, cache=True)
def _numba_optimize_whittle_likelihood(frequencies, periodogram, h_range):
    """
    NUMBA-optimized Whittle likelihood optimization.
    
    Parameters
    ----------
    frequencies : np.ndarray
        Array of frequencies
    periodogram : np.ndarray
        Array of periodogram values
    h_range : np.ndarray
        Range of H values to test
        
    Returns
    -------
    tuple
        (best_h, best_likelihood)
    """
    best_h = 0.5
    best_likelihood = np.inf
    
    for h in h_range:
        likelihood = _numba_calculate_whittle_likelihood(h, frequencies, periodogram)
        if likelihood < best_likelihood:
            best_likelihood = likelihood
            best_h = h
    
    return best_h, best_likelihood


class NumbaOptimizedWhittleEstimator(BaseEstimator):
    """
    NUMBA-Optimized Whittle Estimator for analyzing long-range dependence.

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
    h_range : List[float], optional
        Range of H values to test. If None, uses [0.1, 0.9] with 0.01 step.
    """

    def __init__(
        self,
        min_freq: float = 0.01,
        max_freq: float = None,
        num_freqs: int = 100,
        h_range: List[float] = None,
    ):
        super().__init__(
            min_freq=min_freq,
            max_freq=max_freq,
            num_freqs=num_freqs,
            h_range=h_range,
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
        Estimate Hurst parameter using NUMBA-optimized Whittle method.

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
            raise ValueError("Insufficient valid data points for Whittle analysis")
        
        # Determine H range for optimization
        h_range = self.parameters["h_range"]
        if h_range is None:
            h_range = np.arange(0.1, 0.9, 0.01)
        else:
            h_range = np.array(h_range)
        
        # Use NUMBA-optimized optimization if available
        if NUMBA_AVAILABLE:
            H, likelihood = _numba_optimize_whittle_likelihood(
                valid_frequencies, valid_periodogram, h_range
            )
        else:
            # Fallback to standard optimization
            H, likelihood = self._optimize_whittle_likelihood_standard(
                valid_frequencies, valid_periodogram, h_range
            )
        
        # Store results
        self.results = {
            "hurst_parameter": H,
            "likelihood": likelihood,
            "frequencies": valid_frequencies.tolist(),
            "periodogram": valid_periodogram.tolist(),
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

    def _optimize_whittle_likelihood_standard(self, frequencies: np.ndarray, periodogram: np.ndarray, h_range: np.ndarray) -> Tuple[float, float]:
        """
        Standard Whittle likelihood optimization (fallback when NUMBA is not available).
        """
        best_h = 0.5
        best_likelihood = np.inf
        
        for h in h_range:
            likelihood = 0.0
            for i, freq in enumerate(frequencies):
                if freq <= 0:
                    continue
                    
                # Theoretical spectrum for fractional Gaussian noise
                theoretical_spectrum = freq**(-2.0 * h + 1.0)
                
                # Whittle likelihood
                likelihood += np.log(theoretical_spectrum) + periodogram[i] / theoretical_spectrum
            
            if likelihood < best_likelihood:
                best_likelihood = likelihood
                best_h = h
        
        return best_h, best_likelihood


def benchmark_whittle_performance():
    """Benchmark the performance difference between original and NUMBA-optimized Whittle."""
    import time
    from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    # Generate test data
    fgn = FractionalGaussianNoise(H=0.7)
    data_sizes = [1000, 5000, 10000]
    
    print("🚀 Whittle NUMBA Optimization Benchmark")
    print("=" * 50)
    print(f"NUMBA Available: {NUMBA_AVAILABLE}")
    
    for size in data_sizes:
        print(f"\nData size: {size}")
        data = fgn.generate(size, seed=42)
        
        # Test original Whittle
        try:
            from lrdbench.analysis.spectral.whittle.whittle_estimator import WhittleEstimator
            original_whittle = WhittleEstimator()
            
            start_time = time.time()
            result_orig = original_whittle.estimate(data)
            time_orig = time.time() - start_time
            
            print(f"Original Whittle: {time_orig:.4f}s")
        except Exception as e:
            print(f"Original Whittle: Failed - {e}")
            time_orig = None
        
        # Test NUMBA-optimized Whittle
        try:
            numba_whittle = NumbaOptimizedWhittleEstimator()
            
            start_time = time.time()
            result_numba = numba_whittle.estimate(data)
            time_numba = time.time() - start_time
            
            print(f"NUMBA-Optimized Whittle: {time_numba:.4f}s")
            
            if time_orig is not None:
                speedup = time_orig / time_numba
                print(f"Speedup: {speedup:.2f}x")
            
            # Verify accuracy
            if time_orig is not None:
                h_diff = abs(result_orig['hurst_parameter'] - result_numba['hurst_parameter'])
                print(f"Hurst difference: {h_diff:.6f}")
                
        except Exception as e:
            print(f"NUMBA-Optimized Whittle: Failed - {e}")


if __name__ == "__main__":
    benchmark_whittle_performance()
