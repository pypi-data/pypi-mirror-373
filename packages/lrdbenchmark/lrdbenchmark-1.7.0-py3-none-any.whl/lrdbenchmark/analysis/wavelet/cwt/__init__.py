"""
Continuous Wavelet Transform (CWT) Analysis module.

This module provides Continuous Wavelet Transform analysis for estimating the Hurst parameter
from time series data using continuous wavelet decomposition.
"""

from .cwt_estimator import CWTEstimator

__all__ = ["CWTEstimator"]
