"""
Enhanced LSTM Estimator for Long-Range Dependence Analysis

This module provides an enhanced LSTM-based estimator with adaptive input sizes,
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
import gc

try:
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Enhanced LSTM estimator will not work.")

from .base_ml_estimator import BaseMLEstimator


class AdaptiveLSTM(nn.Module):
    """
    Enhanced LSTM model with adaptive architecture.

    Features:
    - Bidirectional LSTM layers
    - Attention mechanism
    - Dropout regularization
    - Adaptive input handling
    - Multi-layer architecture
    - Memory-efficient training
    """

    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,  # Reduced from 128 for memory efficiency
        num_layers: int = 2,    # Reduced from 3 for memory efficiency
        dropout_rate: float = 0.3,
        bidirectional: bool = True,
        use_attention: bool = True,
        attention_heads: int = 4,  # Reduced from 8 for memory efficiency
        use_gradient_checkpointing: bool = True,  # New: gradient checkpointing
    ):
        """
        Initialize the adaptive LSTM model.

        Parameters
        ----------
        input_size : int
            Size of input features
        hidden_size : int
            Size of hidden layers (reduced for memory efficiency)
        num_layers : int
            Number of LSTM layers (reduced for memory efficiency)
        dropout_rate : float
            Dropout rate for regularization
        bidirectional : bool
            Whether to use bidirectional LSTM
        use_attention : bool
            Whether to use attention mechanism
        attention_heads : int
            Number of attention heads (reduced for memory efficiency)
        use_gradient_checkpointing : bool
            Whether to use gradient checkpointing for memory efficiency
        """
        super(AdaptiveLSTM, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.use_attention = use_attention
        self.num_directions = 2 if bidirectional else 1
        self.use_gradient_checkpointing = use_gradient_checkpointing

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout_rate if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True
        )

        # Attention mechanism
        if use_attention:
            self.attention = nn.MultiheadAttention(
                embed_dim=hidden_size * self.num_directions,
                num_heads=attention_heads,
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

        # Output layers
        self.dropout = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(hidden_size * self.num_directions, hidden_size // 2)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size // 2, 1)

        # Global pooling
        self.global_pool = nn.AdaptiveAvgPool1d(1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, seq_len, input_size)

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, 1)
        """
        # LSTM forward pass with optional checkpointing
        if self._use_checkpoint:
            lstm_out = torch.utils.checkpoint.checkpoint(
                lambda x: self.lstm(x)[0], x, use_reentrant=False
            )
        else:
            lstm_out, _ = self.lstm(x)  # Ignore hidden states for now
        # lstm_out shape: (batch_size, seq_len, hidden_size * num_directions)

        # Attention mechanism with optional checkpointing
        if self.attention is not None:
            if self._use_checkpoint:
                attn_out = torch.utils.checkpoint.checkpoint(
                    lambda q, k, v: self.attention(q, k, v)[0],
                    lstm_out, lstm_out, lstm_out,
                    use_reentrant=False
                )
            else:
                attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
            # attn_out shape: (batch_size, seq_len, hidden_size * num_directions)
        else:
            attn_out = lstm_out

        # Global average pooling
        # Transpose for pooling: (batch_size, features, seq_len)
        pooled = self.global_pool(attn_out.transpose(1, 2))
        # pooled shape: (batch_size, features, 1)
        
        # Squeeze and pass through output layers
        pooled = pooled.squeeze(-1)  # (batch_size, features)
        output = self.fc2(self.relu(self.fc1(pooled)))  # (batch_size, 1)

        return output


