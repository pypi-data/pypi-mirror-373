"""
GPH estimator subpackage.

Exposes the `GPHEstimator` for the Geweke–Porter–Hudak log-periodogram
regression estimator of fractional differencing parameter d and H.
"""

from .gph_estimator import GPHEstimator

__all__ = ["GPHEstimator"]
