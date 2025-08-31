"""
Detrended Fluctuation Analysis (DFA) estimator.

This package provides tools for estimating the Hurst parameter using
Detrended Fluctuation Analysis, a method for quantifying long-range
correlations in time series.
"""

from .dfa_estimator import DFAEstimator

__all__ = ["DFAEstimator"]
