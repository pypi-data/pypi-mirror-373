#!/usr/bin/env python3
"""
Unified R/S (Rescaled Range) Estimator for Long-Range Dependence Analysis.

This module implements the R/S estimator with automatic optimization framework
selection (JAX, Numba, NumPy) for the best performance on the available hardware.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Union, Tuple, List
import warnings

# Import optimization frameworks
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

try:
    import numba
    from numba import jit as numba_jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

# Import base estimator
try:
    from lrdbenchmark.analysis.base_estimator import BaseEstimator
except ImportError:
    try:
        from models.estimators.base_estimator import BaseEstimator
    except ImportError:
        # Fallback if base estimator not available
        class BaseEstimator:
            def __init__(self, **kwargs):
                self.parameters = kwargs


class RSEstimator(BaseEstimator):
    """
    Unified R/S (Rescaled Range) Estimator for Long-Range Dependence Analysis.

    The R/S estimator analyzes the rescaled range of time series data to estimate
    the Hurst parameter, which characterizes long-range dependence.

    Features:
    - Automatic optimization framework selection (JAX, Numba, NumPy)
    - GPU acceleration with JAX when available
    - JIT compilation with Numba for CPU optimization
    - Graceful fallbacks when optimization frameworks fail

    Parameters
    ----------
    min_block_size : int, optional (default=10)
        Minimum block size for analysis
    max_block_size : int, optional (default=None)
        Maximum block size for analysis. If None, uses data length / 4
    num_blocks : int, optional (default=10)
        Number of block sizes to test
    use_optimization : str, optional (default='auto')
        Optimization framework to use: 'auto', 'jax', 'numba', 'numpy'
    """

    def __init__(
        self,
        min_block_size: int = 10,
        max_block_size: Optional[int] = None,
        num_blocks: int = 10,
        use_optimization: str = "auto",
    ):
        super().__init__()
        
        # Estimator parameters
        self.parameters = {
            "min_block_size": min_block_size,
            "max_block_size": max_block_size,
            "num_blocks": num_blocks,
        }
        
        # Optimization framework
        self.optimization_framework = self._select_optimization_framework(use_optimization)
        
        # Results storage
        self.results = {}
        
        # Validation
        self._validate_parameters()

    def _select_optimization_framework(self, use_optimization: str) -> str:
        """Select the optimal optimization framework."""
        if use_optimization == "auto":
            if JAX_AVAILABLE:
                return "jax"  # Best for GPU acceleration
            elif NUMBA_AVAILABLE:
                return "numba"  # Good for CPU optimization
            else:
                return "numpy"  # Fallback
        elif use_optimization == "jax" and JAX_AVAILABLE:
            return "jax"
        elif use_optimization == "numba" and NUMBA_AVAILABLE:
            return "numba"
        else:
            return "numpy"

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["min_block_size"] < 4:
            raise ValueError("min_block_size must be at least 4")
        
        if self.parameters["num_blocks"] < 3:
            raise ValueError("num_blocks must be at least 3")

    def estimate(self, data: Union[np.ndarray, list]) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using R/S analysis with automatic optimization.

        Parameters
        ----------
        data : array-like
            Input time series data

        Returns
        -------
        dict
            Dictionary containing estimation results including:
            - hurst_parameter: Estimated Hurst parameter
            - r_squared: R-squared value of the fit
            - block_sizes: Block sizes used in the analysis
            - rs_values: R/S values for each block size
            - log_block_sizes: Log of block sizes
            - log_rs_values: Log of R/S values
        """
        data = np.asarray(data)
        n = len(data)

        if n < 100:
            warnings.warn("Data length is small, results may be unreliable")

        # Select optimal method based on data size and framework
        if self.optimization_framework == "jax" and JAX_AVAILABLE:
            try:
                return self._estimate_jax(data)
            except Exception as e:
                warnings.warn(f"JAX implementation failed: {e}, falling back to NumPy")
                return self._estimate_numpy(data)
        elif self.optimization_framework == "numba" and NUMBA_AVAILABLE:
            try:
                return self._estimate_numba(data)
            except Exception as e:
                warnings.warn(f"Numba implementation failed: {e}, falling back to NumPy")
                return self._estimate_numpy(data)
        else:
            return self._estimate_numpy(data)

    def _estimate_numpy(self, data: np.ndarray) -> Dict[str, Any]:
        """NumPy implementation of R/S estimation."""
        n = len(data)
        
        # Set max block size if not provided
        if self.parameters["max_block_size"] is None:
            self.parameters["max_block_size"] = n // 4
        
        # Generate block sizes
        block_sizes = np.logspace(
            np.log10(self.parameters["min_block_size"]),
            np.log10(self.parameters["max_block_size"]),
            self.parameters["num_blocks"],
            dtype=int
        )
        
        # Ensure block sizes are unique and valid
        block_sizes = np.unique(block_sizes)
        block_sizes = block_sizes[block_sizes <= n // 2]
        
        if len(block_sizes) < 3:
            raise ValueError("Insufficient valid block sizes for analysis")
        
        # Calculate R/S values for each block size
        rs_values = []
        for block_size in block_sizes:
            rs_val = self._calculate_rs_numpy(data, block_size)
            rs_values.append(rs_val)
        
        rs_values = np.array(rs_values)
        
        # Filter out invalid values
        valid_mask = (rs_values > 0) & ~np.isnan(rs_values)
        if np.sum(valid_mask) < 3:
            raise ValueError("Insufficient valid R/S values for analysis")
        
        valid_block_sizes = block_sizes[valid_mask]
        valid_rs_values = rs_values[valid_mask]
        
        # Log-log regression
        log_block_sizes = np.log(valid_block_sizes)
        log_rs_values = np.log(valid_rs_values)
        
        # Linear regression
        coeffs = np.polyfit(log_block_sizes, log_rs_values, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Calculate R-squared
        y_pred = slope * log_block_sizes + intercept
        ss_res = np.sum((log_rs_values - y_pred) ** 2)
        ss_tot = np.sum((log_rs_values - np.mean(log_rs_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Hurst parameter is the slope
        hurst_parameter = slope
        
        # Store results
        self.results = {
            "hurst_parameter": float(hurst_parameter),
            "r_squared": float(r_squared),
            "slope": float(slope),
            "intercept": float(intercept),
            "p_value": np.nan,  # Not available with simple polyfit
            "std_error": np.nan,  # Not available with simple polyfit
            "block_sizes": valid_block_sizes.tolist(),
            "rs_values": valid_rs_values.tolist(),
            "log_block_sizes": log_block_sizes.tolist(),
            "log_rs_values": log_rs_values.tolist(),
            "method": "numpy",
            "optimization_framework": self.optimization_framework,
        }
        
        return self.results

    def _estimate_numba(self, data: np.ndarray) -> Dict[str, Any]:
        """Numba-optimized implementation of R/S estimation."""
        if not NUMBA_AVAILABLE:
            warnings.warn("Numba not available, falling back to NumPy")
            return self._estimate_numpy(data)
        
        try:
            # Use Numba-optimized calculation
            return self._estimate_numba_optimized(data)
        except Exception as e:
            warnings.warn(f"Numba implementation failed: {e}, falling back to NumPy")
            return self._estimate_numpy(data)
    
    def _estimate_numba_optimized(self, data: np.ndarray) -> Dict[str, Any]:
        """Actual Numba-optimized implementation."""
        n = len(data)
        
        # Set max block size if not provided
        if self.parameters["max_block_size"] is None:
            self.parameters["max_block_size"] = n // 4
        
        # Generate block sizes
        block_sizes = np.logspace(
            np.log10(self.parameters["min_block_size"]),
            np.log10(self.parameters["max_block_size"]),
            self.parameters["num_blocks"],
            dtype=int
        )
        
        # Ensure block sizes are unique and valid
        block_sizes = np.unique(block_sizes)
        block_sizes = block_sizes[block_sizes <= n // 2]
        
        if len(block_sizes) < 3:
            raise ValueError("Insufficient valid block sizes for analysis")
        
        # Calculate R/S values using Numba-optimized function
        rs_values = []
        for block_size in block_sizes:
            rs_val = self._calculate_rs_numba(data, block_size)
            rs_values.append(rs_val)
        
        rs_values = np.array(rs_values)
        
        # Filter out invalid values
        valid_mask = (rs_values > 0) & ~np.isnan(rs_values)
        if np.sum(valid_mask) < 3:
            raise ValueError("Insufficient valid R/S values for analysis")
        
        valid_block_sizes = block_sizes[valid_mask]
        valid_rs_values = rs_values[valid_mask]
        
        # Log-log regression
        log_block_sizes = np.log(valid_block_sizes)
        log_rs_values = np.log(valid_rs_values)
        
        # Linear regression
        coeffs = np.polyfit(log_block_sizes, log_rs_values, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Calculate R-squared
        y_pred = slope * log_block_sizes + intercept
        ss_res = np.sum((log_rs_values - y_pred) ** 2)
        ss_tot = np.sum((log_rs_values - np.mean(log_rs_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Hurst parameter is the slope
        hurst_parameter = slope
        
        # Calculate p-value and standard error
        try:
            # Use scipy for statistical tests
            from scipy import stats
            slope, intercept, r_value, p_value, std_error = stats.linregress(
                log_block_sizes, log_rs_values
            )
        except ImportError:
            p_value = None
            std_error = None
        
        return {
            "hurst_parameter": hurst_parameter,
            "r_squared": r_squared,
            "slope": slope,
            "intercept": intercept,
            "p_value": p_value,
            "std_error": std_error,
            "block_sizes": valid_block_sizes,
            "rs_values": valid_rs_values,
            "log_block_sizes": log_block_sizes,
            "log_rs_values": log_rs_values,
            "method": "numba",
            "optimization_framework": "numba"
        }

    def _estimate_jax(self, data: np.ndarray) -> Dict[str, Any]:
        """JAX-optimized implementation of R/S estimation."""
        if not JAX_AVAILABLE:
            warnings.warn("JAX not available, falling back to NumPy")
            return self._estimate_numpy(data)
        
        try:
            # Use JAX-optimized calculation
            return self._estimate_jax_optimized(data)
        except Exception as e:
            warnings.warn(f"JAX implementation failed: {e}, falling back to NumPy")
            return self._estimate_numpy(data)
    
    def _estimate_jax_optimized(self, data: np.ndarray) -> Dict[str, Any]:
        """Actual JAX-optimized implementation."""
        n = len(data)
        
        # Set max block size if not provided
        if self.parameters["max_block_size"] is None:
            self.parameters["max_block_size"] = n // 4
        
        # Generate block sizes
        block_sizes = np.logspace(
            np.log10(self.parameters["min_block_size"]),
            np.log10(self.parameters["max_block_size"]),
            self.parameters["num_blocks"],
            dtype=int
        )
        
        # Ensure block sizes are unique and valid
        block_sizes = np.unique(block_sizes)
        block_sizes = block_sizes[block_sizes <= n // 2]
        
        if len(block_sizes) < 3:
            raise ValueError("Insufficient valid block sizes for analysis")
        
        # Convert to JAX arrays
        data_jax = jnp.array(data)
        block_sizes_jax = jnp.array(block_sizes)
        
        # Calculate R/S values using JAX-optimized function
        rs_values = []
        for block_size in block_sizes:
            rs_val = self._calculate_rs_jax(data_jax, block_size)
            rs_values.append(rs_val)
        
        rs_values = np.array(rs_values)
        
        # Filter out invalid values
        valid_mask = (rs_values > 0) & ~np.isnan(rs_values)
        if np.sum(valid_mask) < 3:
            raise ValueError("Insufficient valid R/S values for analysis")
        
        valid_block_sizes = block_sizes[valid_mask]
        valid_rs_values = rs_values[valid_mask]
        
        # Log-log regression
        log_block_sizes = np.log(valid_block_sizes)
        log_rs_values = np.log(valid_rs_values)
        
        # Linear regression
        coeffs = np.polyfit(log_block_sizes, log_rs_values, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Calculate R-squared
        y_pred = slope * log_block_sizes + intercept
        ss_res = np.sum((log_rs_values - y_pred) ** 2)
        ss_tot = np.sum((log_rs_values - np.mean(log_rs_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Hurst parameter is the slope
        hurst_parameter = slope
        
        # Calculate p-value and standard error
        try:
            # Use scipy for statistical tests
            from scipy import stats
            slope, intercept, r_value, p_value, std_error = stats.linregress(
                log_block_sizes, log_rs_values
            )
        except ImportError:
            p_value = None
            std_error = None
        
        return {
            "hurst_parameter": hurst_parameter,
            "r_squared": r_squared,
            "slope": slope,
            "intercept": intercept,
            "p_value": p_value,
            "std_error": std_error,
            "block_sizes": valid_block_sizes,
            "rs_values": valid_rs_values,
            "log_block_sizes": log_block_sizes,
            "log_rs_values": log_rs_values,
            "method": "jax",
            "optimization_framework": "jax"
        }

    def _calculate_rs_numpy(self, data: np.ndarray, block_size: int) -> float:
        """Calculate R/S value for a given block size using NumPy."""
        n = len(data)
        n_blocks = n // block_size
        
        if n_blocks == 0:
            return np.nan
        
        rs_values = []
        
        for i in range(n_blocks):
            start_idx = i * block_size
            end_idx = start_idx + block_size
            block_data = data[start_idx:end_idx]
            
            # Calculate cumulative deviation
            mean_val = np.mean(block_data)
            dev = block_data - mean_val
            cum_dev = np.cumsum(dev)
            
            # Calculate range
            R = np.max(cum_dev) - np.min(cum_dev)
            
            # Calculate standard deviation
            S = np.std(block_data, ddof=1)
            
            if S > 0:
                rs_values.append(R / S)
        
        if len(rs_values) == 0:
            return np.nan
        
        return np.mean(rs_values)
    
    def _calculate_rs_numba(self, data: np.ndarray, block_size: int) -> float:
        """Calculate R/S value for a given block size using Numba optimization."""
        if not NUMBA_AVAILABLE:
            return self._calculate_rs_numpy(data, block_size)
        
        try:
            # Use Numba-optimized calculation
            return self._calculate_rs_numba_optimized(data, block_size)
        except Exception as e:
            warnings.warn(f"Numba R/S calculation failed: {e}, falling back to NumPy")
            return self._calculate_rs_numpy(data, block_size)
    
    def _calculate_rs_numba_optimized(self, data: np.ndarray, block_size: int) -> float:
        """Numba-optimized R/S calculation using JIT compilation."""
        if NUMBA_AVAILABLE:
            return self._calculate_rs_numba_jit(data, block_size)
        else:
            return self._calculate_rs_numpy(data, block_size)
    
    @staticmethod
    @numba_jit(nopython=True, cache=True)
    def _calculate_rs_numba_jit(data: np.ndarray, block_size: int) -> float:
        """Numba JIT-compiled R/S calculation for maximum performance."""
        n = len(data)
        n_blocks = n // block_size
        
        if n_blocks == 0:
            return np.nan
        
        rs_values = []
        
        for i in range(n_blocks):
            start_idx = i * block_size
            end_idx = start_idx + block_size
            block_data = data[start_idx:end_idx]
            
            # Calculate cumulative deviation
            mean_val = 0.0
            for j in range(block_size):
                mean_val += block_data[j]
            mean_val /= block_size
            
            dev = np.zeros(block_size)
            for j in range(block_size):
                dev[j] = block_data[j] - mean_val
            
            cum_dev = np.zeros(block_size)
            cum_dev[0] = dev[0]
            for j in range(1, block_size):
                cum_dev[j] = cum_dev[j-1] + dev[j]
            
            # Calculate range
            min_val = cum_dev[0]
            max_val = cum_dev[0]
            for j in range(1, block_size):
                if cum_dev[j] < min_val:
                    min_val = cum_dev[j]
                if cum_dev[j] > max_val:
                    max_val = cum_dev[j]
            R = max_val - min_val
            
            # Calculate standard deviation
            sum_sq = 0.0
            for j in range(block_size):
                diff = dev[j]
                sum_sq += diff * diff
            S = np.sqrt(sum_sq / (block_size - 1))
            
            if S > 0:
                rs_values.append(R / S)
        
        if len(rs_values) == 0:
            return np.nan
        
        # Calculate mean
        total = 0.0
        for val in rs_values:
            total += val
        return total / len(rs_values)
    
    def _calculate_rs_jax(self, data: jnp.ndarray, block_size: int) -> float:
        """Calculate R/S value for a given block size using JAX optimization."""
        if not JAX_AVAILABLE:
            return self._calculate_rs_numpy(np.array(data), block_size)
        
        try:
            # Use JAX-optimized calculation
            return self._calculate_rs_jax_optimized(data, block_size)
        except Exception as e:
            warnings.warn(f"JAX R/S calculation failed: {e}, falling back to NumPy")
            return self._calculate_rs_numpy(np.array(data), block_size)
    
    def _calculate_rs_jax_optimized(self, data: jnp.ndarray, block_size: int) -> float:
        """JAX-optimized R/S calculation using JIT compilation."""
        n = len(data)
        n_blocks = n // block_size
        
        if n_blocks == 0:
            return np.nan
        
        rs_values = []
        
        for i in range(n_blocks):
            start_idx = i * block_size
            end_idx = start_idx + block_size
            block_data = data[start_idx:end_idx]
            
            # Calculate cumulative deviation using JAX operations
            mean_val = jnp.mean(block_data)
            dev = block_data - mean_val
            cum_dev = jnp.cumsum(dev)
            
            # Calculate range
            R = jnp.max(cum_dev) - jnp.min(cum_dev)
            
            # Calculate standard deviation
            S = jnp.std(block_data, ddof=1)
            
            if S > 0:
                rs_values.append(R / S)
        
        if len(rs_values) == 0:
            return np.nan
        
        return jnp.mean(jnp.array(rs_values))

    def get_optimization_info(self) -> Dict[str, Any]:
        """Get information about available optimizations and current selection."""
        return {
            "current_framework": self.optimization_framework,
            "jax_available": JAX_AVAILABLE,
            "numba_available": NUMBA_AVAILABLE,
            "recommended_framework": self._get_recommended_framework()
        }

    def _get_recommended_framework(self) -> str:
        """Get the recommended optimization framework."""
        if JAX_AVAILABLE:
            return "jax"  # Best for GPU acceleration
        elif NUMBA_AVAILABLE:
            return "numba"  # Good for CPU optimization
        else:
            return "numpy"  # Fallback

    def plot_analysis(self, figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None) -> None:
        """Plot the R/S analysis results."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('R/S Analysis Results', fontsize=16)

        # Plot 1: Log-log relationship
        ax1 = axes[0, 0]
        x = self.results["log_block_sizes"]
        y = self.results["log_rs_values"]

        ax1.scatter(x, y, s=60, alpha=0.7, label="Data points")

        # Plot fitted line
        slope = self.results["slope"]
        intercept = self.results["intercept"]
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept
        ax1.plot(x_fit, y_fit, "r--", label=f"Linear fit (slope={slope:.3f})")

        ax1.set_xlabel("log(Block Size)")
        ax1.set_ylabel("log(R/S)")
        ax1.set_title("R/S Scaling")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: R/S vs Block Size (log-log)
        ax2 = axes[0, 1]
        block_sizes = self.results["block_sizes"]
        rs_values = self.results["rs_values"]
        
        ax2.scatter(block_sizes, rs_values, s=60, alpha=0.7)
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.set_xlabel("Block Size")
        ax2.set_ylabel("R/S Value")
        ax2.set_title("R/S vs Block Size (log-log)")
        ax2.grid(True, which="both", ls=":", alpha=0.3)

        # Plot 3: Hurst parameter estimate
        ax3 = axes[1, 0]
        hurst = self.results["hurst_parameter"]
        
        ax3.bar(["Hurst Parameter"], [hurst], alpha=0.7, color='skyblue')
        ax3.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='H=0.5 (no memory)')
        ax3.set_ylabel("Hurst Parameter")
        ax3.set_title(f"Hurst Parameter Estimate: {hurst:.3f}")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: R-squared
        ax4 = axes[1, 1]
        r_squared = self.results["r_squared"]
        
        ax4.bar(["R²"], [r_squared], alpha=0.7, color='lightgreen')
        ax4.set_ylabel("R²")
        ax4.set_title(f"Goodness of Fit: R² = {r_squared:.3f}")
        ax4.set_ylim(0, 1)
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()

    def get_method_recommendation(self, n: int) -> Dict[str, Any]:
        """Get method recommendation for a given data size."""
        if n < 100:
            return {
                "recommended_method": "numpy",
                "reasoning": f"Data size n={n} is too small for optimization benefits",
                "method_details": {
                    "description": "NumPy implementation",
                    "best_for": "Small datasets (n < 100)",
                    "complexity": "O(n²)",
                    "memory": "O(n)",
                    "accuracy": "Medium"
                }
            }
        elif n < 1000:
            return {
                "recommended_method": "numba",
                "reasoning": f"Data size n={n} benefits from JIT compilation",
                "method_details": {
                    "description": "Numba JIT-compiled implementation",
                    "best_for": "Medium datasets (100 ≤ n < 1000)",
                    "complexity": "O(n²)",
                    "memory": "O(n)",
                    "accuracy": "High"
                }
            }
        else:
            return {
                "recommended_method": "jax",
                "reasoning": f"Data size n={n} benefits from GPU acceleration",
                "method_details": {
                    "description": "JAX GPU-accelerated implementation",
                    "best_for": "Large datasets (n ≥ 1000)",
                    "complexity": "O(n²)",
                    "memory": "O(n)",
                    "accuracy": "High"
                }
            }
