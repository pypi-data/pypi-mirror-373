"""
Models package for synthetic data generation.

This package contains implementations of various stochastic models:
- ARFIMA (AutoRegressive Fractionally Integrated Moving Average)
- fBm (Fractional Brownian Motion)
- fGn (Fractional Gaussian Noise)
- MRW (Multifractal Random Walk)
"""

__version__ = "0.1.0"
__author__ = "LRDBench Development Team"

# Import data models with error handling
try:
    from .data_models.fbm.fbm_model import FractionalBrownianMotion as FBMModel
    from .data_models.fgn.fgn_model import FractionalGaussianNoise as FGNModel
    from .data_models.arfima.arfima_model import ARFIMAModel
    from .data_models.mrw.mrw_model import MultifractalRandomWalk as MRWModel
except ImportError:
    # Placeholder classes for modules that don't exist yet
    class FBMModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("FBMModel not available - module not found")
    
    class FGNModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("FGNModel not available - module not found")
    
    class ARFIMAModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("ARFIMAModel not available - module not found")
    
    class MRWModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("MRWModel not available - module not found")

__all__ = [
    "FBMModel",
    "FGNModel", 
    "ARFIMAModel",
    "MRWModel",
]
