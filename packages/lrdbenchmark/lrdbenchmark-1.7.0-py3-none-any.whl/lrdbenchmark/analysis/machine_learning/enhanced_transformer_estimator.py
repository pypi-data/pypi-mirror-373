"""
Enhanced Transformer Estimator for Long-Range Dependence Analysis

This module provides an enhanced Transformer-based estimator with adaptive input sizes,
improved architecture, and comprehensive training capabilities.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import warnings
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import torch.nn.functional as F
import math

try:
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Enhanced Transformer estimator will not work.")

from .base_ml_estimator import BaseMLEstimator


class PositionalEncoding(nn.Module):
    """
    Enhanced positional encoding for transformer models.

    Adds positional information to input embeddings to help the model
    understand the temporal order of the sequence.
    """

    def __init__(self, d_model: int, max_len: int = 10000):
        """
        Initialize enhanced positional encoding.

        Parameters
        ----------
        d_model : int
            Dimension of the model embeddings
        max_len : int
            Maximum sequence length
        """
        super(PositionalEncoding, self).__init__()

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)

        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (seq_len, batch_size, d_model)

        Returns
        -------
        torch.Tensor
            Input with positional encoding added
        """
        return x + self.pe[: x.size(0), :]


class AdaptiveTransformer(nn.Module):
    """
    Enhanced Transformer model with adaptive architecture.

    Features:
    - Multi-head self-attention layers
    - Positional encoding
    - Feed-forward networks
    - Layer normalization
    - Dropout regularization
    - Adaptive input handling
    - Global pooling
    """

    def __init__(
        self,
        input_dim: int = 1,
        d_model: int = 256,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 1024,
        dropout: float = 0.1,
        max_seq_length: int = 10000,
        use_layer_norm: bool = True,
        use_residual: bool = True,
    ):
        """
        Initialize the adaptive transformer model.

        Parameters
        ----------
        input_dim : int
            Input dimension (default: 1 for univariate time series)
        d_model : int
            Model dimension (embedding size)
        nhead : int
            Number of attention heads
        num_layers : int
            Number of transformer layers
        dim_feedforward : int
            Dimension of feedforward networks
        dropout : float
            Dropout rate
        max_seq_length : int
            Maximum sequence length
        use_layer_norm : bool
            Whether to use layer normalization
        use_residual : bool
            Whether to use residual connections
        """
        super(AdaptiveTransformer, self).__init__()

        self.d_model = d_model
        self.input_dim = input_dim
        self.use_layer_norm = use_layer_norm
        self.use_residual = use_residual

        # Input projection
        self.input_projection = nn.Linear(input_dim, d_model)

        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, max_seq_length)

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            norm_first=use_layer_norm,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Layer normalization
        if use_layer_norm:
            self.layer_norm = nn.LayerNorm(d_model)
        else:
            self.layer_norm = None

        # Global pooling
        self.global_pool = nn.AdaptiveAvgPool1d(1)

        # Output projection layers
        self.output_projection = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, d_model // 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 4, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the transformer.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, seq_len, input_dim)

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, 1)
        """
        # Project input to d_model dimensions
        x = self.input_projection(x)  # (batch, seq_len, d_model)

        # Add positional encoding
        x = x.transpose(0, 1)  # (seq_len, batch, d_model)
        x = self.pos_encoder(x)
        x = x.transpose(0, 1)  # (batch, seq_len, d_model)

        # Apply transformer encoder
        x = self.transformer_encoder(x)  # (batch, seq_len, d_model)

        # Apply layer normalization if enabled
        if self.layer_norm is not None:
            x = self.layer_norm(x)

        # Global average pooling
        x = x.transpose(1, 2)  # (batch, d_model, seq_len)
        x = self.global_pool(x)  # (batch, d_model, 1)
        x = x.squeeze(-1)  # (batch, d_model)

        # Output projection
        x = self.output_projection(x)  # (batch, 1)

        return x


class EnhancedTransformerEstimator(BaseMLEstimator):
    """
    Enhanced Transformer estimator for Hurst parameter estimation.

    Features:
    - Adaptive input size handling
    - Comprehensive training curriculum
    - Enhanced architecture with attention
    - Development vs production workflow
    - Automatic model saving and loading
    """

    def __init__(self, **kwargs):
        """
        Initialize the enhanced Transformer estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator parameters including:
            - d_model: int, model dimension (default: 256)
            - nhead: int, number of attention heads (default: 8)
            - num_layers: int, number of transformer layers (default: 6)
            - dim_feedforward: int, feedforward dimension (default: 1024)
            - dropout: float, dropout rate (default: 0.1)
            - learning_rate: float, learning rate (default: 0.0001)
            - batch_size: int, batch size for training (default: 16)
            - epochs: int, number of training epochs (default: 200)
            - use_layer_norm: bool, use layer normalization (default: True)
            - use_residual: bool, use residual connections (default: True)
            - feature_extraction_method: str, feature extraction method (default: 'raw')
            - random_state: int, random seed (default: 42)
            - model_save_path: str, path to save trained models (default: 'models/enhanced_transformer')
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for Enhanced Transformer estimator")

        # Set default parameters
        default_params = {
            "d_model": 256,
            "nhead": 8,
            "num_layers": 6,
            "dim_feedforward": 1024,
            "dropout": 0.1,
            "learning_rate": 0.0001,
            "batch_size": 16,
            "epochs": 200,
            "use_layer_norm": True,
            "use_residual": True,
            "feature_extraction_method": "raw",
            "random_state": 42,
            "model_save_path": "models/enhanced_transformer",
            "early_stopping_patience": 20,
            "learning_rate_scheduler": True,
            "gradient_clipping": True,
            "max_grad_norm": 1.0,
        }

        # Update with provided parameters
        default_params.update(kwargs)
        super().__init__(**default_params)

        # Set random seeds for reproducibility
        torch.manual_seed(self.parameters["random_state"])
        if torch.cuda.is_available():
            torch.cuda.manual_seed(self.parameters["random_state"])

        # Model components
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.scheduler = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Training history
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'train_mae': [],
            'val_mae': []
        }

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["d_model"] <= 0:
            raise ValueError("d_model must be positive")

        if self.parameters["nhead"] <= 0:
            raise ValueError("nhead must be positive")

        if self.parameters["num_layers"] <= 0:
            raise ValueError("num_layers must be positive")

        if self.parameters["dim_feedforward"] <= 0:
            raise ValueError("dim_feedforward must be positive")

        if self.parameters["dropout"] < 0 or self.parameters["dropout"] > 1:
            raise ValueError("dropout must be between 0 and 1")

        if self.parameters["learning_rate"] <= 0:
            raise ValueError("learning_rate must be positive")

        if self.parameters["batch_size"] <= 0:
            raise ValueError("batch_size must be positive")

        if self.parameters["epochs"] <= 0:
            raise ValueError("epochs must be positive")

        # Check if d_model is divisible by nhead
        if self.parameters["d_model"] % self.parameters["nhead"] != 0:
            raise ValueError("d_model must be divisible by nhead")

    def _create_model(self, input_dim: int = 1) -> AdaptiveTransformer:
        """
        Create the enhanced transformer model.

        Parameters
        ----------
        input_dim : int
            Input dimension

        Returns
        -------
        AdaptiveTransformer
            The enhanced transformer model
        """
        return AdaptiveTransformer(
            input_dim=input_dim,
            d_model=self.parameters["d_model"],
            nhead=self.parameters["nhead"],
            num_layers=self.parameters["num_layers"],
            dim_feedforward=self.parameters["dim_feedforward"],
            dropout=self.parameters["dropout"],
            use_layer_norm=self.parameters["use_layer_norm"],
            use_residual=self.parameters["use_residual"],
        ).to(self.device)

    def _prepare_data(self, data: np.ndarray) -> torch.Tensor:
        """
        Prepare data for transformer input.

        Parameters
        ----------
        data : np.ndarray
            Input time series data

        Returns
        -------
        torch.Tensor
            Prepared tensor for transformer
        """
        # Ensure data is 1D
        if data.ndim > 1:
            data = data.flatten()
        
        # Normalize the data
        data_normalized = (data - np.mean(data)) / (np.std(data) + 1e-8)
        
        # Reshape for transformer: (seq_len, features)
        data_reshaped = data_normalized.reshape(-1, 1)
        
        # Convert to torch tensor and add batch dimension
        data_tensor = torch.FloatTensor(data_reshaped).unsqueeze(0)  # (batch=1, seq_len, features=1)

        return data_tensor.to(self.device)

    def _create_training_data(self, data_list: List[np.ndarray], labels: List[float]) -> Tuple[DataLoader, DataLoader]:
        """
        Create training and validation data loaders.

        Parameters
        ----------
        data_list : List[np.ndarray]
            List of training data samples
        labels : List[float]
            List of corresponding labels

        Returns
        -------
        Tuple[DataLoader, DataLoader]
            Training and validation data loaders
        """
        # Prepare data
        X = []
        y = []
        
        for data, label in zip(data_list, labels):
            # Ensure data is 1D
            if data.ndim > 1:
                data = data.flatten()
            
            # Normalize the data
            data_normalized = (data - np.mean(data)) / (np.std(data) + 1e-8)
            
            # Reshape for Transformer: (seq_len, features)
            data_reshaped = data_normalized.reshape(-1, 1)  # (seq_len, 1)
            X.append(data_reshaped)
            y.append(label)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=self.parameters["random_state"]
        )

        # Create datasets - ensure proper tensor shapes
        # X_train and X_val are lists of (seq_len, 1) arrays
        # We need to stack them into (batch_size, seq_len, 1) tensors
        train_dataset = TensorDataset(
            torch.stack([torch.FloatTensor(x) for x in X_train]),
            torch.FloatTensor(y_train)
        )
        val_dataset = TensorDataset(
            torch.stack([torch.FloatTensor(x) for x in X_val]),
            torch.FloatTensor(y_val)
        )

        # Create data loaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.parameters["batch_size"], 
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=self.parameters["batch_size"], 
            shuffle=False
        )

        return train_loader, val_loader

    def train_model(self, data_list: List[np.ndarray], labels: List[float], save_model: bool = True) -> Dict[str, Any]:
        """
        Train the enhanced transformer model.

        Parameters
        ----------
        data_list : List[np.ndarray]
            List of training data samples
        labels : List[float]
            List of corresponding labels
        save_model : bool
            Whether to save the trained model

        Returns
        -------
        Dict[str, Any]
            Training results
        """
        if not data_list or not labels:
            raise ValueError("Training data and labels cannot be empty")

        # Determine input size from data
        input_dim = data_list[0].shape[-1] if data_list[0].ndim > 1 else 1
        print(f"Training Enhanced Transformer with input dimension: {input_dim}")

        # Create model
        self.model = self._create_model(input_dim=input_dim)
        self.optimizer = optim.Adam(
            self.model.parameters(), 
            lr=self.parameters["learning_rate"]
        )
        self.criterion = nn.MSELoss()

        # Learning rate scheduler
        if self.parameters["learning_rate_scheduler"]:
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer, mode='min', factor=0.5, patience=10
            )

        # Create data loaders
        train_loader, val_loader = self._create_training_data(data_list, labels)

        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        early_stopping_patience = self.parameters["early_stopping_patience"]

        print(f"Starting training for {self.parameters['epochs']} epochs...")

        for epoch in range(self.parameters["epochs"]):
            # Training phase
            self.model.train()
            train_loss = 0.0
            train_mae = 0.0
            
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(batch_X).squeeze()
                loss = self.criterion(outputs, batch_y)
                
                loss.backward()
                
                # Gradient clipping
                if self.parameters["gradient_clipping"]:
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(), 
                        self.parameters["max_grad_norm"]
                    )
                
                self.optimizer.step()
                
                train_loss += loss.item()
                train_mae += torch.mean(torch.abs(outputs - batch_y)).item()

            # Validation phase
            self.model.eval()
            val_loss = 0.0
            val_mae = 0.0
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = self.model(batch_X).squeeze()
                    loss = self.criterion(outputs, batch_y)
                    
                    val_loss += loss.item()
                    val_mae += torch.mean(torch.abs(outputs - batch_y)).item()

            # Calculate averages
            train_loss /= len(train_loader)
            train_mae /= len(train_loader)
            val_loss /= len(val_loader)
            val_mae /= len(val_loader)

            # Update learning rate scheduler
            if self.scheduler is not None:
                self.scheduler.step(val_loss)

            # Store history
            self.training_history['train_loss'].append(train_loss)
            self.training_history['val_loss'].append(val_loss)
            self.training_history['train_mae'].append(train_mae)
            self.training_history['val_mae'].append(val_mae)

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                
                # Save best model
                if save_model:
                    self._save_model()
            else:
                patience_counter += 1

            # Print progress
            if (epoch + 1) % 20 == 0:
                print(f"Epoch [{epoch+1}/{self.parameters['epochs']}] - "
                      f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                      f"Train MAE: {train_mae:.4f}, Val MAE: {val_mae:.4f}")

            # Early stopping check
            if patience_counter >= early_stopping_patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

        print("Training completed!")
        
        return {
            'final_train_loss': train_loss,
            'final_val_loss': val_loss,
            'final_train_mae': train_mae,
            'final_val_mae': val_mae,
            'best_val_loss': best_val_loss,
            'epochs_trained': epoch + 1
        }

    def _save_model(self):
        """Save the trained model."""
        save_path = self.parameters["model_save_path"]
        os.makedirs(save_path, exist_ok=True)
        
        model_path = os.path.join(save_path, "enhanced_transformer_model.pth")
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history,
            'parameters': self.parameters,
            'input_dim': self.model.input_dim,
        }, model_path)
        
        print(f"Model saved to: {model_path}")

    def _load_model(self, model_path: str):
        """Load a trained model."""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Create model with saved input dimension
        input_dim = checkpoint['input_dim']
        self.model = self._create_model(input_dim=input_dim)
        
        # Load model state
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        # Load training history
        self.training_history = checkpoint.get('training_history', {})
        
        print(f"Model loaded from: {model_path}")

    def _try_load_pretrained_model(self) -> bool:
        """
        Try to load a pretrained PyTorch model for enhanced Transformer.
        
        Returns
        -------
        bool
            True if pretrained model was loaded successfully, False otherwise
        """
        try:
            # Check multiple possible paths for the pretrained model
            possible_paths = [
                os.path.join(self.parameters["model_save_path"], "enhanced_transformer_model.pth"),
                "models/enhanced_transformer/enhanced_transformer_model.pth",
                "../models/enhanced_transformer/enhanced_transformer_model.pth",
                "../../models/enhanced_transformer/enhanced_transformer_model.pth",
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "enhanced_transformer", "enhanced_transformer_model.pth"),
            ]
            
            for model_path in possible_paths:
                if os.path.exists(model_path):
                    # Load trained model
                    self._load_model(model_path)
                    print(f"✅ Loaded pretrained PyTorch model: {model_path}")
                    return True
            
            # If no PyTorch model found, will create untrained PyTorch model
            return False
            
        except Exception as e:
            print(f"⚠️ Could not load pretrained model for {self.__class__.__name__}: {e}")
            return False

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using enhanced transformer.

        Parameters
        ----------
        data : np.ndarray
            Time series data

        Returns
        -------
        dict
            Estimation results including:
            - 'hurst_parameter': estimated Hurst parameter
            - 'confidence_interval': confidence interval
            - 'model_info': model information
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for Enhanced Transformer estimator")

        # Try to load pretrained model first
        if self._try_load_pretrained_model():
            # Check if we loaded a PyTorch model or scikit-learn model
            if hasattr(self.model, 'forward') and callable(getattr(self.model, 'forward', None)):
                # We have a PyTorch model
                data_tensor = self._prepare_data(data)
                
                # Make prediction
                with torch.no_grad():
                    output = self.model(data_tensor)
                    estimated_hurst = output.item()
                    estimated_hurst = max(0.0, min(1.0, estimated_hurst))
                
                confidence_interval = (
                    max(0, estimated_hurst - 0.1),
                    min(1, estimated_hurst + 0.1),
                )
                
                method = "Enhanced Transformer (Trained Neural Network)"
            else:
                # We have a scikit-learn model
                features = self.extract_features(data)
                if features.ndim == 1:
                    features = features.reshape(1, -1)
                
                # Scale features
                features_scaled = self.scaler.transform(features)
                
                # Make prediction
                estimated_hurst = self.model.predict(features_scaled)[0]
                estimated_hurst = max(0.0, min(1.0, estimated_hurst))
                
                confidence_interval = (
                    max(0, estimated_hurst - 0.1),
                    min(1, estimated_hurst + 0.1),
                )
                
                method = "Enhanced Transformer (Pretrained ML)"
        else:
            # Create and use untrained model (fallback)
            if data.ndim == 1:
                data = data.reshape(1, -1)
            
            data_tensor = self._prepare_data(data)
            
            # Create fresh model
            input_dim = data_tensor.shape[-1]
            self.model = self._create_model(input_dim=input_dim)
            
            # Make prediction
            with torch.no_grad():
                output = self.model(data_tensor)
                estimated_hurst = output.item()
                estimated_hurst = max(0.0, min(1.0, estimated_hurst))
            
            confidence_interval = (
                max(0, estimated_hurst - 0.1),
                min(1, estimated_hurst + 0.1),
            )
            
            method = "Enhanced Transformer (Untrained Neural Network)"

        # Store results
        self.results = {
            "hurst_parameter": estimated_hurst,
            "confidence_interval": confidence_interval,
            "std_error": 0.1,  # Simplified
            "method": method,
            "model_info": {
                "model_type": "EnhancedTransformer",
                "d_model": self.parameters["d_model"],
                "nhead": self.parameters["nhead"],
                "num_layers": self.parameters["num_layers"],
                "dim_feedforward": self.parameters["dim_feedforward"],
                "dropout": self.parameters["dropout"],
                "use_layer_norm": self.parameters["use_layer_norm"],
                "use_residual": self.parameters["use_residual"],
            },
        }

        return self.results

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the enhanced transformer model.

        Returns
        -------
        dict
            Model information
        """
        info = {
            "model_type": "EnhancedTransformer",
            "architecture": "Enhanced Transformer with Multi-Head Attention",
            "d_model": self.parameters["d_model"],
            "nhead": self.parameters["nhead"],
            "num_layers": self.parameters["num_layers"],
            "dim_feedforward": self.parameters["dim_feedforward"],
            "dropout": self.parameters["dropout"],
            "use_layer_norm": self.parameters["use_layer_norm"],
            "use_residual": self.parameters["use_residual"],
            "learning_rate": self.parameters["learning_rate"],
            "batch_size": self.parameters["batch_size"],
            "epochs": self.parameters["epochs"],
            "device": str(self.device),
            "torch_available": TORCH_AVAILABLE,
        }

        if hasattr(self, "model") and self.model is not None:
            info["model_created"] = True
            info["total_parameters"] = sum(p.numel() for p in self.model.parameters())
            info["trainable_parameters"] = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        else:
            info["model_created"] = False

        return info
