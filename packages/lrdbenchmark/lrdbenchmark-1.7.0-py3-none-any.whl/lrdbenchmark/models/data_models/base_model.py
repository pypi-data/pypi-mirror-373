"""
Base model class for all stochastic processes.

This module provides the abstract base class that all stochastic models
should inherit from, ensuring consistent interface and functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
import numpy as np


class BaseModel(ABC):
    """
    Abstract base class for all stochastic models.

    This class defines the interface that all stochastic models must implement,
    including methods for parameter validation, data generation, and model
    information retrieval.
    """

    def __init__(self, **kwargs):
        """
        Initialize the base model.

        Parameters
        ----------
        **kwargs : dict
            Model-specific parameters
        """
        self.parameters = kwargs
        self._validate_parameters()

    @abstractmethod
    def _validate_parameters(self) -> None:
        """
        Validate model parameters.

        This method should be implemented by each model to ensure
        that the provided parameters are valid for the specific model.
        """
        pass

    @abstractmethod
    def generate(self, n: int, seed: Optional[int] = None) -> np.ndarray:
        """
        Generate synthetic data from the model.

        Parameters
        ----------
        n : int
            Length of the time series to generate
        seed : int, optional
            Random seed for reproducibility

        Returns
        -------
        np.ndarray
            Generated time series of length n
        """
        pass

    @abstractmethod
    def get_theoretical_properties(self) -> Dict[str, Any]:
        """
        Get theoretical properties of the model.

        Returns
        -------
        dict
            Dictionary containing theoretical properties such as
            autocorrelation function, power spectral density, etc.
        """
        pass

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current model parameters.

        Returns
        -------
        dict
            Current model parameters
        """
        return self.parameters.copy()

    def set_parameters(self, **kwargs) -> None:
        """
        Set model parameters.

        Parameters
        ----------
        **kwargs : dict
            New parameter values
        """
        self.parameters.update(kwargs)
        self._validate_parameters()

    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}({self.parameters})"

    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return f"{self.__class__.__name__}(parameters={self.parameters})"
