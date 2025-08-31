"""
Spectral analysis estimators for LRDBench.

This module provides various spectral estimators for analyzing long-range dependence
in time series data using frequency domain methods.
"""

# Import individual modules for direct access
from .gph import gph_estimator
from .periodogram import periodogram_estimator
from .whittle import whittle_estimator

# Import estimators from individual modules
from .gph.gph_estimator import GPHEstimator
from .periodogram.periodogram_estimator import PeriodogramEstimator
from .whittle.whittle_estimator import WhittleEstimator

__all__ = [
    "GPHEstimator",
    "PeriodogramEstimator",
    "WhittleEstimator",
    "gph_estimator",
    "periodogram_estimator",
    "whittle_estimator",
]
