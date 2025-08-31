"""
Neural Network Estimator for Long-Range Dependence Analysis

This module provides a neural network-based estimator for Hurst parameter
estimation using scikit-learn's MLPRegressor.
"""

import numpy as np
from typing import Dict, Any
from sklearn.neural_network import MLPRegressor
from .base_ml_estimator import BaseMLEstimator


class NeuralNetworkEstimator(BaseMLEstimator):
    """
    Neural Network estimator for Hurst parameter estimation.

    This estimator uses a multi-layer perceptron (MLP) to learn the mapping
    from time series features to Hurst parameters.
    """

    def __init__(self, **kwargs):
        """
        Initialize the Neural Network estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator parameters including:
            - hidden_layer_sizes: tuple, sizes of hidden layers (default: (100, 50))
            - activation: str, activation function (default: 'relu')
            - solver: str, optimization solver (default: 'adam')
            - alpha: float, L2 regularization (default: 0.0001)
            - learning_rate: str, learning rate schedule (default: 'adaptive')
            - max_iter: int, maximum iterations (default: 1000)
            - random_state: int, random seed (default: 42)
            - feature_extraction_method: str, feature extraction method (default: 'statistical')
        """
        # Set default parameters
        default_params = {
            "hidden_layer_sizes": (100, 50),
            "activation": "relu",
            "solver": "adam",
            "alpha": 0.0001,
            "learning_rate": "adaptive",
            "max_iter": 1000,
            "random_state": 42,
            "feature_extraction_method": "statistical",
        }

        # Update with provided parameters
        default_params.update(kwargs)
        super().__init__(**default_params)

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not isinstance(self.parameters["hidden_layer_sizes"], (tuple, list)):
            raise ValueError("hidden_layer_sizes must be a tuple or list")

        if self.parameters["activation"] not in [
            "identity",
            "logistic",
            "tanh",
            "relu",
        ]:
            raise ValueError(
                "activation must be one of: identity, logistic, tanh, relu"
            )

        if self.parameters["solver"] not in ["lbfgs", "sgd", "adam"]:
            raise ValueError("solver must be one of: lbfgs, sgd, adam")

        if self.parameters["alpha"] <= 0:
            raise ValueError("alpha must be positive")

        if self.parameters["max_iter"] <= 0:
            raise ValueError("max_iter must be positive")

    def _create_model(self) -> MLPRegressor:
        """
        Create the neural network model.

        Returns
        -------
        MLPRegressor
            The neural network model
        """
        return MLPRegressor(
            hidden_layer_sizes=self.parameters["hidden_layer_sizes"],
            activation=self.parameters["activation"],
            solver=self.parameters["solver"],
            alpha=self.parameters["alpha"],
            learning_rate=self.parameters["learning_rate"],
            max_iter=self.parameters["max_iter"],
            random_state=self.parameters["random_state"],
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=10,
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the neural network model.

        Returns
        -------
        dict
            Model information
        """
        return {
            "model_type": "Neural Network (MLP)",
            "hidden_layers": self.parameters["hidden_layer_sizes"],
            "activation": self.parameters["activation"],
            "solver": self.parameters["solver"],
            "regularization": self.parameters["alpha"],
            "feature_extraction": self.feature_extraction_method,
        }
