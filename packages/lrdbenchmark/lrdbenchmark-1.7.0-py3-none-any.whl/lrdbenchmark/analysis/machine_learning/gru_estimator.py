"""
GRU Estimator for Long-Range Dependence Analysis

This module provides a PyTorch GRU-based estimator for Hurst parameter estimation.
It integrates with the BaseMLEstimator interface but overrides training and
estimation to support sequence models (train once, apply many).
"""

from typing import Any, Dict, Tuple, Optional
import numpy as np
from .base_ml_estimator import BaseMLEstimator
from sklearn.preprocessing import StandardScaler

try:
    import torch
    from torch import nn
    from torch.utils.data import Dataset, DataLoader

    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:

    class _SequenceDataset(Dataset):
        def __init__(self, X: np.ndarray, y: np.ndarray):
            self.X = torch.from_numpy(X.astype(np.float32))
            self.y = torch.from_numpy(y.astype(np.float32)).view(-1, 1)

        def __len__(self) -> int:
            return self.X.shape[0]

        def __getitem__(self, idx: int):
            return self.X[idx], self.y[idx]


if TORCH_AVAILABLE:

    class _GRURegressor(nn.Module):
        def __init__(
            self,
            input_size: int,
            hidden_size: int,
            num_layers: int,
            dropout: float = 0.0,
            bidirectional: bool = False,
        ):
            super().__init__()
            self.gru = nn.GRU(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                dropout=dropout if num_layers > 1 else 0.0,
                batch_first=True,
                bidirectional=bidirectional,
            )
            direction_multiplier = 2 if bidirectional else 1
            self.head = nn.Sequential(
                nn.Linear(hidden_size * direction_multiplier, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, 1),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out, hn = self.gru(x)
            last = out[:, -1, :]
            return self.head(last)


# Close the TORCH_AVAILABLE if statement


class GRUEstimator(BaseMLEstimator):
    """GRU estimator for Hurst parameter estimation using PyTorch."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch is required for GRUEstimator. Install with: pip install torch"
            )
        self.hidden_size = self.parameters.get("hidden_size", 64)
        self.num_layers = self.parameters.get("num_layers", 2)
        self.dropout = self.parameters.get("dropout", 0.1)
        self.bidirectional = self.parameters.get("bidirectional", False)
        self.learning_rate = self.parameters.get("learning_rate", 1e-3)
        self.epochs = self.parameters.get("epochs", 30)
        self.batch_size = self.parameters.get("batch_size", 32)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._torch_model: Optional[nn.Module] = None
        
        # Initialize scaler if not already set
        if not hasattr(self, 'scaler') or self.scaler is None:
            self.scaler = StandardScaler()

    def _validate_parameters(self) -> None:
        if self.parameters.get("feature_extraction_method") not in (
            None,
            "raw",
            "statistical",
            "spectral",
            "wavelet",
        ):
            raise ValueError("Invalid feature_extraction_method")

    def _create_model(self) -> Any:
        return None

    def _prepare_sequences(self, X: np.ndarray, fit_scaler: bool) -> np.ndarray:
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Handle different sequence lengths by resizing to a standard length
        target_length = 500  # Standard length for pretrained models
        
        if X.shape[1] != target_length:
            # Resize sequences to target length
            resized_X = []
            for seq in X:
                if len(seq) > target_length:
                    # Truncate if too long
                    resized_seq = seq[:target_length]
                else:
                    # Pad with zeros if too short
                    resized_seq = np.pad(seq, (0, target_length - len(seq)), 'constant')
                resized_X.append(resized_seq)
            X = np.array(resized_X)
        
        if fit_scaler:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        return X_scaled.reshape(X_scaled.shape[0], X_scaled.shape[1], 1)

    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch is required for GRUEstimator. Install with: pip install torch"
            )
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        import time as _time

        X_seq = self._prepare_sequences(X, fit_scaler=True)
        X_train, X_val, y_train, y_val = train_test_split(
            X_seq, y, test_size=self.test_size, random_state=self.random_state
        )

        train_ds = _SequenceDataset(X_train, y_train)
        val_ds = _SequenceDataset(X_val, y_val)
        train_loader = DataLoader(train_ds, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=self.batch_size, shuffle=False)

        model = _GRURegressor(
            input_size=1,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        ).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
        criterion = nn.MSELoss()

        model.train()
        for epoch in range(self.epochs):
            for xb, yb in train_loader:
                xb = xb.to(self.device)
                yb = yb.to(self.device)
                optimizer.zero_grad()
                preds = model(xb)
                loss = criterion(preds, yb)
                loss.backward()
                optimizer.step()

        model.eval()

        def _predict(loader):
            outs, gts = [], []
            with torch.no_grad():
                for xb, yb in loader:
                    xb = xb.to(self.device)
                    preds = model(xb).cpu().numpy().reshape(-1)
                    outs.append(preds)
                    gts.append(yb.numpy().reshape(-1))
            return np.concatenate(outs), np.concatenate(gts)

        train_pred, train_gt = _predict(train_loader)
        val_pred, val_gt = _predict(val_loader)

        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

        train_mse = mean_squared_error(train_gt, train_pred)
        test_mse = mean_squared_error(val_gt, val_pred)
        train_mae = mean_absolute_error(train_gt, train_pred)
        test_mae = mean_absolute_error(val_gt, val_pred)
        train_r2 = r2_score(train_gt, train_pred)
        test_r2 = r2_score(val_gt, val_pred)

        self._torch_model = model
        self.model = model
        self.results = {
            "train_mse": train_mse,
            "test_mse": test_mse,
            "train_mae": train_mae,
            "test_mae": test_mae,
            "train_r2": train_r2,
            "test_r2": test_r2,
            "n_features": X_seq.shape[1],
            "n_samples": X_seq.shape[0],
        }
        self.is_trained = True
        return self.results

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        if not self.is_trained or self._torch_model is None:
            # Try to load pretrained model automatically
            if self._try_load_pretrained_model():
                print(f"✅ Loaded pretrained model for {self.__class__.__name__}")
            else:
                # Create heuristic model as fallback
                if self._create_heuristic_model():
                    print(f"✅ Created heuristic model for {self.__class__.__name__}")
                else:
                    raise RuntimeError(
                        f"Model must be trained before estimation. "
                        f"Use train() method or ensure pretrained model is available for {self.__class__.__name__}"
                    )

        # Check if we have a torch model (pretrained GRU) or sklearn model (heuristic)
        if hasattr(self, '_torch_model') and self._torch_model is not None:
            # Use GRU model
            try:
                # Prepare single sequence using fitted scaler
                if data.ndim == 1:
                    X_seq = self._prepare_sequences(data.reshape(1, -1), fit_scaler=False)
                else:
                    X_seq = self._prepare_sequences(data, fit_scaler=False)

                x = torch.from_numpy(X_seq.astype(np.float32)).to(self.device)
                self._torch_model.eval()
                with torch.no_grad():
                    pred = self._torch_model(x).cpu().numpy().reshape(-1)
                hurst_estimate = float(pred[0])
                
                # Calculate confidence interval
                confidence_interval = self._calculate_confidence_interval(hurst_estimate)

                self.results.update(
                    {
                        "hurst_parameter": hurst_estimate,
                        "confidence_interval": confidence_interval,
                        "method": f"{self.__class__.__name__} (GRU)",
                        "model_info": {
                            "model_type": "GRU",
                            "is_pretrained": True,
                            "hidden_size": self.hidden_size,
                            "num_layers": self.num_layers,
                            "bidirectional": self.bidirectional,
                        },
                    }
                )
            except Exception as e:
                print(f"⚠️ GRU estimation failed, falling back to heuristic: {str(e)}")
                # Fallback to heuristic model
                return self._estimate_with_heuristic(data)
        else:
            # Use heuristic model (sklearn-based)
            return self._estimate_with_heuristic(data)

        return self.results

    def _estimate_with_heuristic(self, data: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation using heuristic model."""
        # Extract features if raw time series data is provided
        if data.ndim == 1 or (data.ndim == 2 and data.shape[1] > 100):
            features = self.extract_features(data)
        else:
            features = data

        # Scale features
        features_scaled = self.scaler.transform(features)

        # Make prediction
        hurst_estimate = self.model.predict(features_scaled)

        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(hurst_estimate[0])

        # Store results
        self.results = {
            "hurst_parameter": float(hurst_estimate[0]),
            "confidence_interval": confidence_interval,
            "r_squared": self.results.get("test_r2", None),
            "p_value": None,  # ML models don't provide p-values
            "method": f"{self.__class__.__name__} (Heuristic)",
            "model_info": {
                "model_type": type(self.model).__name__,
                "is_pretrained": False,
                "feature_extraction": self.feature_extraction_method,
            },
        }

        return self.results

    def save_model(self, filepath: str) -> None:
        if not self.is_trained or self._torch_model is None:
            raise ValueError("Model must be trained before saving")
        import joblib, torch

        meta = {
            "scaler": self.scaler,
            "parameters": self.parameters,
            "results": self.results,
            "model_meta": {
                "hidden_size": self.hidden_size,
                "num_layers": self.num_layers,
                "dropout": self.dropout,
                "bidirectional": self.bidirectional,
            },
        }
        joblib.dump(meta, filepath)
        torch.save(self._torch_model.state_dict(), filepath + ".pt")

    def load_model(self, filepath: str) -> None:
        import os, joblib, torch

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        meta = joblib.load(filepath)
        self.scaler = meta["scaler"]
        self.parameters = meta["parameters"]
        self.results = meta["results"]
        self.hidden_size = meta["model_meta"]["hidden_size"]
        self.num_layers = meta["model_meta"]["num_layers"]
        self.dropout = meta["model_meta"]["dropout"]
        self.bidirectional = meta["model_meta"]["bidirectional"]
        self._torch_model = _GRURegressor(
            input_size=1,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        )
        state_path = filepath + ".pt"
        if not os.path.exists(state_path):
            raise FileNotFoundError(f"Model weights not found: {state_path}")
        self._torch_model.load_state_dict(torch.load(state_path, map_location="cpu"))
        self.model = self._torch_model
        self.is_trained = True
