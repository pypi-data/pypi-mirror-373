"""
Unified Rescaled Range (R/S) Analysis estimator.

This module provides a single RSEstimator class that automatically selects
the optimal implementation (JAX, NUMBA, or NumPy) based on data size and
available optimization frameworks.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats
import warnings

# Try to import optimization libraries
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

try:
    from numba import jit as numba_jit
    from numba import prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

# Import base estimator
try:
    from models.estimators.base_estimator import BaseEstimator
except ImportError:
    # Fallback if base estimator not available
    class BaseEstimator:
        def __init__(self, **kwargs):
            self.parameters = kwargs


class RSEstimator(BaseEstimator):
    """
    Unified Rescaled Range (R/S) Analysis estimator.

    This class automatically selects the optimal implementation based on:
    - Data size and computational requirements
    - Available optimization frameworks (JAX, NUMBA)
    - Performance requirements

    The R/S method estimates the Hurst parameter by analyzing the scaling
    behavior of the rescaled range statistic across different time scales.

    Parameters
    ----------
    min_window_size : int, optional
        Minimum window size to use (default: 10)
    max_window_size : int, optional
        Maximum window size to use (default: None, uses n/4)
    window_sizes : List[int], optional
        Custom list of window sizes to use (default: None)
    overlap : bool, optional
        Whether to use overlapping windows (default: False)
    use_optimization : str, optional
        Optimization framework preference (default: 'auto')
        - 'auto': Choose best available
        - 'jax': GPU acceleration (when available)
        - 'numba': CPU optimization (when available)
        - 'numpy': Standard NumPy
    """

    def __init__(
        self,
        min_window_size: int = 10,
        max_window_size: Optional[int] = None,
        window_sizes: Optional[List[int]] = None,
        overlap: bool = False,
        use_optimization: str = "auto"
    ):
        """
        Initialize the R/S estimator.

        Parameters
        ----------
        min_window_size : int, optional
            Minimum window size to use (default: 10)
        max_window_size : int, optional
            Maximum window size to use (default: None, uses n/4)
        window_sizes : List[int], optional
            Custom list of window sizes to use (default: None)
        overlap : bool, optional
            Whether to use overlapping windows (default: False)
        use_optimization : str, optional
            Optimization framework preference (default: 'auto')
        """
        super().__init__(
            min_window_size=min_window_size,
            max_window_size=max_window_size,
            window_sizes=window_sizes,
            overlap=overlap,
            use_optimization=use_optimization
        )

        # Set optimization framework
        if use_optimization == "auto":
            if JAX_AVAILABLE:
                self.optimization_framework = "jax"
            elif NUMBA_AVAILABLE:
                self.optimization_framework = "numba"
            else:
                self.optimization_framework = "numpy"
        else:
            self.optimization_framework = use_optimization
            
        # Validate optimization framework availability
        if self.optimization_framework == "jax" and not JAX_AVAILABLE:
            warnings.warn("JAX requested but not available. Falling back to numpy.")
            self.optimization_framework = "numpy"
        elif self.optimization_framework == "numba" and not NUMBA_AVAILABLE:
            warnings.warn("Numba requested but not available. Falling back to numpy.")
            self.optimization_framework = "numpy"

        # Results storage
        self.scales = []
        self.rs_values = []
        self.estimated_hurst = None
        self.confidence_interval = None
        self.r_squared = None

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """
        Validate the estimator parameters.

        Raises:
            ValueError: If parameters are invalid
        """
        if self.parameters["window_sizes"] is not None:
            if len(self.parameters["window_sizes"]) < 3:
                raise ValueError("Need at least 3 window sizes")
            if any(w < 4 for w in self.parameters["window_sizes"]):
                raise ValueError("All window sizes must be at least 4")
            if not all(
                self.parameters["window_sizes"][i]
                < self.parameters["window_sizes"][i + 1]
                for i in range(len(self.parameters["window_sizes"]) - 1)
            ):
                raise ValueError("Window sizes must be in ascending order")
        else:
            if self.parameters["min_window_size"] < 4:
                raise ValueError("min_window_size must be at least 4")
            if (
                self.parameters["max_window_size"] is not None
                and self.parameters["max_window_size"]
                <= self.parameters["min_window_size"]
            ):
                raise ValueError("max_window_size must be greater than min_window_size")

    def _get_window_sizes(self, n: int) -> List[int]:
        """Get the list of window sizes to use for analysis."""
        if self.parameters["window_sizes"] is not None:
            return [w for w in self.parameters["window_sizes"] if w <= n]

        min_size = self.parameters["min_window_size"]
        max_size = self.parameters["max_window_size"] or n // 4

        # Generate window sizes with geometric spacing
        sizes = []
        current_size = min_size
        while current_size <= max_size and current_size <= n // 2:
            sizes.append(current_size)
            current_size = int(current_size * 1.5)

        return sizes

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using R/S analysis.

        Parameters
        ----------
        data : np.ndarray
            Time series data

        Returns
        -------
        dict
            Estimation results including Hurst parameter, confidence intervals, etc.
        """
        n = len(data)
        window_sizes = self._get_window_sizes(n)

        if len(window_sizes) < 3:
            raise ValueError(f"Need at least 3 valid window sizes. Got: {window_sizes}")

        # Choose implementation based on optimization framework
        if self.optimization_framework == "jax" and JAX_AVAILABLE:
            scales, rs_values = self._estimate_jax(data, window_sizes)
        elif self.optimization_framework == "numba" and NUMBA_AVAILABLE:
            scales, rs_values = self._estimate_numba(data, window_sizes)
        else:
            scales, rs_values = self._estimate_numpy(data, window_sizes)

        # Store results
        self.scales = scales
        self.rs_values = rs_values

        # Fit linear regression to log-log plot
        if len(scales) >= 2:
            log_scales = np.log10(scales)
            log_rs = np.log10(rs_values)

            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                log_scales, log_rs
            )

            self.estimated_hurst = slope
            self.r_squared = r_value ** 2

            # Confidence interval (95%)
            n_points = len(scales)
            t_value = stats.t.ppf(0.975, n_points - 2)
            self.confidence_interval = (
                slope - t_value * std_err,
                slope + t_value * std_err,
            )

            return {
                "hurst_parameter": self.estimated_hurst,
                "confidence_interval": self.confidence_interval,
                "r_squared": self.r_squared,
                "p_value": p_value,
                "scales": scales,
                "rs_values": rs_values,
                "optimization_framework": self.optimization_framework,
            }
        else:
            raise ValueError("Insufficient data points for estimation")

    def _estimate_numpy(self, data: np.ndarray, window_sizes: List[int]) -> Tuple[List[float], List[float]]:
        """NumPy implementation of R/S estimation."""
        scales = []
        rs_values = []

        for scale in window_sizes:
            rs_scale = self._calculate_rs_scale_numpy(data, scale)
            if rs_scale > 0:
                scales.append(scale)
                rs_values.append(rs_scale)

        return scales, rs_values

    def _estimate_jax(self, data: np.ndarray, window_sizes: List[int]) -> Tuple[List[float], List[float]]:
        """JAX implementation of R/S estimation."""
        if not JAX_AVAILABLE:
            return self._estimate_numpy(data, window_sizes)

        # Convert to JAX arrays
        data_jax = jnp.array(data)
        scales = []
        rs_values = []

        for scale in window_sizes:
            rs_scale = self._calculate_rs_scale_jax(data_jax, scale)
            if rs_scale > 0:
                scales.append(scale)
                rs_values.append(float(rs_scale))

        return scales, rs_values

    def _estimate_numba(self, data: np.ndarray, window_sizes: List[int]) -> Tuple[List[float], List[float]]:
        """NUMBA implementation of R/S estimation."""
        if not NUMBA_AVAILABLE:
            return self._estimate_numpy(data, window_sizes)

        # For now, fall back to NumPy implementation
        # NUMBA optimization can be added later if needed
        return self._estimate_numpy(data, window_sizes)

    def _calculate_rs_scale_numpy(self, data: np.ndarray, scale: int) -> float:
        """Calculate average R/S statistic for a given scale using NumPy."""
        n = len(data)
        num_windows = n // scale

        if num_windows == 0:
            return 0.0

        total_rs = 0.0
        valid_count = 0

        for i in range(num_windows):
            start_idx = i * scale
            rs_val = self._calculate_rs_window_numpy(data, start_idx, scale)
            if rs_val > 0:
                total_rs += rs_val
                valid_count += 1

        return total_rs / valid_count if valid_count > 0 else 0.0

    def _calculate_rs_window_numpy(self, data: np.ndarray, start_idx: int, scale: int) -> float:
        """Calculate R/S statistic for a single window using NumPy."""
        end_idx = start_idx + scale
        window = data[start_idx:end_idx]

        # Calculate mean
        mean_val = np.mean(window)

        # Calculate cumulative deviation
        cum_dev = np.cumsum(window - mean_val)

        # Calculate range
        R = np.max(cum_dev) - np.min(cum_dev)

        # Calculate standard deviation
        S = np.std(window, ddof=1)

        # Return R/S value
        return R / S if S > 0 else 0.0

    def _calculate_rs_scale_jax(self, data: jnp.ndarray, scale: int) -> jnp.ndarray:
        """Calculate average R/S statistic for a given scale using JAX."""
        n = len(data)
        num_windows = n // scale

        if num_windows == 0:
            return jnp.array(0.0)

        # Vectorized calculation using JAX
        def calculate_rs_for_window(i):
            start_idx = i * scale
            return self._calculate_rs_window_jax(data, start_idx, scale)

        # Calculate R/S for all windows
        rs_values = jax.vmap(calculate_rs_for_window)(jnp.arange(num_windows))
        
        # Filter valid values and compute mean
        valid_rs = rs_values[rs_values > 0]
        return jnp.mean(valid_rs) if len(valid_rs) > 0 else jnp.array(0.0)

    def _calculate_rs_window_jax(self, data: jnp.ndarray, start_idx: int, scale: int) -> jnp.ndarray:
        """Calculate R/S statistic for a single window using JAX."""
        end_idx = start_idx + scale
        
        # Use dynamic_slice for JAX compatibility
        from jax import lax
        window = lax.dynamic_slice(data, (start_idx,), (scale,))

        # Calculate mean
        mean_val = jnp.mean(window)

        # Calculate cumulative deviation
        cum_dev = jnp.cumsum(window - mean_val)

        # Calculate range
        R = jnp.max(cum_dev) - jnp.min(cum_dev)

        # Calculate standard deviation
        S = jnp.std(window, ddof=1)

        # Return R/S value
        return jnp.where(S > 0, R / S, jnp.array(0.0))

    def get_optimization_info(self) -> Dict[str, Any]:
        """
        Get information about available optimizations and current selection.

        Returns
        -------
        dict
            Dictionary containing optimization framework information
        """
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

    def plot_results(self, save_path: Optional[str] = None) -> None:
        """Plot the R/S analysis results."""
        try:
            import matplotlib.pyplot as plt

            if not self.scales or not self.rs_values:
                print("No results to plot. Run estimate() first.")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Plot 1: R/S vs Scale
            ax1.loglog(self.scales, self.rs_values, 'o-', linewidth=2, markersize=8)
            ax1.set_xlabel('Scale (Window Size)')
            ax1.set_ylabel('R/S Statistic')
            ax1.set_title('R/S Analysis: R/S vs Scale')
            ax1.grid(True, alpha=0.3)

            # Plot 2: Log-Log with regression line
            if self.estimated_hurst is not None:
                log_scales = np.log10(self.scales)
                log_rs = np.log10(self.rs_values)
                
                ax2.plot(log_scales, log_rs, 'o', markersize=8, label='Data')
                
                # Regression line
                x_reg = np.array([min(log_scales), max(log_scales)])
                y_reg = self.estimated_hurst * x_reg + np.log10(self.rs_values[0]) - self.estimated_hurst * log_scales[0]
                ax2.plot(x_reg, y_reg, 'r--', linewidth=2, 
                        label=f'Slope = {self.estimated_hurst:.3f}')
                
                ax2.set_xlabel('log10(Scale)')
                ax2.set_ylabel('log10(R/S)')
                ax2.set_title(f'Log-Log Plot (H = {self.estimated_hurst:.3f})')
                ax2.legend()
                ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Plot saved to {save_path}")
            else:
                plt.show()

        except ImportError:
            print("Matplotlib not available for plotting")
