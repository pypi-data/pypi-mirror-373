"""
Random Forest Estimator for Long-Range Dependence Analysis

This module provides a random forest-based estimator for Hurst parameter
estimation using scikit-learn's RandomForestRegressor.
"""

import numpy as np
from typing import Dict, Any
from sklearn.ensemble import RandomForestRegressor
from .base_ml_estimator import BaseMLEstimator


class RandomForestEstimator(BaseMLEstimator):
    """
    Random Forest estimator for Hurst parameter estimation.

    This estimator uses an ensemble of decision trees to learn the mapping
    from time series features to Hurst parameters.
    """

    def __init__(self, **kwargs):
        """
        Initialize the Random Forest estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator parameters including:
            - n_estimators: int, number of trees (default: 100)
            - max_depth: int, maximum depth of trees (default: None)
            - min_samples_split: int, minimum samples to split (default: 2)
            - min_samples_leaf: int, minimum samples per leaf (default: 1)
            - max_features: str, feature selection method (default: 'sqrt')
            - random_state: int, random seed (default: 42)
            - feature_extraction_method: str, feature extraction method (default: 'statistical')
        """
        # Set default parameters
        default_params = {
            "n_estimators": 100,
            "max_depth": None,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
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

        if (
            self.parameters["max_depth"] is not None
            and self.parameters["max_depth"] <= 0
        ):
            raise ValueError("max_depth must be positive or None")

        if self.parameters["min_samples_split"] < 2:
            raise ValueError("min_samples_split must be at least 2")

        if self.parameters["min_samples_leaf"] < 1:
            raise ValueError("min_samples_leaf must be at least 1")

        if self.parameters["max_features"] not in ["sqrt", "log2", None]:
            raise ValueError("max_features must be one of: sqrt, log2, None")

    def _create_model(self) -> RandomForestRegressor:
        """
        Create the random forest model.

        Returns
        -------
        RandomForestRegressor
            The random forest model
        """
        return RandomForestRegressor(
            n_estimators=self.parameters["n_estimators"],
            max_depth=self.parameters["max_depth"],
            min_samples_split=self.parameters["min_samples_split"],
            min_samples_leaf=self.parameters["min_samples_leaf"],
            max_features=self.parameters["max_features"],
            random_state=self.parameters["random_state"],
            n_jobs=-1,  # Use all available cores
            oob_score=True,  # Enable out-of-bag scoring
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the random forest model.

        Returns
        -------
        dict
            Model information
        """
        info = {
            "model_type": "Random Forest",
            "n_estimators": self.parameters["n_estimators"],
            "max_depth": self.parameters["max_depth"],
            "min_samples_split": self.parameters["min_samples_split"],
            "min_samples_leaf": self.parameters["min_samples_leaf"],
            "max_features": self.parameters["max_features"],
            "feature_extraction": self.feature_extraction_method,
        }

        # Add out-of-bag score if model is trained
        if self.is_trained and hasattr(self.model, "oob_score_"):
            info["oob_score"] = self.model.oob_score_

        return info
