"""
Unified Detrended Moving Average (DMA) estimator for Hurst parameter.

This module provides a single DMAEstimator class that automatically selects
the optimal implementation (JAX, NUMBA, or NumPy) based on data size and
available optimization frameworks.

The DMA method is a variant of DFA that uses a moving average instead
of polynomial fitting for detrending. It is computationally efficient
and robust to various types of non-stationarity.

The method works by:
1. Computing the cumulative sum of the time series
2. For each window size, calculating the moving average
3. Detrending by subtracting the moving average
4. Computing the fluctuation function
5. Fitting a power law relationship: F(n) ~ n^H
"""

import numpy as np
from scipy import stats
from scipy.ndimage import uniform_filter1d
from typing import Dict, Any, List, Tuple, Optional
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


class DMAEstimator(BaseEstimator):
    """
    Unified Detrended Moving Average (DMA) estimator for Hurst parameter.

    This class automatically selects the optimal implementation based on:
    - Data size and computational requirements
    - Available optimization frameworks (JAX, NUMBA)
    - Performance requirements

    The DMA method is a variant of DFA that uses a moving average instead
    of polynomial fitting for detrending. It is computationally efficient
    and robust to various types of non-stationarity.

    Parameters
    ----------
    min_window_size : int, default=4
        Minimum window size for DMA calculation.
    max_window_size : int, optional
        Maximum window size. If None, uses n/4 where n is data length.
    window_sizes : List[int], optional
        Specific window sizes to use. If provided, overrides min/max.
    overlap : bool, default=True
        Whether to use overlapping windows for moving average.
    use_optimization : str, optional
        Optimization framework preference (default: 'auto')
        - 'auto': Choose best available
        - 'jax': GPU acceleration (when available)
        - 'numba': CPU optimization (when available)
        - 'numpy': Standard NumPy
    """

    def __init__(
        self,
        min_window_size: int = 4,
        max_window_size: Optional[int] = None,
        window_sizes: Optional[List[int]] = None,
        overlap: bool = True,
        use_optimization: str = "auto"
    ):
        """
        Initialize the DMA estimator.

        Parameters
        ----------
        min_window_size : int, default=4
            Minimum window size for DMA calculation.
        max_window_size : int, optional
            Maximum window size. If None, uses n/4 where n is data length.
        window_sizes : List[int], optional
            Specific window sizes to use. If provided, overrides min/max.
        overlap : bool, default=True
            Whether to use overlapping windows for moving average.
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
        self.window_sizes = []
        self.fluctuation_values = []
        self.estimated_hurst = None
        self.confidence_interval = None
        self.r_squared = None

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["min_window_size"] < 3:
            raise ValueError("min_window_size must be at least 3")

        if self.parameters["max_window_size"] is not None:
            if self.parameters["max_window_size"] <= self.parameters["min_window_size"]:
                raise ValueError("max_window_size must be greater than min_window_size")

        if self.parameters["window_sizes"] is not None:
            if not all(size >= 3 for size in self.parameters["window_sizes"]):
                raise ValueError("All window sizes must be at least 3")
            if not all(
                size1 < size2
                for size1, size2 in zip(
                    self.parameters["window_sizes"][:-1],
                    self.parameters["window_sizes"][1:],
                )
            ):
                raise ValueError("Window sizes must be in ascending order")

    def _get_window_sizes(self, n: int) -> List[int]:
        """Get the list of window sizes to use for analysis."""
        if self.parameters["window_sizes"] is not None:
            return [w for w in self.parameters["window_sizes"] if w <= n // 2]

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
        Estimate the Hurst parameter using DMA method.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing estimation results:
            - 'hurst_parameter': Estimated Hurst parameter
            - 'window_sizes': List of window sizes used
            - 'fluctuation_values': List of fluctuation values for each window size
            - 'r_squared': R-squared value of the linear fit
            - 'std_error': Standard error of the Hurst parameter estimate
            - 'confidence_interval': 95% confidence interval for H
        """
        if len(data) < 10:
            raise ValueError("Data length must be at least 10 for DMA analysis")

        n = len(data)
        window_sizes = self._get_window_sizes(n)

        if len(window_sizes) < 3:
            raise ValueError(f"Need at least 3 valid window sizes. Got: {window_sizes}")

        # Choose implementation based on optimization framework
        if self.optimization_framework == "jax" and JAX_AVAILABLE:
            window_sizes, fluctuation_values = self._estimate_jax(data, window_sizes)
        elif self.optimization_framework == "numba" and NUMBA_AVAILABLE:
            window_sizes, fluctuation_values = self._estimate_numba(data, window_sizes)
        else:
            window_sizes, fluctuation_values = self._estimate_numpy(data, window_sizes)

        # Store results
        self.window_sizes = window_sizes
        self.fluctuation_values = fluctuation_values

        # Fit linear regression to log-log plot
        if len(window_sizes) >= 2:
            log_sizes = np.log10(window_sizes)
            log_fluctuations = np.log10(fluctuation_values)

            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                log_sizes, log_fluctuations
            )

            self.estimated_hurst = slope
            self.r_squared = r_value ** 2

            # Confidence interval (95%)
            n_points = len(window_sizes)
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
                "std_error": std_err,
                "window_sizes": window_sizes,
                "fluctuation_values": fluctuation_values,
                "optimization_framework": self.optimization_framework,
            }
        else:
            raise ValueError("Insufficient data points for estimation")

    def _estimate_numpy(self, data: np.ndarray, window_sizes: List[int]) -> Tuple[List[int], List[float]]:
        """NumPy implementation of DMA estimation."""
        valid_sizes = []
        valid_fluctuations = []

        for size in window_sizes:
            try:
                fluctuation = self._calculate_dma_fluctuation_numpy(data, size)
                if fluctuation > 0 and not np.isnan(fluctuation):
                    valid_sizes.append(size)
                    valid_fluctuations.append(fluctuation)
            except Exception:
                continue

        return valid_sizes, valid_fluctuations

    def _estimate_jax(self, data: np.ndarray, window_sizes: List[int]) -> Tuple[List[int], List[float]]:
        """JAX implementation of DMA estimation."""
        if not JAX_AVAILABLE:
            return self._estimate_numpy(data, window_sizes)

        # Convert to JAX arrays
        data_jax = jnp.array(data)
        valid_sizes = []
        valid_fluctuations = []

        for size in window_sizes:
            try:
                fluctuation = self._calculate_dma_fluctuation_jax(data_jax, size)
                if fluctuation > 0 and not jnp.isnan(fluctuation):
                    valid_sizes.append(size)
                    valid_fluctuations.append(float(fluctuation))
            except Exception as e:
                print(f"JAX calculation failed for size={size}: {e}")
                continue

        # If JAX implementation fails, fall back to NumPy
        if len(valid_sizes) < 3:
            print(f"JAX implementation returned insufficient results ({len(valid_sizes)}), falling back to NumPy")
            return self._estimate_numpy(data, window_sizes)

        return valid_sizes, valid_fluctuations

    def _estimate_numba(self, data: np.ndarray, window_sizes: List[int]) -> Tuple[List[int], List[float]]:
        """NUMBA implementation of DMA estimation."""
        if not NUMBA_AVAILABLE:
            return self._estimate_numpy(data, window_sizes)

        # Use NUMBA-optimized calculation
        valid_sizes = []
        valid_fluctuations = []

        for size in window_sizes:
            try:
                fluctuation = self._calculate_dma_fluctuation_numba(data, size)
                if fluctuation > 0 and not np.isnan(fluctuation):
                    valid_sizes.append(size)
                    valid_fluctuations.append(fluctuation)
            except Exception as e:
                print(f"NUMBA calculation failed for size={size}: {e}")
                continue

        # If NUMBA implementation fails, fall back to NumPy
        if len(valid_sizes) < 3:
            print(f"NUMBA implementation returned insufficient results ({len(valid_sizes)}), falling back to NumPy")
            return self._estimate_numpy(data, window_sizes)

        return valid_sizes, valid_fluctuations

    def _calculate_dma_fluctuation_numpy(self, data: np.ndarray, window_size: int) -> float:
        """Calculate DMA fluctuation for a given window size using NumPy."""
        n = len(data)
        if window_size > n:
            return np.nan

        # Calculate cumulative sum
        cumsum = np.cumsum(data - np.mean(data))
        
        # Calculate moving average
        if self.parameters["overlap"]:
            # Use scipy's uniform filter for efficient moving average
            moving_avg = uniform_filter1d(cumsum, size=window_size, mode='constant')
        else:
            # Non-overlapping windows
            moving_avg = np.zeros_like(cumsum)
            for i in range(0, n, window_size):
                end_idx = min(i + window_size, n)
                moving_avg[i:end_idx] = np.mean(cumsum[i:end_idx])

        # Detrend by subtracting moving average
        detrended = cumsum - moving_avg
        
        # Calculate root mean square fluctuation
        fluctuation = np.sqrt(np.mean(detrended ** 2))
        
        return fluctuation

    def _calculate_dma_fluctuation_jax(self, data: jnp.ndarray, window_size: int) -> jnp.ndarray:
        """Calculate DMA fluctuation for a given window size using JAX."""
        n = len(data)
        if window_size > n:
            return jnp.array(jnp.nan)

        # Calculate cumulative sum
        cumsum = jnp.cumsum(data - jnp.mean(data))
        
        # Calculate moving average using JAX
        if self.parameters["overlap"]:
            # Simple moving average using JAX
            def moving_average_1d(x, size):
                return jnp.convolve(x, jnp.ones(size) / size, mode='same')
            
            moving_avg = moving_average_1d(cumsum, window_size)
        else:
            # Non-overlapping windows
            moving_avg = jnp.zeros_like(cumsum)
            
            def update_window(i):
                end_idx = jnp.minimum(i + window_size, n)
                return jnp.mean(cumsum[i:end_idx])
            
            # Update moving average for each window
            for i in range(0, n, window_size):
                end_idx = jnp.minimum(i + window_size, n)
                window_mean = jnp.mean(cumsum[i:end_idx])
                moving_avg = moving_avg.at[i:end_idx].set(window_mean)

        # Detrend by subtracting moving average
        detrended = cumsum - moving_avg
        
        # Calculate root mean square fluctuation
        fluctuation = jnp.sqrt(jnp.mean(detrended ** 2))
        
        return fluctuation

    def _calculate_dma_fluctuation_numba(self, data: np.ndarray, window_size: int) -> float:
        """Calculate DMA fluctuation for a given window size using NUMBA."""
        if not NUMBA_AVAILABLE:
            return self._calculate_dma_fluctuation_numpy(data, window_size)

        # NUMBA-optimized implementation
        return self._numba_calculate_dma_fluctuation(data, window_size)

    @staticmethod
    @numba_jit(nopython=True, parallel=True, cache=True)
    def _numba_calculate_dma_fluctuation(data: np.ndarray, window_size: int) -> float:
        """
        NUMBA-optimized DMA fluctuation calculation.
        
        Parameters
        ----------
        data : np.ndarray
            Time series data
        window_size : int
            Window size for moving average
            
        Returns
        -------
        float
            DMA fluctuation value
        """
        n = len(data)
        if window_size > n:
            return np.nan

        # Calculate cumulative sum
        mean_val = np.mean(data)
        cumsum = np.zeros(n)
        cumsum[0] = data[0] - mean_val
        for i in range(1, n):
            cumsum[i] = cumsum[i-1] + (data[i] - mean_val)
        
        # Calculate moving average
        moving_avg = np.zeros(n)
        for i in range(n):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(n, i + window_size // 2 + 1)
            moving_avg[i] = np.mean(cumsum[start_idx:end_idx])

        # Detrend by subtracting moving average
        detrended = cumsum - moving_avg
        
        # Calculate root mean square fluctuation
        fluctuation = np.sqrt(np.mean(detrended ** 2))
        
        return fluctuation

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
        """Plot the DMA analysis results."""
        try:
            import matplotlib.pyplot as plt
            
            if not self.window_sizes or not self.fluctuation_values:
                print("No results to plot. Run estimate() first.")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Plot 1: Fluctuation vs Window Size
            ax1.loglog(self.window_sizes, self.fluctuation_values, 'o-', linewidth=2, markersize=8)
            ax1.set_xlabel('Window Size')
            ax1.set_ylabel('Fluctuation F(n)')
            ax1.set_title('DMA Analysis: Fluctuation vs Window Size')
            ax1.grid(True, alpha=0.3)

            # Plot 2: Log-Log with regression line
            if self.estimated_hurst is not None:
                log_sizes = np.log10(self.window_sizes)
                log_fluctuations = np.log10(self.fluctuation_values)
                
                ax2.plot(log_sizes, log_fluctuations, 'o', markersize=8, label='Data')
                
                # Regression line
                x_reg = np.array([min(log_sizes), max(log_sizes)])
                y_reg = self.estimated_hurst * x_reg + np.log10(self.fluctuation_values[0]) - self.estimated_hurst * log_sizes[0]
                ax2.plot(x_reg, y_reg, 'r--', linewidth=2, 
                        label=f'Slope = {self.estimated_hurst:.3f}')
                
                ax2.set_xlabel('log10(Window Size)')
                ax2.set_ylabel('log10(Fluctuation)')
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
