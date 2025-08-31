"""
Base class for pre-trained neural network models.

This provides a common interface for all pre-trained models used in LRDBench.
"""

import numpy as np
from typing import Dict, Any, Optional
import warnings

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Pre-trained models will not work.")


class BasePretrainedModel:
    """
    Base class for pre-trained neural network models.

    This class provides a common interface for loading and using pre-trained
    models without requiring training during runtime.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the pre-trained model.

        Parameters
        ----------
        model_path : str, optional
            Path to the pre-trained model file
        """
        self.model = None
        self.model_path = model_path
        self.is_loaded = False

        if TORCH_AVAILABLE and model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> bool:
        """
        Load a pre-trained model from file.

        Parameters
        ----------
        model_path : str
            Path to the pre-trained model file

        Returns
        -------
        bool
            True if model loaded successfully, False otherwise
        """
        if not TORCH_AVAILABLE:
            warnings.warn("PyTorch not available. Cannot load model.")
            return False

        try:
            # Load the model
            self.model = torch.load(model_path, map_location="cpu")
            self.model.eval()  # Set to evaluation mode
            self.is_loaded = True
            return True
        except Exception as e:
            warnings.warn(f"Failed to load model from {model_path}: {e}")
            return False

    def predict(self, data: np.ndarray) -> np.ndarray:
        """
        Make predictions using the pre-trained model.

        Parameters
        ----------
        data : np.ndarray
            Input data

        Returns
        -------
        np.ndarray
            Model predictions
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for model inference.")

        # Convert numpy array to torch tensor
        if isinstance(data, np.ndarray):
            data = torch.from_numpy(data).float()

        # Ensure data is on the same device as the model
        device = next(self.model.parameters()).device
        data = data.to(device)

        # Make prediction
        with torch.no_grad():
            prediction = self.model(data)

        # Convert back to numpy
        if isinstance(prediction, torch.Tensor):
            prediction = prediction.cpu().numpy()

        return prediction

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns
        -------
        dict
            Model information
        """
        info = {
            "is_loaded": self.is_loaded,
            "model_path": self.model_path,
            "torch_available": TORCH_AVAILABLE,
        }

        if self.is_loaded and self.model is not None:
            info["model_type"] = type(self.model).__name__
            info["total_parameters"] = sum(p.numel() for p in self.model.parameters())

        return info
