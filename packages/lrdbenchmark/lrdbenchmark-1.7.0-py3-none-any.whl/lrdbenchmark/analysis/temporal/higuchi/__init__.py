"""
Higuchi Method subpackage.

Exposes the `HiguchiEstimator` for estimating the fractal dimension
and Hurst parameter using the Higuchi method.
"""

from .higuchi_estimator import HiguchiEstimator

__all__ = ["HiguchiEstimator"]