class EnhancedLSTMEstimator(BaseMLEstimator):
    """
    Enhanced LSTM estimator for Hurst parameter estimation.

    Features:
    - Adaptive input size handling
    - Comprehensive training curriculum
    - Enhanced architecture with attention
    - Development vs production workflow
    - Automatic model saving and loading
    """

    def __init__(self, **kwargs):
        """
        Initialize the enhanced LSTM estimator.

        Parameters
        ----------
        **kwargs : dict
            Estimator parameters including:
            - hidden_size: int, size of hidden layers (default: 128)
            - num_layers: int, number of LSTM layers (default: 3)
            - dropout_rate: float, dropout rate (default: 0.3)
            - learning_rate: float, learning rate (default: 0.001)
            - batch_size: int, batch size for training (default: 32)
            - epochs: int, number of training epochs (default: 200)
            - bidirectional: bool, use bidirectional LSTM (default: True)
            - use_attention: bool, use attention mechanism (default: True)
            - attention_heads: int, number of attention heads (default: 8)
            - feature_extraction_method: str, feature extraction method (default: 'raw')
            - random_state: int, random seed (default: 42)
            - model_save_path: str, path to save trained models (default: 'models/enhanced_lstm')
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for Enhanced LSTM estimator")

        # Set default parameters
        default_params = {
            "hidden_size": 64,  # Reduced for memory efficiency
            "num_layers": 2,    # Reduced for memory efficiency
            "dropout_rate": 0.3,
            "learning_rate": 0.001,
            "batch_size": 16,   # Reduced for memory efficiency
            "epochs": 200,
            "bidirectional": True,
            "use_attention": True,
            "attention_heads": 4,  # Reduced for memory efficiency
            "feature_extraction_method": "raw",
            "random_state": 42,
            "model_save_path": "models/enhanced_lstm",
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
        if self.parameters["hidden_size"] <= 0:
            raise ValueError("hidden_size must be positive")

        if self.parameters["num_layers"] <= 0:
            raise ValueError("num_layers must be positive")

        if self.parameters["dropout_rate"] < 0 or self.parameters["dropout_rate"] > 1:
            raise ValueError("dropout_rate must be between 0 and 1")

        if self.parameters["learning_rate"] <= 0:
            raise ValueError("learning_rate must be positive")

        if self.parameters["batch_size"] <= 0:
            raise ValueError("batch_size must be positive")

        if self.parameters["epochs"] <= 0:
            raise ValueError("epochs must be positive")

        if self.parameters["attention_heads"] <= 0:
            raise ValueError("attention_heads must be positive")

    def _create_model(self, input_size: int = 1) -> AdaptiveLSTM:
        """
        Create the enhanced LSTM model.

        Parameters
        ----------
        input_size : int
            Size of input features

        Returns
        -------
        AdaptiveLSTM
            The enhanced LSTM model
        """
        return AdaptiveLSTM(
            input_size=input_size,
            hidden_size=self.parameters["hidden_size"],
            num_layers=self.parameters["num_layers"],
            dropout_rate=self.parameters["dropout_rate"],
            bidirectional=self.parameters["bidirectional"],
            use_attention=self.parameters["use_attention"],
            attention_heads=self.parameters["attention_heads"],
            use_gradient_checkpointing=self.parameters["use_gradient_checkpointing"], # Pass to AdaptiveLSTM
        ).to(self.device)

    def _prepare_data(self, data: np.ndarray) -> torch.Tensor:
        """
        Prepare data for LSTM input with enhanced preprocessing.

        Parameters
        ----------
        data : np.ndarray
            Input time series data

        Returns
        -------
        torch.Tensor
            Prepared tensor for LSTM
        """
        # Ensure data is 1D
        if data.ndim > 1:
            data = data.flatten()
        
        # Normalize data to improve training stability
        data_normalized = (data - np.mean(data)) / (np.std(data) + 1e-8)
        
        # Reshape for LSTM: (batch_size, seq_len, features)
        data_tensor = torch.FloatTensor(data_normalized).unsqueeze(0).unsqueeze(-1)
        
        return data_tensor.to(self.device)

    def _create_training_data(self, data_list: List[np.ndarray], labels: List[float]) -> Tuple[DataLoader, DataLoader]:
        """
        Create training and validation data loaders with enhanced preprocessing.

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
        # Prepare data with enhanced preprocessing
        X = []
        y = []
        
        for data, label in zip(data_list, labels):
            # Normalize each time series
            if data.ndim > 1:
                data = data.flatten()
            
            # Apply normalization
            data_normalized = (data - np.mean(data)) / (np.std(data) + 1e-8)
            
            # Reshape for LSTM: (seq_len, features)
            data_reshaped = data_normalized.reshape(-1, 1)
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

        # Create data loaders with memory-efficient batch sizes
        # Dynamically adjust batch size based on available GPU memory
        optimal_batch_size = self._get_optimal_batch_size(len(X_train))
        val_batch_size = min(optimal_batch_size, len(X_val))
        
        train_loader = DataLoader(
            train_dataset, 
            batch_size=optimal_batch_size, 
            shuffle=True,
            drop_last=True,
            pin_memory=torch.cuda.is_available()
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=val_batch_size, 
            shuffle=False,
            drop_last=False,
            pin_memory=torch.cuda.is_available()
        )

        return train_loader, val_loader
    
    def _get_optimal_batch_size(self, dataset_size: int) -> int:
        """
        Dynamically determine optimal batch size based on available GPU memory.
        
        Parameters
        ----------
        dataset_size : int
            Size of the training dataset
            
        Returns
        -------
        int
            Optimal batch size
        """
        if not torch.cuda.is_available():
            return min(self.parameters["batch_size"], dataset_size)
        
        try:
            # Get available GPU memory
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            allocated_memory = torch.cuda.memory_allocated(0)
            free_memory = gpu_memory - allocated_memory
            
            # Estimate memory per sample (conservative estimate)
            estimated_memory_per_sample = 1024 * 1024 * 50  # 50MB per sample
            
            # Calculate safe batch size
            safe_batch_size = max(1, int(free_memory * 0.7 / estimated_memory_per_sample))
            
            # Use the smaller of safe batch size, default batch size, or dataset size
            optimal_batch_size = min(safe_batch_size, self.parameters["batch_size"], dataset_size)
            
            print(f"🔍 GPU Memory: {free_memory / 1024**3:.2f}GB free")
            print(f"📊 Optimal batch size: {optimal_batch_size}")
            
            return optimal_batch_size
            
        except Exception as e:
            print(f"⚠️ Could not determine optimal batch size: {e}")
            # Fallback to conservative batch size
            return min(16, self.parameters["batch_size"], dataset_size)
    
    def _clear_gpu_memory(self):
        """Clear GPU memory and garbage collect."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        gc.collect()

    def train_model(self, data_list: List[np.ndarray], labels: List[float], save_model: bool = True) -> Dict[str, Any]:
        """
        Train the enhanced LSTM model.

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
        input_size = data_list[0].shape[-1] if data_list[0].ndim > 1 else 1
        print(f"Training Enhanced LSTM with input size: {input_size}")

        # Create model
        self.model = self._create_model(input_size=input_size)
        self.optimizer = optim.Adam(
            self.model.parameters(), 
            lr=self.parameters["learning_rate"]
        )
        # Enhanced loss function combining MSE and MAE for better training
        self.criterion = nn.MSELoss()
        self.mae_criterion = nn.L1Loss()

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
                
                # Enhanced loss combining MSE and MAE for better training stability
                mse_loss = self.criterion(outputs, batch_y)
                mae_loss = self.mae_criterion(outputs, batch_y)
                loss = mse_loss + 0.1 * mae_loss  # Weighted combination
                
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
                
                # Memory management: clear intermediate tensors
                del outputs, loss
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

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
                    
                    # Memory management: clear intermediate tensors
                    del outputs, loss
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

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
            
            # Memory cleanup between epochs
            self._clear_gpu_memory()

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
        
        model_path = os.path.join(save_path, "enhanced_lstm_model.pth")
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history,
            'parameters': self.parameters,
            'input_size': self.model.input_size,
        }, model_path)
        
        print(f"Model saved to: {model_path}")

    def _load_model(self, model_path: str):
        """Load a trained model."""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Create model with saved input size
        input_size = checkpoint['input_size']
        self.model = self._create_model(input_size=input_size)
        
        # Load model state
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        # Load training history
        self.training_history = checkpoint.get('training_history', {})
        
        print(f"Model loaded from: {model_path}")

    def _try_load_pretrained_model(self) -> bool:
        """
        Try to load a pretrained PyTorch model for enhanced LSTM.
        
        Returns
        -------
        bool
            True if pretrained model was loaded successfully, False otherwise
        """
        try:
            # Check multiple possible paths for the pretrained model
            possible_paths = [
                os.path.join(self.parameters["model_save_path"], "enhanced_lstm_model.pth"),
                "models/enhanced_lstm/enhanced_lstm_model.pth",
                "../models/enhanced_lstm/enhanced_lstm_model.pth",
                "../../models/enhanced_lstm/enhanced_lstm_model.pth",
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "enhanced_lstm", "enhanced_lstm_model.pth"),
            ]
            
            # Try to import streamlit for logging, fallback to print if not available
            try:
                import streamlit as st
                st.write(f"🔍 Checking paths for LSTM model...")
                for i, model_path in enumerate(possible_paths):
                    exists = os.path.exists(model_path)
                    st.write(f"  Path {i+1}: {model_path} - {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
                    if exists:
                        try:
                            # Load trained model
                            self._load_model(model_path)
                            st.write(f"✅ Successfully loaded pretrained PyTorch model: {model_path}")
                            return True
                        except Exception as load_error:
                            st.write(f"⚠️ Failed to load model from {model_path}: {load_error}")
                            continue
                
                st.write(f"🔍 No PyTorch models found, will create untrained PyTorch model")
                # Don't fall back to scikit-learn - we want to use PyTorch models
                return False
            except ImportError:
                # Fallback to print if streamlit not available
                print(f"🔍 Checking paths for LSTM model...")
                for i, model_path in enumerate(possible_paths):
                    exists = os.path.exists(model_path)
                    print(f"  Path {i+1}: {model_path} - {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
                    if exists:
                        try:
                            # Load trained model
                            self._load_model(model_path)
                            print(f"✅ Successfully loaded pretrained PyTorch model: {model_path}")
                            return True
                        except Exception as load_error:
                            print(f"⚠️ Failed to load model from {model_path}: {load_error}")
                            continue
                
                print(f"🔍 No PyTorch models found, will create untrained PyTorch model")
                # Don't fall back to scikit-learn - we want to use PyTorch models
                return False
            
        except Exception as e:
            try:
                import streamlit as st
                st.write(f"⚠️ Could not load pretrained model for {self.__class__.__name__}: {e}")
            except ImportError:
                print(f"⚠️ Could not load pretrained model for {self.__class__.__name__}: {e}")
            return False

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using enhanced LSTM.

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
            raise ImportError("PyTorch is required for Enhanced LSTM estimator")

        # Try to load pretrained model first
        try:
            import streamlit as st
            st.write(f"🔍 LSTM: Attempting to load pretrained model...")
        except ImportError:
            pass
            
        if self._try_load_pretrained_model():
            try:
                import streamlit as st
                st.write(f"✅ LSTM: Pretrained model loaded successfully!")
            except ImportError:
                pass
                
            # Check if we loaded a PyTorch model or scikit-learn model
            if hasattr(self.model, 'forward') and callable(getattr(self.model, 'forward', None)):
                # We have a PyTorch model
                try:
                    import streamlit as st
                    st.write(f"🤖 LSTM: Using PyTorch neural network model")
                except ImportError:
                    pass
                    
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
                
                method = "Enhanced LSTM (Trained Neural Network)"
            else:
                # We have a scikit-learn model
                try:
                    import streamlit as st
                    st.write(f"📊 LSTM: Using scikit-learn ML model")
                except ImportError:
                    pass
                    
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
                
                method = "Enhanced LSTM (Pretrained ML)"
        else:
            # Create and use untrained model (fallback)
            try:
                import streamlit as st
                st.write(f"⚠️ LSTM: No pretrained model found, using untrained neural network")
            except ImportError:
                pass
                
            data_tensor = self._prepare_data(data)
            
            # Create fresh model
            input_size = data_tensor.shape[-1]
            self.model = self._create_model(input_size=input_size)
            
            # Make prediction
            with torch.no_grad():
                output = self.model(data_tensor)
                estimated_hurst = output.item()
                estimated_hurst = max(0.0, min(1.0, estimated_hurst))
            
            confidence_interval = (
                max(0, estimated_hurst - 0.1),
                min(1, estimated_hurst + 0.1),
            )
            
            method = "Enhanced LSTM (Untrained Neural Network)"

        # Store results
        self.results = {
            "hurst_parameter": estimated_hurst,
            "confidence_interval": confidence_interval,
            "std_error": 0.1,  # Simplified
            "method": method,
            "model_info": {
                "model_type": "EnhancedLSTM",
                "hidden_size": self.parameters["hidden_size"],
                "num_layers": self.parameters["num_layers"],
                "dropout_rate": self.parameters["dropout_rate"],
                "bidirectional": self.parameters["bidirectional"],
                "use_attention": self.parameters["use_attention"],
                "attention_heads": self.parameters["attention_heads"],
            },
        }

        return self.results

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the enhanced LSTM model.

        Returns
        -------
        dict
            Model information
        """
        info = {
            "model_type": "EnhancedLSTM",
            "architecture": "Enhanced LSTM with Attention and Bidirectional Layers",
            "hidden_size": self.parameters["hidden_size"],
            "num_layers": self.parameters["num_layers"],
            "dropout_rate": self.parameters["dropout_rate"],
            "bidirectional": self.parameters["bidirectional"],
            "use_attention": self.parameters["use_attention"],
            "attention_heads": self.parameters["attention_heads"],
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
