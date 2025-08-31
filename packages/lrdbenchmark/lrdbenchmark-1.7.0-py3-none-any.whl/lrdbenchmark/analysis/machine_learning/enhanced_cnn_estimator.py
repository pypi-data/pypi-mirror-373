"""
Enhanced Convolutional Neural Network Estimator for Long-Range Dependence Analysis

This module provides an enhanced CNN-based estimator with adaptive input sizes,
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

try:
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Enhanced CNN estimator will not work.")

from .base_ml_estimator import BaseMLEstimator


class AdaptiveCNN1D(nn.Module):
    """
    Enhanced 1D Convolutional Neural Network with adaptive architecture.

    Features:
    - Adaptive pooling for variable input sizes
    - Residual connections
    - Batch normalization
    - Dropout regularization
    - Multi-scale feature extraction
    """

    def __init__(
        self,
        input_length: int,
        num_features: int = 1,
        conv_channels: List[int] = [16, 32, 64],  # Reduced for memory efficiency
        fc_layers: List[int] = [128, 64],  # Reduced for memory efficiency
        dropout_rate: float = 0.3,
        use_residual: bool = True,
        use_attention: bool = True,
        use_gradient_checkpointing: bool = True,  # New: gradient checkpointing
    ):
        """
        Initialize the adaptive CNN model.

        Parameters
        ----------
        input_length : int
            Length of input time series
        num_features : int
            Number of input features (default: 1 for univariate)
        conv_channels : list
            Number of channels in each convolutional layer
        fc_layers : list
            Number of neurons in each fully connected layer
        dropout_rate : float
            Dropout rate for regularization
        use_residual : bool
            Whether to use residual connections
        use_attention : bool
            Whether to use attention mechanism
        """
        super(AdaptiveCNN1D, self).__init__()

        self.input_length = input_length
        self.num_features = num_features
        self.conv_channels = conv_channels
        self.use_residual = use_residual
        self.use_attention = use_attention
        self.use_gradient_checkpointing = use_gradient_checkpointing

        # Convolutional layers with residual connections
        self.conv_layers = nn.ModuleList()
        self.bn_layers = nn.ModuleList()
        self.residual_layers = nn.ModuleList()
        
        in_channels = num_features
        
        for i, out_channels in enumerate(conv_channels):
            # Main conv layer
            conv_layer = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=3, padding=1),
                nn.BatchNorm1d(out_channels),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            )
            self.conv_layers.append(conv_layer)
            
            # Batch norm for residual
            self.bn_layers.append(nn.BatchNorm1d(out_channels))
            
            # Residual connection (if input and output channels match)
            if use_residual and in_channels == out_channels:
                self.residual_layers.append(nn.Identity())
            elif use_residual:
                self.residual_layers.append(
                    nn.Conv1d(in_channels, out_channels, kernel_size=1)
                )
            else:
                self.residual_layers.append(nn.Identity())
            
            in_channels = out_channels

        # Attention mechanism
        if use_attention:
            self.attention = nn.MultiheadAttention(
                embed_dim=conv_channels[-1], 
                num_heads=4,  # Reduced for memory efficiency
                batch_first=True
            )
        else:
            self.attention = None

        # Enable gradient checkpointing if requested
        if use_gradient_checkpointing:
            # Use standard checkpoint for compatibility
            self._use_checkpoint = True
        else:
            self._use_checkpoint = False

        # Adaptive pooling
        self.adaptive_pool = nn.AdaptiveAvgPool1d(1)
        
        # Global feature extraction
        self.global_features = nn.Sequential(
            nn.Linear(conv_channels[-1], conv_channels[-1] // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(conv_channels[-1] // 2, conv_channels[-1] // 4),
            nn.ReLU(),
            nn.Dropout(dropout_rate)
        )

        # Fully connected layers
        fc_input_size = conv_channels[-1] // 4
        fc_layers = [fc_input_size] + fc_layers + [1]
        fc_modules = []

        for i in range(len(fc_layers) - 1):
            fc_modules.extend([
                nn.Linear(fc_layers[i], fc_layers[i + 1]),
                nn.ReLU() if i < len(fc_layers) - 2 else nn.Identity(),
                nn.Dropout(dropout_rate) if i < len(fc_layers) - 2 else nn.Identity(),
            ])

        self.fc_layers = nn.Sequential(*fc_modules)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, num_features, input_length)

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, 1)
        """
        # Apply convolutional layers with residual connections
        for i, (conv_layer, bn_layer, residual_layer) in enumerate(
            zip(self.conv_layers, self.bn_layers, self.residual_layers)
        ):
            identity = x if i == 0 else identity
            
            # Main conv path with optional checkpointing
            if self._use_checkpoint:
                out = torch.utils.checkpoint.checkpoint(
                    conv_layer, x, use_reentrant=False
                )
            else:
                out = conv_layer(x)
            
            # Residual connection
            if self.use_residual and x.size(1) == out.size(1):
                out = out + residual_layer(identity)
            elif self.use_residual:
                out = out + residual_layer(identity)
            
            # Batch norm and activation
            out = bn_layer(out)
            out = F.relu(out)
            
            # Update for next iteration
            x = out
            identity = out

        # Attention mechanism with optional checkpointing
        if self.attention is not None:
            # Reshape for attention: (batch, seq_len, features)
            x_attn = x.transpose(1, 2)
            
            if self._use_checkpoint:
                attn_out = torch.utils.checkpoint.checkpoint(
                    lambda q, k, v: self.attention(q, k, v)[0],
                    x_attn, x_attn, x_attn,
                    use_reentrant=False
                )
            else:
                attn_out, _ = self.attention(x_attn, x_attn, x_attn)
            
            x = attn_out.transpose(1, 2)  # Back to (batch, features, seq_len)

        # Global average pooling
        x = self.adaptive_pool(x).squeeze(-1)  # (batch, features)

        # Global feature extraction
        x = self.global_features(x)

        # Fully connected layers
        x = self.fc_layers(x)

        return x


