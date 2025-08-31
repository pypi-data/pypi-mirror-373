"""
Fractional Brownian Motion (fBm) model implementation.

This package provides tools for generating and analyzing fractional Brownian motion,
a self-similar Gaussian process characterized by the Hurst parameter H.
"""

from .fbm_model import FractionalBrownianMotion

__all__ = ["FractionalBrownianMotion"]
