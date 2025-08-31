"""
Support Vector Regression Estimator for Long-Range Dependence Analysis

This module provides a support vector regression-based estimator for Hurst parameter
estimation using scikit-learn's SVR.
"""

import numpy as np
from typing import Dict, Any
from sklearn.svm import SVR
from .base_ml_estimator import BaseMLEstimator


class SVREstimator(BaseMLEstimator):
    """
    Support Vector Regression estimator for Hurst parameter estimation.

    This estimator uses support vector regression to learn the mapping
    from time series features to Hurst parameters.
    """

    def __init__(self, **kwargs):
        """
        Initialize the SVR estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator parameters including:
            - kernel: str, kernel function (default: 'rbf')
            - C: float, regularization parameter (default: 1.0)
            - epsilon: float, epsilon in epsilon-SVR (default: 0.1)
            - gamma: str, kernel coefficient (default: 'scale')
            - random_state: int, random seed (default: 42)
            - feature_extraction_method: str, feature extraction method (default: 'statistical')
        """
        # Set default parameters
        default_params = {
            "kernel": "rbf",
            "C": 1.0,
            "epsilon": 0.1,
            "gamma": "scale",
            "random_state": 42,
            "feature_extraction_method": "statistical",
        }

        # Update with provided parameters
        default_params.update(kwargs)
        super().__init__(**default_params)

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["kernel"] not in ["linear", "poly", "rbf", "sigmoid"]:
            raise ValueError("kernel must be one of: linear, poly, rbf, sigmoid")

        if self.parameters["C"] <= 0:
            raise ValueError("C must be positive")

        if self.parameters["epsilon"] < 0:
            raise ValueError("epsilon must be non-negative")

        if self.parameters["gamma"] not in ["scale", "auto"] and not isinstance(
            self.parameters["gamma"], (int, float)
        ):
            raise ValueError("gamma must be 'scale', 'auto', or a positive number")

    def _create_model(self) -> SVR:
        """
        Create the SVR model.

        Returns
        -------
        SVR
            The support vector regression model
        """
        return SVR(
            kernel=self.parameters["kernel"],
            C=self.parameters["C"],
            epsilon=self.parameters["epsilon"],
            gamma=self.parameters["gamma"],
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the SVR model.

        Returns
        -------
        dict
            Model information
        """
        return {
            "model_type": "Support Vector Regression",
            "kernel": self.parameters["kernel"],
            "C": self.parameters["C"],
            "epsilon": self.parameters["epsilon"],
            "gamma": self.parameters["gamma"],
            "feature_extraction": self.feature_extraction_method,
        }
