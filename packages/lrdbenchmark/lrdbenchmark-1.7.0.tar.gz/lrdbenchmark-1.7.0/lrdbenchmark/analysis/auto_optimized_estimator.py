#!/usr/bin/env python3
"""
Auto-Optimized Estimator System for LRDBench

This module provides automatic optimization switching that uses the fastest
available implementation (NUMBA > JAX > Standard) and falls back gracefully
when optimizations aren't available.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Type
import sys
import os
import time
import warnings

# Add the project root to the path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)

# Try to import optimization libraries
try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

try:
    import jax
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False


class AutoOptimizedEstimator:
    """
    Automatic optimization switcher for LRDBench estimators.
    
    This class automatically selects the fastest available implementation:
    1. NUMBA-optimized (fastest)
    2. JAX-optimized (GPU acceleration)
    3. Standard implementation (fallback)
    
    Features:
    - Automatic performance detection
    - Graceful fallback system
    - Performance monitoring
    - Transparent API
    """
    
    def __init__(self, estimator_type: str, **kwargs):
        """
        Initialize auto-optimized estimator.
        
        Parameters
        ----------
        estimator_type : str
            Type of estimator ('dfa', 'rs', 'dma', 'higuchi', etc.)
        **kwargs
            Parameters to pass to the estimator
        """
        self.estimator_type = estimator_type.lower()
        self.kwargs = kwargs
        self.optimization_level = None
        self.estimator = None
        self.performance_log = {}
        
        # Initialize the best available estimator
        self._initialize_estimator()
    
    def _initialize_estimator(self):
        """Initialize the fastest available estimator."""
        try:
            # For DFA and RS, use SciPy optimization instead of problematic NUMBA
            if self.estimator_type in ['dfa', 'rs']:
                try:
                    self.estimator = self._get_numba_estimator()  # This actually gets SciPy-optimized for DFA/RS
                    self.optimization_level = "SciPy"
                    return
                except Exception as e:
                    warnings.warn(f"SciPy optimization failed for {self.estimator_type}: {e}")
                    self.estimator = self._get_standard_estimator()
                    self.optimization_level = "Standard"
                    return
            
            # For other estimators, try NUMBA first (fastest)
            if NUMBA_AVAILABLE:
                try:
                    self.estimator = self._get_numba_estimator()
                    self.optimization_level = "NUMBA"
                    return
                except Exception as e:
                    warnings.warn(f"NUMBA optimization failed for {self.estimator_type}: {e}")
            
            # Try JAX second (GPU acceleration)
            if JAX_AVAILABLE:
                try:
                    self.estimator = self._get_jax_estimator()
                    self.optimization_level = "JAX"
                    return
                except Exception as e:
                    warnings.warn(f"JAX optimization failed for {self.estimator_type}: {e}")
            
            # Fallback to standard implementation
            self.estimator = self._get_standard_estimator()
            self.optimization_level = "Standard"
            
        except Exception as e:
            warnings.warn(f"Failed to initialize {self.optimization_level} estimator: {e}")
            # Fallback to standard
            self.estimator = self._get_standard_estimator()
            self.optimization_level = "Standard"
    
    def _get_numba_estimator(self):
        """Get NUMBA-optimized estimator."""
        if self.estimator_type == 'dfa':
            # Use SciPy optimization instead of problematic NUMBA
            from lrdbench.analysis.temporal.dfa.dfa_estimator_scipy_optimized import ScipyOptimizedDFAEstimator
            return ScipyOptimizedDFAEstimator(**self.kwargs)
        elif self.estimator_type == 'rs':
            # Use SciPy optimization instead of problematic NUMBA
            from lrdbench.analysis.temporal.rs.scipy_optimized_rs_estimator import ScipyOptimizedRSEstimator
            return ScipyOptimizedRSEstimator(**self.kwargs)
        elif self.estimator_type == 'dma':
            from lrdbench.analysis.temporal.dma.dma_estimator_optimized import OptimizedDMAEstimator
            return OptimizedDMAEstimator(**self.kwargs)
        elif self.estimator_type == 'higuchi':
            from lrdbench.analysis.temporal.higuchi.higuchi_estimator_numba_optimized import NumbaOptimizedHiguchiEstimator
            return NumbaOptimizedHiguchiEstimator(**self.kwargs)
        elif self.estimator_type == 'gph':
            from lrdbench.analysis.spectral.gph.gph_estimator_numba_optimized import NumbaOptimizedGPHEstimator
            return NumbaOptimizedGPHEstimator(**self.kwargs)
        elif self.estimator_type == 'periodogram':
            from lrdbench.analysis.spectral.periodogram.periodogram_estimator_numba_optimized import NumbaOptimizedPeriodogramEstimator
            return NumbaOptimizedPeriodogramEstimator(**self.kwargs)
        elif self.estimator_type == 'whittle':
            from lrdbench.analysis.spectral.whittle.whittle_estimator_numba_optimized import NumbaOptimizedWhittleEstimator
            return NumbaOptimizedWhittleEstimator(**self.kwargs)
        elif self.estimator_type == 'cwt':
            from lrdbench.analysis.wavelet.cwt.cwt_estimator_numba_optimized import NumbaOptimizedCWTEstimator
            return NumbaOptimizedCWTEstimator(**self.kwargs)
        elif self.estimator_type == 'wavelet_variance':
            from lrdbench.analysis.wavelet.variance.wavelet_variance_estimator_numba_optimized import NumbaOptimizedWaveletVarianceEstimator
            return NumbaOptimizedWaveletVarianceEstimator(**self.kwargs)
        elif self.estimator_type == 'wavelet_log_variance':
            from lrdbench.analysis.wavelet.log_variance.wavelet_log_variance_estimator_numba_optimized import NumbaOptimizedWaveletLogVarianceEstimator
            return NumbaOptimizedWaveletLogVarianceEstimator(**self.kwargs)
        elif self.estimator_type == 'wavelet_whittle':
            from lrdbench.analysis.wavelet.whittle.wavelet_whittle_estimator_numba_optimized import NumbaOptimizedWaveletWhittleEstimator
            return NumbaOptimizedWaveletWhittleEstimator(**self.kwargs)
        elif self.estimator_type == 'mfdfa':
            from lrdbench.analysis.multifractal.mfdfa.mfdfa_estimator_numba_optimized import NumbaOptimizedMFDFAEstimator
            return NumbaOptimizedMFDFAEstimator(**self.kwargs)
        else:
            raise ValueError(f"NUMBA optimization not available for {self.estimator_type}")
    
    def _get_jax_estimator(self):
        """Get JAX-optimized estimator."""
        if self.estimator_type == 'dfa':
            from lrdbench.analysis.temporal.dfa.dfa_estimator_jax_optimized import JaxOptimizedDFAEstimator
            return JaxOptimizedDFAEstimator(**self.kwargs)
        elif self.estimator_type in ['cwt', 'wavelet_variance', 'wavelet_log_variance', 'wavelet_whittle', 'mfdfa']:
            # These estimators don't have JAX optimizations yet, so fall back to NUMBA
            raise ValueError(f"JAX optimization not available for {self.estimator_type}")
        else:
            raise ValueError(f"JAX optimization not available for {self.estimator_type}")
    
    def _get_standard_estimator(self):
        """Get standard estimator."""
        if self.estimator_type == 'dfa':
            from lrdbench.analysis.temporal.dfa.dfa_estimator import DFAEstimator
            return DFAEstimator(**self.kwargs)
        elif self.estimator_type == 'rs':
            from lrdbench.analysis.temporal.rs.rs_estimator import RSEstimator
            return RSEstimator(**self.kwargs)
        elif self.estimator_type == 'dma':
            from lrdbench.analysis.temporal.dma.dma_estimator import DMAEstimator
            return DMAEstimator(**self.kwargs)
        elif self.estimator_type == 'higuchi':
            from lrdbench.analysis.temporal.higuchi.higuchi_estimator import HiguchiEstimator
            return HiguchiEstimator(**self.kwargs)
        elif self.estimator_type == 'gph':
            from lrdbench.analysis.spectral.gph.gph_estimator import GPHEstimator
            return GPHEstimator(**self.kwargs)
        elif self.estimator_type == 'periodogram':
            from lrdbench.analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
            return PeriodogramEstimator(**self.kwargs)
        elif self.estimator_type == 'whittle':
            from lrdbench.analysis.spectral.whittle.whittle_estimator import WhittleEstimator
            return WhittleEstimator(**self.kwargs)
        elif self.estimator_type == 'cwt':
            from lrdbench.analysis.wavelet.cwt.cwt_estimator import CWTEstimator
            return CWTEstimator(**self.kwargs)
        elif self.estimator_type == 'wavelet_variance':
            from lrdbench.analysis.wavelet.variance.wavelet_variance_estimator import WaveletVarianceEstimator
            return WaveletVarianceEstimator(**self.kwargs)
        elif self.estimator_type == 'wavelet_log_variance':
            from lrdbench.analysis.wavelet.log_variance.wavelet_log_variance_estimator import WaveletLogVarianceEstimator
            return WaveletLogVarianceEstimator(**self.kwargs)
        elif self.estimator_type == 'wavelet_whittle':
            from lrdbench.analysis.wavelet.whittle.wavelet_whittle_estimator import WaveletWhittleEstimator
            return WaveletWhittleEstimator(**self.kwargs)
        elif self.estimator_type == 'mfdfa':
            from lrdbench.analysis.multifractal.mfdfa.mfdfa_estimator import MFDFAEstimator
            return MFDFAEstimator(**self.kwargs)
        else:
            raise ValueError(f"Unknown estimator type: {self.estimator_type}")
    
    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using the fastest available implementation.
        
        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze
            
        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        start_time = time.time()
        
        try:
            result = self.estimator.estimate(data)
            
            # Log performance
            execution_time = time.time() - start_time
            self.performance_log = {
                'optimization_level': self.optimization_level,
                'execution_time': execution_time,
                'data_size': len(data),
                'success': True
            }
            
            # Add optimization info to results
            result['optimization_info'] = {
                'level': self.optimization_level,
                'execution_time': execution_time,
                'data_size': len(data)
            }
            
            return result
            
        except Exception as e:
            # Log failure
            execution_time = time.time() - start_time
            self.performance_log = {
                'optimization_level': self.optimization_level,
                'execution_time': execution_time,
                'data_size': len(data),
                'success': False,
                'error': str(e)
            }
            raise
    
    def get_optimization_info(self) -> Dict[str, Any]:
        """Get information about the current optimization level."""
        return {
            'optimization_level': self.optimization_level,
            'numba_available': NUMBA_AVAILABLE,
            'jax_available': JAX_AVAILABLE,
            'performance_log': self.performance_log
        }
    
    def benchmark_all_implementations(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Benchmark all available implementations for comparison.
        
        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze
            
        Returns
        -------
        dict
            Benchmark results for all available implementations
        """
        results = {}
        
        # Test standard implementation
        try:
            standard_estimator = self._get_standard_estimator()
            start_time = time.time()
            standard_result = standard_estimator.estimate(data)
            standard_time = time.time() - start_time
            
            results['standard'] = {
                'time': standard_time,
                'hurst': standard_result['hurst_parameter'],
                'success': True
            }
        except Exception as e:
            results['standard'] = {
                'time': None,
                'hurst': None,
                'success': False,
                'error': str(e)
            }
        
        # Test NUMBA implementation
        if NUMBA_AVAILABLE:
            try:
                numba_estimator = self._get_numba_estimator()
                start_time = time.time()
                numba_result = numba_estimator.estimate(data)
                numba_time = time.time() - start_time
                
                results['numba'] = {
                    'time': numba_time,
                    'hurst': numba_result['hurst_parameter'],
                    'success': True
                }
            except Exception as e:
                results['numba'] = {
                    'time': None,
                    'hurst': None,
                    'success': False,
                    'error': str(e)
                }
        
        # Test JAX implementation
        if JAX_AVAILABLE:
            try:
                jax_estimator = self._get_jax_estimator()
                start_time = time.time()
                jax_result = jax_estimator.estimate(data)
                jax_time = time.time() - start_time
                
                results['jax'] = {
                    'time': jax_time,
                    'hurst': jax_result['hurst_parameter'],
                    'success': True
                }
            except Exception as e:
                results['jax'] = {
                    'time': None,
                    'hurst': None,
                    'success': False,
                    'error': str(e)
                }
        
        # Calculate speedups
        if results['standard']['success'] and results['standard']['time']:
            standard_time = results['standard']['time']
            
            if results.get('numba', {}).get('success') and results['numba']['time']:
                results['numba']['speedup'] = standard_time / results['numba']['time']
            
            if results.get('jax', {}).get('success') and results['jax']['time']:
                results['jax']['speedup'] = standard_time / results['jax']['time']
        
        return results


