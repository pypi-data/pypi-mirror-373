"""
Whittle estimator subpackage.

Exposes the `WhittleEstimator` for (approximate) Whittle likelihood
estimation of fractional differencing parameter d and Hurst parameter.
"""

from .whittle_estimator import WhittleEstimator

__all__ = ["WhittleEstimator"]
