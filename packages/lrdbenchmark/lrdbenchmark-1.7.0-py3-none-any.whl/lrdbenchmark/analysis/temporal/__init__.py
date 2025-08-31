"""
Temporal analysis estimators for LRDBench.

This module provides various temporal estimators for analyzing long-range dependence
in time series data.
"""

# Import individual modules for direct access
from .rs import rs_estimator
from .dma import dma_estimator
from .dfa import dfa_estimator
from .higuchi import higuchi_estimator

# Import unified estimators
from .rs.rs_estimator import RSEstimator
from .dma.dma_estimator import DMAEstimator
from .dfa.dfa_estimator import DFAEstimator
from .higuchi.higuchi_estimator import HiguchiEstimator

__all__ = [
    "RSEstimator",
    "DMAEstimator", 
    "DFAEstimator",
    "HiguchiEstimator",
    "rs_estimator",
    "dma_estimator",
    "dfa_estimator",
    "higuchi_estimator",
]
