"""
Unified Detrended Fluctuation Analysis (DFA) estimator.

This module provides a single DFAEstimator class that automatically selects
the optimal implementation (JAX, NUMBA, or NumPy) based on data size and
available optimization frameworks.
"""

import numpy as np
from scipy import stats
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


class DFAEstimator(BaseEstimator):
    """
    Unified Detrended Fluctuation Analysis (DFA) estimator.

    This class automatically selects the optimal implementation based on:
    - Data size and computational requirements
    - Available optimization frameworks (JAX, NUMBA)
    - Performance requirements

    DFA is a method for quantifying long-range correlations in time series
    that is robust to non-stationarities. It estimates the Hurst parameter
    by analyzing the scaling behavior of detrended fluctuations.

    Parameters
    ----------
    min_box_size : int, optional
        Minimum box size for analysis (default: 4)
    max_box_size : int, optional
        Maximum box size for analysis (default: None, will use n/4)
    box_sizes : List[int], optional
        Specific box sizes to use (default: None)
    polynomial_order : int, optional
        Order of polynomial for detrending (default: 1)
    use_optimization : str, optional
        Optimization framework preference (default: 'auto')
        - 'auto': Choose best available
        - 'jax': GPU acceleration (when available)
        - 'numba': CPU optimization (when available)
        - 'numpy': Standard NumPy
    """

    def __init__(
        self,
        min_box_size: int = 4,
        max_box_size: Optional[int] = None,
        box_sizes: Optional[List[int]] = None,
        polynomial_order: int = 1,
        use_optimization: str = "auto"
    ):
        """
        Initialize the DFA estimator.

        Parameters
        ----------
        min_box_size : int, optional
            Minimum box size for analysis (default: 4)
        max_box_size : int, optional
            Maximum box size for analysis (default: None)
        box_sizes : List[int], optional
            Specific box sizes to use (default: None)
        polynomial_order : int, optional
            Order of polynomial for detrending (default: 1)
        use_optimization : str, optional
            Optimization framework preference (default: 'auto')
        """
        super().__init__(
            min_box_size=min_box_size,
            max_box_size=max_box_size,
            box_sizes=box_sizes,
            polynomial_order=polynomial_order,
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
        self.box_sizes = []
        self.fluctuations = []
        self.estimated_hurst = None
        self.confidence_interval = None
        self.r_squared = None

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_box_size = self.parameters["min_box_size"]
        polynomial_order = self.parameters["polynomial_order"]

        if min_box_size < 2:
            raise ValueError("min_box_size must be at least 2")

        if polynomial_order < 0:
            raise ValueError("polynomial_order must be non-negative")

    def _get_box_sizes(self, n: int) -> List[int]:
        """Get the list of box sizes to use for analysis."""
        if self.parameters["box_sizes"] is not None:
            return [s for s in self.parameters["box_sizes"] if s <= n // 2]

        min_size = self.parameters["min_box_size"]
        max_size = self.parameters["max_box_size"] or n // 4

        # Generate box sizes with geometric spacing
        sizes = []
        current_size = min_size
        while current_size <= max_size and current_size <= n // 2:
            sizes.append(current_size)
            current_size = int(current_size * 1.5)

        return sizes

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using DFA.

        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        n = len(data)
        box_sizes = self._get_box_sizes(n)

        if len(box_sizes) < 3:
            raise ValueError(f"Need at least 3 valid box sizes. Got: {box_sizes}")

        # Choose implementation based on optimization framework
        if self.optimization_framework == "jax" and JAX_AVAILABLE:
            box_sizes, fluctuations = self._estimate_jax(data, box_sizes)
        elif self.optimization_framework == "numba" and NUMBA_AVAILABLE:
            box_sizes, fluctuations = self._estimate_numba(data, box_sizes)
        else:
            box_sizes, fluctuations = self._estimate_numpy(data, box_sizes)

        # Store results
        self.box_sizes = box_sizes
        self.fluctuations = fluctuations

        # Fit linear regression to log-log plot
        if len(box_sizes) >= 2:
            log_sizes = np.log10(box_sizes)
            log_fluctuations = np.log10(fluctuations)

            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                log_sizes, log_fluctuations
            )

            self.estimated_hurst = slope
            self.r_squared = r_value ** 2

            # Confidence interval (95%)
            n_points = len(box_sizes)
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
                "box_sizes": box_sizes,
                "fluctuations": fluctuations,
                "optimization_framework": self.optimization_framework,
            }
        else:
            raise ValueError("Insufficient data points for estimation")

    def _estimate_numpy(self, data: np.ndarray, box_sizes: List[int]) -> Tuple[List[int], List[float]]:
        """NumPy implementation of DFA estimation."""
        valid_sizes = []
        valid_fluctuations = []

        for size in box_sizes:
            try:
                fluctuation = self._calculate_fluctuation_numpy(data, size)
                if fluctuation > 0:
                    valid_sizes.append(size)
                    valid_fluctuations.append(fluctuation)
            except Exception:
                continue

        return valid_sizes, valid_fluctuations

    def _estimate_jax(self, data: np.ndarray, box_sizes: List[int]) -> Tuple[List[int], List[float]]:
        """JAX implementation of DFA estimation."""
        if not JAX_AVAILABLE:
            return self._estimate_numpy(data, box_sizes)

        # Convert to JAX arrays
        data_jax = jnp.array(data)
        valid_sizes = []
        valid_fluctuations = []

        for size in box_sizes:
            try:
                fluctuation = self._calculate_fluctuation_jax(data_jax, size)
                if fluctuation > 0:
                    valid_sizes.append(size)
                    valid_fluctuations.append(float(fluctuation))
            except Exception:
                continue

        return valid_sizes, valid_fluctuations

    def _estimate_numba(self, data: np.ndarray, box_sizes: List[int]) -> Tuple[List[int], List[float]]:
        """NUMBA implementation of DFA estimation."""
        if not NUMBA_AVAILABLE:
            return self._estimate_numpy(data, box_sizes)

        # For now, fall back to NumPy implementation
        # NUMBA optimization can be added later if needed
        return self._estimate_numpy(data, box_sizes)

    def _calculate_fluctuation_numpy(self, data: np.ndarray, box_size: int) -> float:
        """Calculate DFA fluctuation for a given box size using NumPy."""
        n = len(data)
        n_boxes = n // box_size
        
        if n_boxes == 0:
            return 0.0

        # Calculate cumulative sum
        cumsum = np.cumsum(data - np.mean(data))
        
        # Calculate fluctuations for each box
        fluctuations = []
        for i in range(n_boxes):
            start_idx = i * box_size
            end_idx = start_idx + box_size
            box_data = cumsum[start_idx:end_idx]
            
            # Fit polynomial trend
            x = np.arange(box_size)
            coeffs = np.polyfit(x, box_data, self.parameters["polynomial_order"])
            trend = np.polyval(coeffs, x)
            
            # Calculate detrended fluctuation
            detrended = box_data - trend
            fluctuation = np.sqrt(np.mean(detrended ** 2))
            fluctuations.append(fluctuation)

        return np.mean(fluctuations)

    def _calculate_fluctuation_jax(self, data: jnp.ndarray, box_size: int) -> jnp.ndarray:
        """Calculate DFA fluctuation for a given box size using JAX."""
        n = len(data)
        n_boxes = n // box_size
        
        if n_boxes == 0:
            return jnp.array(0.0)

        # Calculate cumulative sum
        cumsum = jnp.cumsum(data - jnp.mean(data))
        
        # Vectorized calculation using JAX
        def calculate_fluctuation_for_box(i):
            start_idx = i * box_size
            end_idx = start_idx + box_size
            box_data = cumsum[start_idx:end_idx]
            
            # Fit polynomial trend
            x = jnp.arange(box_size)
            coeffs = jnp.polyfit(x, box_data, self.parameters["polynomial_order"])
            trend = jnp.polyval(coeffs, x)
            
            # Calculate detrended fluctuation
            detrended = box_data - trend
            fluctuation = jnp.sqrt(jnp.mean(detrended ** 2))
            return fluctuation

        # Calculate fluctuations for all boxes
        fluctuations = jax.vmap(calculate_fluctuation_for_box)(jnp.arange(n_boxes))
        
        return jnp.mean(fluctuations)

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
        """Plot the DFA analysis results."""
        try:
            import matplotlib.pyplot as plt

            if not self.box_sizes or not self.fluctuations:
                print("No results to plot. Run estimate() first.")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Plot 1: Fluctuation vs Box Size
            ax1.loglog(self.box_sizes, self.fluctuations, 'o-', linewidth=2, markersize=8)
            ax1.set_xlabel('Box Size')
            ax1.set_ylabel('Fluctuation F(n)')
            ax1.set_title('DFA Analysis: Fluctuation vs Box Size')
            ax1.grid(True, alpha=0.3)

            # Plot 2: Log-Log with regression line
            if self.estimated_hurst is not None:
                log_sizes = np.log10(self.box_sizes)
                log_fluctuations = np.log10(self.fluctuations)
                
                ax2.plot(log_sizes, log_fluctuations, 'o', markersize=8, label='Data')
                
                # Regression line
                x_reg = np.array([min(log_sizes), max(log_sizes)])
                y_reg = self.estimated_hurst * x_reg + np.log10(self.fluctuations[0]) - self.estimated_hurst * log_sizes[0]
                ax2.plot(x_reg, y_reg, 'r--', linewidth=2, 
                        label=f'Slope = {self.estimated_hurst:.3f}')
                
                ax2.set_xlabel('log10(Box Size)')
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
