"""
Multifractal Random Walk (MRW) subpackage.

Exposes the `MultifractalRandomWalk` model for generating multifractal
time series with log-normal volatility cascades.
"""

from .mrw_model import MultifractalRandomWalk

__all__ = ["MultifractalRandomWalk"]
