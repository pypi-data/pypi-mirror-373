"""
Estimators package for parameter estimation from time series data.

This package provides various estimators for characterizing time series
properties including Hurst parameter, long-range dependence, and multifractal
characteristics.
"""

from .base_estimator import BaseEstimator

__all__ = ["BaseEstimator"]
