"""
Numba-optimized high-performance estimators.

This package contains Numba JIT-compiled versions of all estimators for improved
single-threaded performance on CPU.
"""

from .dfa_numba import DFAEstimatorNumba
from .rs_numba import RSEstimatorNumba
from .higuchi_numba import HiguchiEstimatorNumba
from .dma_numba import DMAEstimatorNumba
from .periodogram_numba import PeriodogramEstimatorNumba
from .whittle_numba import WhittleEstimatorNumba
from .gph_numba import GPHEstimatorNumba
from .wavelet_log_variance_numba import WaveletLogVarianceEstimatorNumba
from .wavelet_variance_numba import WaveletVarianceEstimatorNumba
from .wavelet_whittle_numba import WaveletWhittleEstimatorNumba
from .cwt_numba import CWTEstimatorNumba
from .mfdfa_numba import MFDFAEstimatorNumba
from .multifractal_wavelet_leaders_numba import MultifractalWaveletLeadersEstimatorNumba

__all__ = [
    "DFAEstimatorNumba",
    "RSEstimatorNumba",
    "HiguchiEstimatorNumba",
    "DMAEstimatorNumba",
    "PeriodogramEstimatorNumba",
    "WhittleEstimatorNumba",
    "GPHEstimatorNumba",
    "WaveletLogVarianceEstimatorNumba",
    "WaveletVarianceEstimatorNumba",
    "WaveletWhittleEstimatorNumba",
    "CWTEstimatorNumba",
    "MFDFAEstimatorNumba",
    "MultifractalWaveletLeadersEstimatorNumba",
]
