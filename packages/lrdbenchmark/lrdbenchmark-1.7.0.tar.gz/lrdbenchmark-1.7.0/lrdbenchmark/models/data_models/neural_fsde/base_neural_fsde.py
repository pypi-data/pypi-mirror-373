"""
Base class for neural fractional stochastic differential equations.

This module provides the foundation for implementing neural fSDEs with
support for both JAX (high performance) and PyTorch (compatibility).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np

# Try to import JAX and PyTorch
try:
    import jax
    import jax.numpy as jnp

    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    jax = None
    jnp = None

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None

from ..base_model import BaseModel


class BaseNeuralFSDE(BaseModel, ABC):
    """
    Base class for neural fractional stochastic differential equations.

    This class provides a unified interface for neural fSDEs implemented
    in either JAX (for high performance) or PyTorch (for compatibility).
    """

    def __init__(
        self,
        state_dim: int,
        hidden_dim: int,
        hurst_parameter: float = 0.7,
        framework: str = "auto",
        **kwargs,
    ):
        """
        Initialize the base neural fSDE.

        Parameters
        ----------
        state_dim : int
            Dimension of the state space
        hidden_dim : int
            Dimension of hidden layers in neural networks
        hurst_parameter : float, default=0.7
            Initial Hurst parameter for fractional Brownian motion
        framework : str, default='auto'
            Framework to use: 'jax', 'torch', or 'auto'
        **kwargs
            Additional keyword arguments
        """
        # Set attributes before calling parent __init__ to avoid validation issues
        self.state_dim = state_dim
        self.hidden_dim = hidden_dim
        self.hurst_parameter = hurst_parameter

        # Framework selection
        if framework == "auto":
            self.framework = self._auto_select_framework()
        else:
            self.framework = framework

        if not self._validate_framework():
            raise ValueError(f"Framework '{self.framework}' not available")

        # Call parent __init__ with parameters
        super().__init__(
            state_dim=state_dim,
            hidden_dim=hidden_dim,
            hurst_parameter=hurst_parameter,
            framework=self.framework,
            **kwargs,
        )

        # Initialize framework-specific components
        self._initialize_framework()

    def _auto_select_framework(self) -> str:
        """Automatically select the best available framework."""
        if JAX_AVAILABLE:
            return "jax"
        elif TORCH_AVAILABLE:
            return "torch"
        else:
            raise RuntimeError("Neither JAX nor PyTorch is available")

    def _validate_framework(self) -> bool:
        """Validate that the selected framework is available."""
        if self.framework == "jax":
            return JAX_AVAILABLE
        elif self.framework == "torch":
            return TORCH_AVAILABLE
        else:
            return False

    @abstractmethod
    def _initialize_framework(self):
        """Initialize framework-specific components."""
        pass

    @abstractmethod
    def forward(self, x: np.ndarray, t: np.ndarray, dt: float) -> np.ndarray:
        """
        Forward pass through the neural fSDE.

        Parameters
        ----------
        x : np.ndarray
            Current state vector
        t : np.ndarray
            Current time points
        dt : float
            Time step size

        Returns
        -------
        np.ndarray
            Next state vector
        """
        pass

    @abstractmethod
    def generate_fbm_increment(self, dt: float, hurst: float) -> np.ndarray:
        """
        Generate fractional Brownian motion increment.

        Parameters
        ----------
        dt : float
            Time step size
        hurst : float
            Hurst parameter

        Returns
        -------
        np.ndarray
            fBm increment
        """
        pass

    def simulate(
        self,
        n_samples: int,
        dt: float = 0.01,
        initial_state: Optional[np.ndarray] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Simulate time series using the neural fSDE.

        Parameters
        ----------
        n_samples : int
            Number of samples to generate
        dt : float, default=0.01
            Time step size
        initial_state : np.ndarray, optional
            Initial state vector. If None, uses zero vector.
        **kwargs
            Additional keyword arguments

        Returns
        -------
        np.ndarray
            Generated time series
        """
        if initial_state is None:
            initial_state = np.zeros(self.state_dim)

        # Generate time points
        time_points = np.arange(0, n_samples * dt, dt)

        # Initialize trajectory
        trajectory = np.zeros((len(time_points), self.state_dim))
        trajectory[0] = initial_state

        # Simulate using the neural fSDE
        for i in range(1, len(time_points)):
            trajectory[i] = self.forward(trajectory[i - 1], time_points[i - 1], dt)

        return trajectory

    @abstractmethod
    def fit(self, data: np.ndarray, **kwargs) -> Dict[str, Any]:
        """
        Train the neural fSDE on data.

        Parameters
        ----------
        data : np.ndarray
            Training data
        **kwargs
            Additional keyword arguments

        Returns
        -------
        Dict[str, Any]
            Training results and metrics
        """
        pass

    def get_hurst_parameter(self) -> float:
        """Get the current Hurst parameter."""
        return self.hurst_parameter

    def set_hurst_parameter(self, hurst: float):
        """Set the Hurst parameter."""
        if not (0.01 <= hurst <= 0.99):
            raise ValueError("Hurst parameter must be between 0.01 and 0.99")
        self.hurst_parameter = hurst

    def get_framework(self) -> str:
        """Get the current framework being used."""
        return self.framework

    def switch_framework(self, framework: str):
        """Switch to a different framework."""
        if framework == self.framework:
            return

        if not self._validate_framework():
            raise ValueError(f"Framework '{framework}' not available")

        # Save current state
        current_state = self._get_current_state()

        # Switch framework
        self.framework = framework
        self._initialize_framework()

        # Restore state
        self._set_current_state(current_state)

    @abstractmethod
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current state for framework switching."""
        pass

    @abstractmethod
    def _set_current_state(self, state: Dict[str, Any]):
        """Set current state after framework switching."""
        pass

    def __str__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}(state_dim={self.state_dim}, "
            f"hidden_dim={self.hidden_dim}, hurst={self.hurst_parameter:.3f}, "
            f"framework={self.framework})"
        )

    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()
