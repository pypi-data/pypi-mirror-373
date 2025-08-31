"""
Autoregressive Fractionally Integrated Moving Average (ARFIMA) subpackage.

Exposes the `ARFIMAModel` for generating ARFIMA time series with long-range dependence.
"""

from .arfima_model import ARFIMAModel

__all__ = ["ARFIMAModel"]
