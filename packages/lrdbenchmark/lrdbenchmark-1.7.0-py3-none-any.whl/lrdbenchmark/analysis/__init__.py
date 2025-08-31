"""
Analysis module for LRDBench.

This module provides various estimators for analyzing long-range dependence
in time series data using both temporal and spectral methods.
"""

# Auto-optimized estimator system
try:
    from .auto_optimized_estimator import AutoOptimizedEstimator
except ImportError:
    AutoOptimizedEstimator = None

# Standard DFA (fallback)
try:
    from .temporal.dfa.dfa_estimator import DFAEstimator
except ImportError:
    DFAEstimator = None

# Import submodules
from . import temporal
from . import spectral

__all__ = [
    # Auto-optimized estimator system
    "AutoOptimizedEstimator",
    
    # Standard estimators
    "DFAEstimator",
    
    # Submodules
    "temporal",
    "spectral",
]
