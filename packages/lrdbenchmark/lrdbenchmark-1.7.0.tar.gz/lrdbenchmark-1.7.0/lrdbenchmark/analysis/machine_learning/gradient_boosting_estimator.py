"""
Gradient Boosting Estimator for Long-Range Dependence Analysis

This module provides a gradient boosting-based estimator for Hurst parameter
estimation using scikit-learn's GradientBoostingRegressor.
"""

import numpy as np
from typing import Dict, Any
from sklearn.ensemble import GradientBoostingRegressor
from .base_ml_estimator import BaseMLEstimator


class GradientBoostingEstimator(BaseMLEstimator):
    """
    Gradient Boosting estimator for Hurst parameter estimation.

    This estimator uses gradient boosting to learn the mapping
    from time series features to Hurst parameters.
    """

    def __init__(self, **kwargs):
        """
        Initialize the Gradient Boosting estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator parameters including:
            - n_estimators: int, number of boosting stages (default: 100)
            - learning_rate: float, learning rate (default: 0.1)
            - max_depth: int, maximum depth of trees (default: 3)
            - min_samples_split: int, minimum samples to split (default: 2)
            - min_samples_leaf: int, minimum samples per leaf (default: 1)
            - subsample: float, fraction of samples for fitting (default: 1.0)
            - random_state: int, random seed (default: 42)
            - feature_extraction_method: str, feature extraction method (default: 'statistical')
        """
        # Set default parameters
        default_params = {
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 3,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "subsample": 1.0,
            "random_state": 42,
            "feature_extraction_method": "statistical",
        }

        # Update with provided parameters
        default_params.update(kwargs)
        super().__init__(**default_params)

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["n_estimators"] <= 0:
            raise ValueError("n_estimators must be positive")

        if self.parameters["learning_rate"] <= 0:
            raise ValueError("learning_rate must be positive")

        if self.parameters["max_depth"] <= 0:
            raise ValueError("max_depth must be positive")

        if self.parameters["min_samples_split"] < 2:
            raise ValueError("min_samples_split must be at least 2")

        if self.parameters["min_samples_leaf"] < 1:
            raise ValueError("min_samples_leaf must be at least 1")

        if not 0 < self.parameters["subsample"] <= 1:
            raise ValueError("subsample must be between 0 and 1")

    def _create_model(self) -> GradientBoostingRegressor:
        """
        Create the gradient boosting model.

        Returns
        -------
        GradientBoostingRegressor
            The gradient boosting model
        """
        return GradientBoostingRegressor(
            n_estimators=self.parameters["n_estimators"],
            learning_rate=self.parameters["learning_rate"],
            max_depth=self.parameters["max_depth"],
            min_samples_split=self.parameters["min_samples_split"],
            min_samples_leaf=self.parameters["min_samples_leaf"],
            subsample=self.parameters["subsample"],
            random_state=self.parameters["random_state"],
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the gradient boosting model.

        Returns
        -------
        dict
            Model information
        """
        return {
            "model_type": "Gradient Boosting",
            "n_estimators": self.parameters["n_estimators"],
            "learning_rate": self.parameters["learning_rate"],
            "max_depth": self.parameters["max_depth"],
            "min_samples_split": self.parameters["min_samples_split"],
            "min_samples_leaf": self.parameters["min_samples_leaf"],
            "subsample": self.parameters["subsample"],
            "feature_extraction": self.feature_extraction_method,
        }