class EnhancedCNNEstimator(BaseMLEstimator):
    """
    Enhanced CNN estimator for Hurst parameter estimation.

    Features:
    - Adaptive input size handling
    - Comprehensive training curriculum
    - Enhanced architecture with residual connections and attention
    - Development vs production workflow
    - Automatic model saving and loading
    """

    def __init__(self, **kwargs):
        """
        Initialize the enhanced CNN estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator parameters including:
            - conv_channels: list, number of channels in conv layers (default: [32, 64, 128, 256])
            - fc_layers: list, number of neurons in FC layers (default: [512, 256, 128, 64])
            - dropout_rate: float, dropout rate (default: 0.3)
            - learning_rate: float, learning rate (default: 0.001)
            - batch_size: int, batch size for training (default: 32)
            - epochs: int, number of training epochs (default: 200)
            - use_residual: bool, use residual connections (default: True)
            - use_attention: bool, use attention mechanism (default: True)
            - feature_extraction_method: str, feature extraction method (default: 'raw')
            - random_state: int, random seed (default: 42)
            - model_save_path: str, path to save trained models (default: 'models/enhanced_cnn')
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for Enhanced CNN estimator")

        # Set default parameters
        default_params = {
            "conv_channels": [16, 32, 64],  # Reduced for memory efficiency
            "fc_layers": [128, 64],  # Reduced for memory efficiency
            "dropout_rate": 0.3,
            "learning_rate": 0.001,
            "batch_size": 16,  # Reduced for memory efficiency
            "epochs": 200,
            "use_residual": True,
            "use_attention": True,
            "feature_extraction_method": "raw",
            "random_state": 42,
            "model_save_path": "models/enhanced_cnn",
            "early_stopping_patience": 20,
            "learning_rate_scheduler": True,
            "gradient_clipping": True,
            "max_grad_norm": 1.0,
            "use_gradient_checkpointing": False,  # Temporarily disabled for debugging
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
        if self.parameters["dropout_rate"] < 0 or self.parameters["dropout_rate"] > 1:
            raise ValueError("dropout_rate must be between 0 and 1")

        if self.parameters["learning_rate"] <= 0:
            raise ValueError("learning_rate must be positive")

        if self.parameters["batch_size"] <= 0:
            raise ValueError("batch_size must be positive")

        if self.parameters["epochs"] <= 0:
            raise ValueError("epochs must be positive")

        if not isinstance(self.parameters["conv_channels"], list) or len(self.parameters["conv_channels"]) == 0:
            raise ValueError("conv_channels must be a non-empty list")

        if not isinstance(self.parameters["fc_layers"], list) or len(self.parameters["fc_layers"]) == 0:
            raise ValueError("fc_layers must be a non-empty list")

    def _create_model(self, input_length: int, num_features: int = 1) -> AdaptiveCNN1D:
        """
        Create the enhanced CNN model.

        Parameters
        ----------
        input_length : int
            Length of input time series
        num_features : int
            Number of input features

        Returns
        -------
        AdaptiveCNN1D
            The enhanced CNN model
        """
        return AdaptiveCNN1D(
            input_length=input_length,
            num_features=num_features,
            conv_channels=self.parameters["conv_channels"],
            fc_layers=self.parameters["fc_layers"],
            dropout_rate=self.parameters["dropout_rate"],
            use_residual=self.parameters["use_residual"],
            use_attention=self.parameters["use_attention"],
        ).to(self.device)

    def _prepare_data(self, data: np.ndarray) -> torch.Tensor:
        """
        Prepare data for CNN input.

        Parameters
        ----------
        data : np.ndarray
            Input time series data

        Returns
        -------
        torch.Tensor
            Prepared tensor for CNN
        """
        # Ensure data is 1D
        if data.ndim > 1:
            data = data.flatten()
        
        # Normalize the data
        data_normalized = (data - np.mean(data)) / (np.std(data) + 1e-8)
        
        # Reshape for CNN: (batch=1, channels=1, length)
        data_tensor = torch.FloatTensor(data_normalized).unsqueeze(0).unsqueeze(0)  # (batch, channels, length)

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
            
            # Reshape for CNN: (channels=1, length)
            data_reshaped = data_normalized.reshape(1, -1)  # (channels=1, length)
            X.append(data_reshaped)
            y.append(label)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=self.parameters["random_state"]
        )

        # Create datasets
        train_dataset = TensorDataset(
            torch.FloatTensor(np.array(X_train)),
            torch.FloatTensor(y_train)
        )
        val_dataset = TensorDataset(
            torch.FloatTensor(np.array(X_val)),
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
        Train the enhanced CNN model.

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
        input_length = len(data_list[0])
        print(f"Training Enhanced CNN with input length: {input_length}")

        # Create model
        self.model = self._create_model(input_length, num_features=1)
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
                model_output = self.model(batch_X)
                # Handle checkpointing output format
                if isinstance(model_output, tuple):
                    outputs = model_output[0].squeeze()
                else:
                    outputs = model_output.squeeze()
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
                    model_output = self.model(batch_X)
                    # Handle checkpointing output format
                    if isinstance(model_output, tuple):
                        outputs = model_output[0].squeeze()
                    else:
                        outputs = model_output.squeeze()
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
        
        model_path = os.path.join(save_path, "enhanced_cnn_model.pth")
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history,
            'parameters': self.parameters,
            'input_length': self.model.input_length,
        }, model_path)
        
        print(f"Model saved to: {model_path}")

    def _load_model(self, model_path: str):
        """Load a trained model."""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Create model with saved input length
        input_length = checkpoint['input_length']
        self.model = self._create_model(input_length, num_features=1)
        
        # Load model state
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        # Load training history
        self.training_history = checkpoint.get('training_history', {})
        
        print(f"Model loaded from: {model_path}")

    def _try_load_pretrained_model(self) -> bool:
        """
        Try to load a pretrained PyTorch model for enhanced CNN.
        
        Returns
        -------
        bool
            True if pretrained model was loaded successfully, False otherwise
        """
        try:
            # Check multiple possible paths for the pretrained model
            possible_paths = [
                os.path.join(self.parameters["model_save_path"], "enhanced_cnn_model.pth"),
                "models/enhanced_cnn/enhanced_cnn_model.pth",
                "../models/enhanced_cnn/enhanced_cnn_model.pth",
                "../../models/enhanced_cnn/enhanced_cnn_model.pth",
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "enhanced_cnn", "enhanced_cnn_model.pth"),
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
        Estimate Hurst parameter using enhanced CNN.

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
            raise ImportError("PyTorch is required for Enhanced CNN estimator")

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
                
                method = "Enhanced CNN (Trained Neural Network)"
            else:
                # We have a scikit-learn model
                # Ensure we extract features properly for scikit-learn models
                if self.parameters.get("feature_extraction_method", "statistical") == "raw":
                    # If using raw features, we need to ensure the data matches the expected dimensions
                    if data.ndim == 1:
                        data = data.reshape(1, -1)
                    features = data
                else:
                    # Extract features using the configured method
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
                
                method = "Enhanced CNN (Pretrained ML)"
        else:
            # Create and use untrained model (fallback)
            if data.ndim == 1:
                data = data.reshape(1, -1)
            
            data_tensor = self._prepare_data(data)
            
            # Create fresh model
            input_length = data_tensor.shape[2]
            self.model = self._create_model(input_length, num_features=1)
            
            # Make prediction
            with torch.no_grad():
                output = self.model(data_tensor)
                estimated_hurst = output.item()
                estimated_hurst = max(0.0, min(1.0, estimated_hurst))
            
            confidence_interval = (
                max(0, estimated_hurst - 0.1),
                min(1, estimated_hurst + 0.1),
            )
            
            method = "Enhanced CNN (Untrained Neural Network)"

        # Store results
        self.results = {
            "hurst_parameter": estimated_hurst,
            "confidence_interval": confidence_interval,
            "std_error": 0.1,  # Simplified
            "method": method,
            "model_info": {
                "model_type": "EnhancedCNN1D",
                "conv_channels": self.parameters["conv_channels"],
                "fc_layers": self.parameters["fc_layers"],
                "dropout_rate": self.parameters["dropout_rate"],
                "use_residual": self.parameters["use_residual"],
                "use_attention": self.parameters["use_attention"],
            },
        }

        return self.results

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the enhanced CNN model.

        Returns
        -------
        dict
            Model information
        """
        info = {
            "model_type": "EnhancedCNN1D",
            "architecture": "Enhanced 1D CNN with Residual Connections and Attention",
            "conv_channels": self.parameters["conv_channels"],
            "fc_layers": self.parameters["fc_layers"],
            "dropout_rate": self.parameters["dropout_rate"],
            "use_residual": self.parameters["use_residual"],
            "use_attention": self.parameters["use_attention"],
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
