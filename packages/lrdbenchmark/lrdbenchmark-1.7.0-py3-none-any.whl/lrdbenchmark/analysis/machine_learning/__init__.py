"""
Machine Learning Estimators for Long-Range Dependence Analysis

This package provides machine learning-based approaches for estimating
Hurst parameters and long-range dependence characteristics from time series data.

The estimators include:
- Neural Network Regression
- Random Forest Regression
- Support Vector Regression
- Gradient Boosting Regression
- Convolutional Neural Networks
- Recurrent Neural Networks (LSTM/GRU)
- Transformer-based approaches
"""

from .base_ml_estimator import BaseMLEstimator
from .neural_network_estimator import NeuralNetworkEstimator
from .random_forest_estimator import RandomForestEstimator
from .svr_estimator import SVREstimator
from .gradient_boosting_estimator import GradientBoostingEstimator

# Enhanced neural network estimators (replacing old ones)
from .enhanced_cnn_estimator import EnhancedCNNEstimator as CNNEstimator
from .enhanced_lstm_estimator import EnhancedLSTMEstimator as LSTMEstimator
from .enhanced_gru_estimator import EnhancedGRUEstimator as GRUEstimator
from .enhanced_transformer_estimator import EnhancedTransformerEstimator as TransformerEstimator

__all__ = [
    "BaseMLEstimator",
    "NeuralNetworkEstimator",
    "RandomForestEstimator",
    "SVREstimator",
    "GradientBoostingEstimator",
    # Enhanced estimators (aliased to original names)
    "CNNEstimator",
    "LSTMEstimator",
    "GRUEstimator",
    "TransformerEstimator",
]
