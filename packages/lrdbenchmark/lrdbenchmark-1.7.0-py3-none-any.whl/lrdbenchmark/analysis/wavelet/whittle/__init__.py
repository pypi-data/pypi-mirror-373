"""
Wavelet Whittle Analysis module.

This module provides wavelet Whittle analysis for estimating the Hurst parameter
from time series data using wavelet-based Whittle likelihood estimation.
"""

from .wavelet_whittle_estimator import WaveletWhittleEstimator

__all__ = ["WaveletWhittleEstimator"]
