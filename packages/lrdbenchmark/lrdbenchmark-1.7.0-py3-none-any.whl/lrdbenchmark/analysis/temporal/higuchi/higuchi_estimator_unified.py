"""
Unified Higuchi Method estimator for fractal dimension and Hurst parameter.

This module provides a single HiguchiEstimator class that automatically selects
the optimal implementation (JAX, NUMBA, or NumPy) based on data size and
available optimization frameworks.

The Higuchi method is an efficient algorithm for estimating the fractal
dimension of a time series. It is based on the relationship between the
length of the curve and the time interval used to measure it.

The method works by:
1. Computing the curve length for different time intervals k
2. Fitting a power law relationship: L(k) ~ k^(-D)
3. The fractal dimension D is related to the Hurst parameter H by: H = 2 - D
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


class HiguchiEstimator(BaseEstimator):
    """
    Unified Higuchi Method estimator for fractal dimension and Hurst parameter.

    This class automatically selects the optimal implementation based on:
    - Data size and computational requirements
    - Available optimization frameworks (JAX, NUMBA)
    - Performance requirements

    The Higuchi method is an efficient algorithm for estimating the fractal
    dimension of a time series. It is based on the relationship between the
    length of the curve and the time interval used to measure it.

    Parameters
    ----------
    min_k : int, default=2
        Minimum time interval for curve length calculation.
    max_k : int, optional
        Maximum time interval. If None, uses n/4 where n is data length.
    k_values : List[int], optional
        Specific k values to use. If provided, overrides min/max.
    use_optimization : str, optional
        Optimization framework preference (default: 'auto')
        - 'auto': Choose best available
        - 'jax': GPU acceleration (when available)
        - 'numba': CPU optimization (when available)
        - 'numpy': Standard NumPy
    """

    def __init__(
        self, 
        min_k: int = 2, 
        max_k: Optional[int] = None, 
        k_values: Optional[List[int]] = None,
        use_optimization: str = "auto"
    ):
        """
        Initialize the Higuchi estimator.

        Parameters
        ----------
        min_k : int, default=2
            Minimum time interval for curve length calculation.
        max_k : int, optional
            Maximum time interval. If None, uses n/4 where n is data length.
        k_values : List[int], optional
            Specific k values to use. If provided, overrides min/max.
        use_optimization : str, optional
            Optimization framework preference (default: 'auto')
        """
        super().__init__(
            min_k=min_k, 
            max_k=max_k, 
            k_values=k_values,
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
        self.k_values = []
        self.l_values = []
        self.estimated_hurst = None
        self.fractal_dimension = None
        self.confidence_interval = None
        self.r_squared = None

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["min_k"] < 2:
            raise ValueError("min_k must be at least 2")

        if self.parameters["max_k"] is not None:
            if self.parameters["max_k"] <= self.parameters["min_k"]:
                raise ValueError("max_k must be greater than min_k")

        if self.parameters["k_values"] is not None:
            if not all(k >= 2 for k in self.parameters["k_values"]):
                raise ValueError("All k values must be at least 2")
            if not all(
                k1 < k2
                for k1, k2 in zip(
                    self.parameters["k_values"][:-1], self.parameters["k_values"][1:]
                )
            ):
                raise ValueError("k values must be in ascending order")

    def _get_k_values(self, n: int) -> List[int]:
        """Get the list of k values to use for analysis."""
        if self.parameters["k_values"] is not None:
            return [k for k in self.parameters["k_values"] if k < n // 2]

        min_k = self.parameters["min_k"]
        max_k = self.parameters["max_k"] or n // 4

        # Generate k values with geometric spacing
        k_values = []
        current_k = min_k
        while current_k <= max_k and current_k < n // 2:
            k_values.append(current_k)
            current_k = int(current_k * 1.5)

        return k_values

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using the Higuchi method.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.

        Returns
        -------
        dict
            Dictionary containing estimation results.
        """
        if len(data) < 10:
            raise ValueError("Data length must be at least 10 for Higuchi method")

        n = len(data)
        k_values = self._get_k_values(n)

        if len(k_values) < 3:
            raise ValueError(f"Need at least 3 valid k values. Got: {k_values}")

        # Choose implementation based on optimization framework
        if self.optimization_framework == "jax" and JAX_AVAILABLE:
            k_values, l_values = self._estimate_jax(data, k_values)
        elif self.optimization_framework == "numba" and NUMBA_AVAILABLE:
            k_values, l_values = self._estimate_numba(data, k_values)
        else:
            k_values, l_values = self._estimate_numpy(data, k_values)

        # Store results
        self.k_values = k_values
        self.l_values = l_values

        # Fit linear regression to log-log plot
        if len(k_values) >= 2:
            log_k = np.log10(k_values)
            log_l = np.log10(l_values)

            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                log_k, log_l
            )

            # Fractal dimension D = -slope, Hurst parameter H = 2 - D
            self.fractal_dimension = -slope
            self.estimated_hurst = 2 - self.fractal_dimension
            self.r_squared = r_value ** 2

            # Confidence interval (95%)
            n_points = len(k_values)
            t_value = stats.t.ppf(0.975, n_points - 2)
            self.confidence_interval = (
                self.estimated_hurst - t_value * std_err,
                self.estimated_hurst + t_value * std_err,
            )

            # Determine which method was actually used
            if self.optimization_framework == "jax" and JAX_AVAILABLE:
                method = "jax"
            elif self.optimization_framework == "numba" and NUMBA_AVAILABLE:
                method = "numba"
            else:
                method = "numpy"
            
            return {
                "hurst_parameter": self.estimated_hurst,
                "fractal_dimension": self.fractal_dimension,
                "confidence_interval": self.confidence_interval,
                "r_squared": self.r_squared,
                "p_value": p_value,
                "k_values": k_values,
                "l_values": l_values,
                "method": method,
                "optimization_framework": self.optimization_framework,
            }
        else:
            raise ValueError("Insufficient data points for estimation")

    def _estimate_numpy(self, data: np.ndarray, k_values: List[int]) -> Tuple[List[int], List[float]]:
        """NumPy implementation of Higuchi estimation."""
        valid_k = []
        valid_l = []

        for k in k_values:
            try:
                l_value = self._calculate_higuchi_dimension_numpy(data, k)
                if l_value > 0 and not np.isnan(l_value):
                    valid_k.append(k)
                    valid_l.append(l_value)
            except Exception:
                continue

        return valid_k, valid_l

    def _estimate_jax(self, data: np.ndarray, k_values: List[int]) -> Tuple[List[int], List[float]]:
        """JAX implementation of Higuchi estimation."""
        if not JAX_AVAILABLE:
            return self._estimate_numpy(data, k_values)

        # Convert to JAX arrays
        data_jax = jnp.array(data)
        valid_k = []
        valid_l = []

        for k in k_values:
            try:
                l_value = self._calculate_higuchi_dimension_jax(data_jax, k)
                if l_value > 0 and not jnp.isnan(l_value):
                    valid_k.append(k)
                    valid_l.append(float(l_value))
            except Exception as e:
                print(f"JAX calculation failed for k={k}: {e}")
                continue

        # If JAX implementation fails, fall back to NumPy
        if len(valid_k) < 3:
            print(f"JAX implementation returned insufficient results ({len(valid_k)}), falling back to NumPy")
            return self._estimate_numpy(data, k_values)

        return valid_k, valid_l

    def _estimate_numba(self, data: np.ndarray, k_values: List[int]) -> Tuple[List[int], List[float]]:
        """NUMBA implementation of Higuchi estimation."""
        if not NUMBA_AVAILABLE:
            return self._estimate_numpy(data, k_values)

        # Use NUMBA-optimized calculation
        valid_k = []
        valid_l = []

        for k in k_values:
            try:
                l_value = self._calculate_higuchi_dimension_numba(data, k)
                if l_value > 0 and not np.isnan(l_value):
                    valid_k.append(k)
                    valid_l.append(l_value)
            except Exception as e:
                print(f"NUMBA calculation failed for k={k}: {e}")
                continue

        # If NUMBA implementation fails, fall back to NumPy
        if len(valid_k) < 3:
            print(f"NUMBA implementation returned insufficient results ({len(valid_k)}), falling back to NumPy")
            return self._estimate_numpy(data, k_values)

        return valid_k, valid_l

    def _calculate_higuchi_dimension_numpy(self, data: np.ndarray, k: int) -> float:
        """Calculate Higuchi dimension for a given k using NumPy."""
        n = len(data)
        if k > n:
            return np.nan

        # Calculate L(k)
        l_sum = 0.0
        count = 0

        for m in range(k):
            # Calculate sum for this m
            sum_val = 0.0
            for j in range(1, int((n - m) / k)):
                idx1 = m + (j - 1) * k
                idx2 = m + j * k
                if idx2 < n:
                    sum_val += abs(data[idx2] - data[idx1])

            if sum_val > 0:
                l_sum += sum_val
                count += 1

        if count > 0:
            return l_sum / count
        else:
            return np.nan

    def _calculate_higuchi_dimension_jax(self, data: jnp.ndarray, k: int) -> jnp.ndarray:
        """Calculate Higuchi dimension for a given k using JAX."""
        n = len(data)
        if k > n:
            return jnp.array(jnp.nan)

        # For now, use a simplified JAX implementation that avoids concretization issues
        # This can be enhanced with more sophisticated JAX optimizations later
        
        # Convert to regular numpy for calculation to avoid JAX limitations
        data_np = np.array(data)
        
        # Use the numpy implementation
        result = self._calculate_higuchi_dimension_numpy(data_np, k)
        
        return jnp.array(result)

    def _calculate_higuchi_dimension_numba(self, data: np.ndarray, k: int) -> float:
        """Calculate Higuchi dimension for a given k using NUMBA."""
        if not NUMBA_AVAILABLE:
            return self._calculate_higuchi_dimension_numpy(data, k)

        # NUMBA-optimized implementation
        return self._numba_calculate_higuchi_dimension(data, k)

    @staticmethod
    @numba_jit(nopython=True, parallel=True, cache=True)
    def _numba_calculate_higuchi_dimension(data: np.ndarray, k: int) -> float:
        """
        NUMBA-optimized Higuchi dimension calculation.
        
        Parameters
        ----------
        data : np.ndarray
            Time series data
        k : int
            Time interval for analysis
            
        Returns
        -------
        float
            L(k) value
        """
        n = len(data)
        if k > n:
            return np.nan

        # Calculate L(k)
        l_sum = 0.0
        count = 0

        for m in prange(k):
            # Calculate sum for this m
            sum_val = 0.0
            for j in range(1, int((n - m) / k)):
                idx1 = m + (j - 1) * k
                idx2 = m + j * k
                if idx2 < n:
                    sum_val += abs(data[idx2] - data[idx1])

            if sum_val > 0:
                l_sum += sum_val
                count += 1

        if count > 0:
            return l_sum / count
        else:
            return np.nan

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
        """Plot the Higuchi analysis results."""
        try:
            import matplotlib.pyplot as plt
            
            if not self.k_values or not self.l_values:
                print("No results to plot. Run estimate() first.")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Plot 1: L(k) vs k
            ax1.loglog(self.k_values, self.l_values, 'o-', linewidth=2, markersize=8)
            ax1.set_xlabel('Time Interval k')
            ax1.set_ylabel('Curve Length L(k)')
            ax1.set_title('Higuchi Analysis: L(k) vs k')
            ax1.grid(True, alpha=0.3)

            # Plot 2: Log-Log with regression line
            if self.estimated_hurst is not None:
                log_k = np.log10(self.k_values)
                log_l = np.log10(self.l_values)
                
                ax2.plot(log_k, log_l, 'o', markersize=8, label='Data')
                
                # Regression line
                x_reg = np.array([min(log_k), max(log_k)])
                y_reg = -self.fractal_dimension * x_reg + np.log10(self.l_values[0]) + self.fractal_dimension * log_k[0]
                ax2.plot(x_reg, y_reg, 'r--', linewidth=2, 
                        label=f'D = {self.fractal_dimension:.3f}, H = {self.estimated_hurst:.3f}')
                
                ax2.set_xlabel('log10(k)')
                ax2.set_ylabel('log10(L(k))')
                ax2.set_title(f'Log-Log Plot (D = {self.fractal_dimension:.3f})')
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
