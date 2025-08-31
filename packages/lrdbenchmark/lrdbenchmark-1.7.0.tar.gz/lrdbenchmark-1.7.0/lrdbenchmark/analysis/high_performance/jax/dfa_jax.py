"""
JAX-optimized Detrended Fluctuation Analysis (DFA) estimator.

This module provides a JAX-optimized version of the DFA estimator for GPU acceleration
and improved performance on large datasets.
"""

import jax
import jax.numpy as jnp
from jax import jit, vmap
from typing import Dict, Any, List, Tuple
import numpy as np
import sys
import os

# Add the project root to the path to import BaseEstimator
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class DFAEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Detrended Fluctuation Analysis (DFA) estimator.

    This version uses JAX for GPU acceleration and improved performance.
    It maintains the same interface as the original DFA estimator but with
    significant performance improvements, especially for large datasets.

    Parameters
    ----------
    min_box_size : int, optional
        Minimum box size for analysis (default: 4)
    max_box_size : int, optional
        Maximum box size for analysis (default: None, will use n/4)
    box_sizes : array-like, optional
        Specific box sizes to use (default: None)
    polynomial_order : int, optional
        Order of polynomial for detrending (default: 1)
    use_gpu : bool, optional
        Whether to use GPU acceleration (default: True)
    """

    def __init__(
        self,
        min_box_size: int = 4,
        max_box_size: int = None,
        box_sizes: List[int] = None,
        polynomial_order: int = 1,
        use_gpu: bool = True,
    ):
        """
        Initialize the JAX-optimized DFA estimator.

        Parameters
        ----------
        min_box_size : int, optional
            Minimum box size for analysis (default: 4)
        max_box_size : int, optional
            Maximum box size for analysis (default: None)
        box_sizes : array-like, optional
            Specific box sizes to use (default: None)
        polynomial_order : int, optional
            Order of polynomial for detrending (default: 1)
        use_gpu : bool, optional
            Whether to use GPU acceleration (default: True)
        """
        super().__init__(
            min_box_size=min_box_size,
            max_box_size=max_box_size,
            box_sizes=box_sizes,
            polynomial_order=polynomial_order,
            use_gpu=use_gpu,
        )

        # Configure JAX for GPU usage
        if use_gpu:
            try:
                # Check if GPU is available
                jax.devices("gpu")
                print("JAX DFA: Using GPU acceleration")
            except RuntimeError:
                print("JAX DFA: GPU not available, using CPU")
                self.parameters["use_gpu"] = False
        else:
            print("JAX DFA: Using CPU (GPU disabled)")

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_box_size = self.parameters["min_box_size"]
        polynomial_order = self.parameters["polynomial_order"]

        if min_box_size < 2:
            raise ValueError("min_box_size must be at least 2")

        if polynomial_order < 0:
            raise ValueError("polynomial_order must be non-negative")

    @staticmethod
    def _calculate_fluctuation_jax(
        segment: jnp.ndarray, polynomial_order: int
    ) -> jnp.ndarray:
        """
        JAX-optimized calculation of detrended fluctuation for a segment.

        Parameters
        ----------
        segment : jnp.ndarray
            Data segment to analyze
        polynomial_order : int
            Order of polynomial for detrending

        Returns
        -------
        jnp.ndarray
            Detrended fluctuation
        """
        box_size = len(segment)
        x = jnp.arange(box_size, dtype=jnp.float32)

        # Fit polynomial trend
        if polynomial_order == 0:
            trend = jnp.mean(segment)
        else:
            # Use JAX's polyfit equivalent
            coeffs = jnp.polyfit(x, segment, polynomial_order)
            trend = jnp.polyval(coeffs, x)

        # Detrend
        detrended = segment - trend

        # Calculate fluctuation
        f = jnp.mean(detrended**2)
        return f

    def _calculate_fluctuation_single(self, data: jnp.ndarray, box_size: int) -> float:
        """
        Calculate detrended fluctuation for a given box size (matching original implementation).

        Parameters
        ----------
        data : jnp.ndarray
            Time series data
        box_size : int
            Size of the box for analysis

        Returns
        -------
        float
            Detrended fluctuation
        """
        n = len(data)
        polynomial_order = self.parameters["polynomial_order"]

        # Calculate cumulative sum
        cumsum = jnp.cumsum(data - jnp.mean(data))

        # Number of boxes
        n_boxes = n // box_size

        if n_boxes == 0:
            return 0.0

        # Calculate fluctuations for each box
        fluctuations = []

        for i in range(n_boxes):
            start_idx = i * box_size
            end_idx = start_idx + box_size

            # Extract segment
            segment = cumsum[start_idx:end_idx]
            x = jnp.arange(box_size, dtype=jnp.float32)

            # Fit polynomial trend
            if polynomial_order == 0:
                trend = jnp.mean(segment)
            else:
                coeffs = jnp.polyfit(x, segment, polynomial_order)
                trend = jnp.polyval(coeffs, x)

            # Detrend
            detrended = segment - trend

            # Calculate fluctuation
            f = jnp.mean(detrended**2)
            fluctuations.append(f)

        # Return root mean square fluctuation
        return jnp.sqrt(jnp.mean(jnp.array(fluctuations)))

    @staticmethod
    def _calculate_fluctuations_batch(
        data: jnp.ndarray, box_sizes: jnp.ndarray, polynomial_order: int
    ) -> jnp.ndarray:
        """
        JAX-optimized batch calculation of fluctuations for multiple box sizes.

        Parameters
        ----------
        data : jnp.ndarray
            Time series data
        box_sizes : jnp.ndarray
            Array of box sizes to analyze
        polynomial_order : int
            Order of polynomial for detrending

        Returns
        -------
        jnp.ndarray
            Array of fluctuations for each box size
        """
        n = len(data)
        fluctuations = []

        for box_size in box_sizes:
            n_boxes = n // box_size
            if n_boxes == 0:
                fluctuations.append(jnp.nan)
                continue

            # Calculate cumulative sum
            cumsum = jnp.cumsum(data - jnp.mean(data))

            # Create segments for all boxes
            segment_fluctuations = []
            for i in range(n_boxes):
                start_idx = i * box_size
                end_idx = start_idx + box_size
                segment = cumsum[start_idx:end_idx]

                # Calculate fluctuation for this segment
                f = DFAEstimatorJAX._calculate_fluctuation_jax(
                    segment, polynomial_order
                )
                segment_fluctuations.append(f)

            # Return mean fluctuation
            mean_f = jnp.mean(jnp.array(segment_fluctuations))
            fluctuations.append(mean_f)

        return jnp.array(fluctuations)

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using JAX-optimized DFA.

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

        # Convert to JAX array
        data_jax = jnp.array(data, dtype=jnp.float32)

        # Determine box sizes (exactly matching original implementation)
        if self.parameters["box_sizes"] is not None:
            box_sizes = jnp.array(self.parameters["box_sizes"], dtype=jnp.int32)
        else:
            min_size = self.parameters["min_box_size"]
            max_size = self.parameters["max_box_size"] or n // 4

            # Create box sizes with approximately equal spacing in log space (exactly matching original)
            box_sizes = jnp.unique(
                jnp.logspace(
                    jnp.log10(min_size),
                    jnp.log10(max_size),
                    num=min(20, max_size - min_size + 1),
                    dtype=jnp.int32,
                )
            )

            # Filter out box sizes that are too small (matching original behavior)
            box_sizes = box_sizes[box_sizes >= min_size]

        # Calculate fluctuations for each box size (matching original logic)
        fluctuations = []
        valid_box_sizes = []

        for s in box_sizes:
            if s > n:
                continue

            f = self._calculate_fluctuation_single(data_jax, s)
            if jnp.isfinite(f) and f > 0:
                fluctuations.append(f)
                valid_box_sizes.append(s)

        if len(fluctuations) < 3:
            raise ValueError("Insufficient data points for DFA analysis")

        # Convert to arrays
        valid_box_sizes = jnp.array(valid_box_sizes, dtype=jnp.float32)
        valid_fluctuations = jnp.array(fluctuations, dtype=jnp.float32)

        if len(valid_fluctuations) < 3:
            raise ValueError("Insufficient valid fluctuations for DFA analysis")

        # Linear regression in log-log space
        log_sizes = jnp.log(valid_box_sizes.astype(jnp.float32))
        log_fluctuations = jnp.log(valid_fluctuations.astype(jnp.float32))

        # Use JAX's linear algebra for regression
        X = jnp.column_stack([log_sizes, jnp.ones_like(log_sizes)])
        coeffs, residuals, rank, s = jnp.linalg.lstsq(X, log_fluctuations, rcond=None)

        slope = coeffs[0]
        intercept = coeffs[1]

        # Calculate R-squared
        y_pred = X @ coeffs
        ss_res = jnp.sum((log_fluctuations - y_pred) ** 2)
        ss_tot = jnp.sum((log_fluctuations - jnp.mean(log_fluctuations)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        # Calculate standard error
        n_points = len(log_fluctuations)
        mse = ss_res / (n_points - 2)
        std_error = jnp.sqrt(mse / jnp.sum((log_sizes - jnp.mean(log_sizes)) ** 2))

        # Hurst parameter is the slope
        H = float(slope)

        # Store results
        self.results = {
            "hurst_parameter": H,
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "p_value": None,  # JAX doesn't have built-in p-value calculation
            "std_error": float(std_error),
            "box_sizes": valid_box_sizes.tolist(),
            "fluctuations": valid_fluctuations.tolist(),
            "log_sizes": log_sizes.tolist(),
            "log_fluctuations": log_fluctuations.tolist(),
            "slope": float(slope),
            "n_points": int(n_points),
            "optimization": "JAX",
        }

        return self.results

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for estimated parameters.

        Parameters
        ----------
        confidence_level : float, optional
            Confidence level (default: 0.95)

        Returns
        -------
        dict
            Dictionary containing confidence intervals
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # Calculate confidence interval for Hurst parameter
        H = self.results["hurst_parameter"]
        std_error = self.results["std_error"]
        n_points = self.results["n_points"]

        # Use t-distribution for small samples, normal for large samples
        if n_points < 30:
            # For small samples, we'd need scipy.stats.t.ppf
            # For now, use normal approximation
            z_score = 1.96  # 95% confidence for normal distribution
        else:
            z_score = 1.96  # 95% confidence for normal distribution

        margin_of_error = z_score * std_error
        ci_lower = H - margin_of_error
        ci_upper = H + margin_of_error

        return {"hurst_parameter": (float(ci_lower), float(ci_upper))}

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the estimation.

        Returns
        -------
        dict
            Dictionary containing quality metrics
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        return {
            "r_squared": self.results["r_squared"],
            "std_error": self.results["std_error"],
            "n_points": self.results["n_points"],
            "optimization": self.results["optimization"],
        }

    def plot_scaling(self, save_path: str = None, show: bool = True) -> None:
        """
        Plot the scaling behavior.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot (default: None)
        show : bool, optional
            Whether to display the plot (default: True)
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        # Switch to non-interactive backend for CI compatibility
        plt.switch_backend("Agg")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot data points
        ax.scatter(
            self.results["log_sizes"],
            self.results["log_fluctuations"],
            alpha=0.6,
            label="Data points",
        )

        # Plot regression line
        x_min, x_max = min(self.results["log_sizes"]), max(self.results["log_sizes"])
        y_min = self.results["intercept"] + self.results["slope"] * x_min
        y_max = self.results["intercept"] + self.results["slope"] * x_max

        ax.plot(
            [x_min, x_max],
            [y_min, y_max],
            "r-",
            label=f'Regression (H = {self.results["hurst_parameter"]:.3f})',
        )

        ax.set_xlabel("log(Box Size)")
        ax.set_ylabel("log(Fluctuation)")
        ax.set_title(
            f'DFA Scaling (JAX Optimized)\nH = {self.results["hurst_parameter"]:.3f}, R² = {self.results["r_squared"]:.3f}'
        )
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        if show:
            plt.show()

        plt.close(fig)
