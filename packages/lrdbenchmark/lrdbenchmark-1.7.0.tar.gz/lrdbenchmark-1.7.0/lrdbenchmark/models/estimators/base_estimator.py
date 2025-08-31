"""
Base estimator class for all parameter estimation methods.

This module provides the abstract base class that all estimators should
inherit from, ensuring consistent interface and functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import numpy as np


class BaseEstimator(ABC):
    """
    Abstract base class for all parameter estimators.

    This class defines the interface that all estimators must implement,
    including methods for parameter estimation, confidence intervals,
    and result reporting.
    """

    def __init__(self, **kwargs):
        """
        Initialize the base estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator-specific parameters
        """
        self.parameters = kwargs
        self.results = {}

    @abstractmethod
    def _validate_parameters(self) -> None:
        """
        Validate estimator parameters.

        This method should be implemented by each estimator to ensure
        that the provided parameters are valid for the specific method.
        """
        pass

    @abstractmethod
    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate parameters from the given data.

        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        pass

    def get_results(self) -> Dict[str, Any]:
        """
        Get the most recent estimation results.

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        return self.results.copy()

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current estimator parameters.

        Returns
        -------
        dict
            Current estimator parameters
        """
        return self.parameters.copy()

    def set_parameters(self, **kwargs) -> None:
        """
        Set estimator parameters.

        Parameters
        ----------
        **kwargs : dict
            New parameter values
        """
        self.parameters.update(kwargs)
        self._validate_parameters()

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for estimated parameters.

        Parameters
        ----------
        confidence_level : float, optional
            Confidence level (default: 0.95)

        Returns
        -------
        dict
            Dictionary containing confidence intervals for each parameter
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # Default implementation - can be overridden by specific estimators
        return {}

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the estimation.

        Returns
        -------
        dict
            Dictionary containing quality metrics
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # Default implementation - can be overridden by specific estimators
        return {}

    def __str__(self) -> str:
        """String representation of the estimator."""
        return f"{self.__class__.__name__}({self.parameters})"

    def __repr__(self) -> str:
        """Detailed string representation of the estimator."""
        return f"{self.__class__.__name__}(parameters={self.parameters})"