# Convenience functions for easy access
def AutoDFAEstimator(**kwargs):
    """Auto-optimized DFA estimator."""
    return AutoOptimizedEstimator('dfa', **kwargs)

def AutoRSEstimator(**kwargs):
    """Auto-optimized RS estimator."""
    return AutoOptimizedEstimator('rs', **kwargs)

def AutoDMAEstimator(**kwargs):
    """Auto-optimized DMA estimator."""
    return AutoOptimizedEstimator('dma', **kwargs)

def AutoHiguchiEstimator(**kwargs):
    """Auto-optimized Higuchi estimator."""
    return AutoOptimizedEstimator('higuchi', **kwargs)

def AutoGPHEstimator(**kwargs):
    """Auto-optimized GPH estimator."""
    return AutoOptimizedEstimator('gph', **kwargs)

def AutoPeriodogramEstimator(**kwargs):
    """Auto-optimized Periodogram estimator."""
    return AutoOptimizedEstimator('periodogram', **kwargs)

def AutoWhittleEstimator(**kwargs):
    """Auto-optimized Whittle estimator."""
    return AutoOptimizedEstimator('whittle', **kwargs)


def benchmark_auto_optimization():
    """Benchmark the auto-optimization system."""
    import time
    from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise
    
    # Generate test data
    fgn = FractionalGaussianNoise(H=0.7)
    data_sizes = [1000, 5000, 10000]
    
    print("🚀 Auto-Optimization System Benchmark")
    print("=" * 60)
    print(f"NUMBA Available: {NUMBA_AVAILABLE}")
    print(f"JAX Available: {JAX_AVAILABLE}")
    
    estimators = ['dfa', 'rs', 'dma']
    
    for estimator_type in estimators:
        print(f"\n{'='*20} {estimator_type.upper()} {'='*20}")
        
        for size in data_sizes:
            print(f"\nData size: {size}")
            data = fgn.generate(size, seed=42)
            
            try:
                # Test auto-optimized estimator
                auto_estimator = AutoOptimizedEstimator(estimator_type)
                
                start_time = time.time()
                result = auto_estimator.estimate(data)
                time_taken = time.time() - start_time
                
                print(f"Auto-Optimized ({auto_estimator.optimization_level}): {time_taken:.4f}s")
                print(f"Hurst: {result['hurst_parameter']:.6f}")
                
                # Benchmark all implementations
                benchmark_results = auto_estimator.benchmark_all_implementations(data)
                
                print("Benchmark Results:")
                for impl, res in benchmark_results.items():
                    if res['success']:
                        speedup = res.get('speedup', 'N/A')
                        print(f"  {impl.upper()}: {res['time']:.4f}s (speedup: {speedup})")
                    else:
                        print(f"  {impl.upper()}: Failed - {res.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"Auto-Optimized {estimator_type.upper()}: Failed - {e}")


if __name__ == "__main__":
    benchmark_auto_optimization()
