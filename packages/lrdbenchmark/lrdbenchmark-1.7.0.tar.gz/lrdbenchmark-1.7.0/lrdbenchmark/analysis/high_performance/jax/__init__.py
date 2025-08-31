"""
JAX-optimized high-performance estimators.

This package contains JAX-optimized versions of all estimators for GPU acceleration
and improved performance on large datasets.
"""

from .dfa_jax import DFAEstimatorJAX
from .rs_jax import RSEstimatorJAX
from .higuchi_jax import HiguchiEstimatorJAX
from .dma_jax import DMAEstimatorJAX
from .periodogram_jax import PeriodogramEstimatorJAX
from .whittle_jax import WhittleEstimatorJAX
from .gph_jax import GPHEstimatorJAX
from .wavelet_log_variance_jax import WaveletLogVarianceEstimatorJAX
from .wavelet_variance_jax import WaveletVarianceEstimatorJAX
from .wavelet_whittle_jax import WaveletWhittleEstimatorJAX
from .cwt_jax import CWTEstimatorJAX
from .mfdfa_jax import MFDFAEstimatorJAX
from .multifractal_wavelet_leaders_jax import MultifractalWaveletLeadersEstimatorJAX

__all__ = [
    "DFAEstimatorJAX",
    "RSEstimatorJAX",
    "HiguchiEstimatorJAX",
    "DMAEstimatorJAX",
    "PeriodogramEstimatorJAX",
    "WhittleEstimatorJAX",
    "GPHEstimatorJAX",
    "WaveletLogVarianceEstimatorJAX",
    "WaveletVarianceEstimatorJAX",
    "WaveletWhittleEstimatorJAX",
    "CWTEstimatorJAX",
    "MFDFAEstimatorJAX",
    "MultifractalWaveletLeadersEstimatorJAX",
]
