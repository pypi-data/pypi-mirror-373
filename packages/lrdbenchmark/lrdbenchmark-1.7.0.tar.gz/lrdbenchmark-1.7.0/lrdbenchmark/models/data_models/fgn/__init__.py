"""
Fractional Gaussian Noise (fGn) subpackage.

Exposes the `FractionalGaussianNoise` model for generating stationary
increments of fractional Brownian motion.
"""

from .fgn_model import FractionalGaussianNoise

__all__ = ["FractionalGaussianNoise"]
