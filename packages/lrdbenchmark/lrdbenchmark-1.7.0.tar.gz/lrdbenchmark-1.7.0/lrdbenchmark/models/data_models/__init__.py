"""
Data models package containing implementations of stochastic processes.

This package provides classes for generating synthetic data from various
stochastic models including ARFIMA, fBm, fGn, and MRW.
"""

from .base_model import BaseModel

# Import all model classes
from .fbm.fbm_model import FractionalBrownianMotion
from .fgn.fgn_model import FractionalGaussianNoise
from .arfima.arfima_model import ARFIMAModel
from .mrw.mrw_model import MultifractalRandomWalk

# Create shortened aliases for convenience
FBMModel = FractionalBrownianMotion
FGNModel = FractionalGaussianNoise
ARFIMAModel = ARFIMAModel  # Keep as is since it's already short
MRWModel = MultifractalRandomWalk


# Convenience functions with default parameters
def create_fbm_model(H=0.7, sigma=1.0):
    """Create FBMModel with default parameters"""
    return FBMModel(H=H, sigma=sigma)


def create_fgn_model(H=0.6, sigma=1.0):
    """Create FGNModel with default parameters"""
    return FGNModel(H=H, sigma=sigma)


def create_arfima_model(d=0.2, sigma=1.0):
    """Create ARFIMAModel with default parameters"""
    return ARFIMAModel(d=d, sigma=sigma)


def create_mrw_model(H=0.7, lambda_param=0.1, sigma=1.0):
    """Create MRWModel with default parameters"""
    return MRWModel(H=H, lambda_param=lambda_param, sigma=sigma)


__all__ = [
    "BaseModel",
    "FractionalBrownianMotion",
    "FractionalGaussianNoise",
    "ARFIMAModel",
    "MultifractalRandomWalk",
    "FBMModel",
    "FGNModel",
    "MRWModel",
    "create_fbm_model",
    "create_fgn_model",
    "create_arfima_model",
    "create_mrw_model",
]
