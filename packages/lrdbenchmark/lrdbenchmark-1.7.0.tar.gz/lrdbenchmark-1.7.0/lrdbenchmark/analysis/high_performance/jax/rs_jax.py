"""
JAX-optimized Rescaled Range (R/S) Analysis estimator.

This module provides a JAX-optimized version of the R/S estimator for GPU acceleration
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


class RSEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Rescaled Range (R/S) Analysis estimator.

    This version uses JAX for GPU acceleration and improved performance.
    It maintains the same interface as the original R/S estimator but with
    significant performance improvements, especially for large datasets.

    Parameters
    ----------
    min_window_size : int, optional
        Minimum window size for analysis (default: 10)
    max_window_size : int, optional
        Maximum window size for analysis (default: None, will use n/4)
    window_sizes : array-like, optional
        Specific window sizes to use (default: None)
    overlap : bool, optional
        Whether to use overlapping windows (default: False)
    use_gpu : bool, optional
        Whether to use GPU acceleration (default: True)
    """

    def __init__(
        self,
        min_window_size: int = 10,
        max_window_size: int = None,
        window_sizes: List[int] = None,
        overlap: bool = False,
        use_gpu: bool = True,
    ):
        """
        Initialize the JAX-optimized R/S estimator.

        Parameters
        ----------
        min_window_size : int, optional
            Minimum window size for analysis (default: 10)
        max_window_size : int, optional
            Maximum window size for analysis (default: None)
        window_sizes : array-like, optional
            Specific window sizes to use (default: None)
        overlap : bool, optional
            Whether to use overlapping windows (default: False)
        use_gpu : bool, optional
            Whether to use GPU acceleration (default: True)
        """
        super().__init__(
            min_window_size=min_window_size,
            max_window_size=max_window_size,
            window_sizes=window_sizes,
            overlap=overlap,
            use_gpu=use_gpu,
        )

        # Configure JAX for GPU usage
        if use_gpu:
            try:
                # Check if GPU is available
                jax.devices("gpu")
                print("JAX R/S: Using GPU acceleration")
            except RuntimeError:
                print("JAX R/S: GPU not available, using CPU")
                self.parameters["use_gpu"] = False
        else:
            print("JAX R/S: Using CPU (GPU disabled)")

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_window_size = self.parameters["min_window_size"]
        max_window_size = self.parameters["max_window_size"]

        if min_window_size < 3:
            raise ValueError("min_window_size must be at least 3")

        if max_window_size is not None and max_window_size <= min_window_size:
            raise ValueError("max_window_size must be greater than min_window_size")

    @staticmethod
    @jit
    def _calculate_rs_jax(window: jnp.ndarray) -> jnp.ndarray:
        """
        JAX-optimized calculation of R/S statistic for a window.

        Parameters
        ----------
        window : jnp.ndarray
            Data window to analyze

        Returns
        -------
        jnp.ndarray
            R/S statistic
        """
        n = len(window)

        # Calculate mean
        mean_val = jnp.mean(window)

        # Calculate cumulative deviation
        dev = window - mean_val
        cumdev = jnp.cumsum(dev)

        # Calculate R (range)
        R = jnp.max(cumdev) - jnp.min(cumdev)

        # Calculate S (standard deviation)
        S = jnp.std(window, ddof=1)  # Sample standard deviation

        # Avoid division by zero
        S = jnp.where(S == 0, jnp.inf, S)

        # Calculate R/S statistic
        rs_stat = R / S

        return rs_stat

    @staticmethod
    def _calculate_rs_batch(
        data: jnp.ndarray, window_sizes: jnp.ndarray, overlap: bool
    ) -> jnp.ndarray:
        """
        JAX-optimized batch calculation of R/S statistics for multiple window sizes.

        Parameters
        ----------
        data : jnp.ndarray
            Time series data
        window_sizes : jnp.ndarray
            Array of window sizes to analyze
        overlap : bool
            Whether to use overlapping windows

        Returns
        -------
        jnp.ndarray
            Array of mean R/S statistics for each window size
        """
        n = len(data)
        rs_stats = []

        for window_size in window_sizes:
            if window_size > n:
                rs_stats.append(jnp.nan)
                continue

            if overlap:
                # Overlapping windows
                n_windows = n - window_size + 1
                step = 1
            else:
                # Non-overlapping windows
                n_windows = n // window_size
                step = window_size

            if n_windows == 0:
                rs_stats.append(jnp.nan)
                continue

            # Create windows and calculate R/S statistics
            window_rs_stats = []
            for i in range(n_windows):
                start_idx = i * step
                end_idx = start_idx + window_size
                if end_idx <= n:
                    window = data[start_idx:end_idx]
                    rs_stat = RSEstimatorJAX._calculate_rs_jax(window)
                    window_rs_stats.append(rs_stat)

            if window_rs_stats:
                # Return mean R/S statistic
                mean_rs = jnp.mean(jnp.array(window_rs_stats))
                rs_stats.append(mean_rs)
            else:
                rs_stats.append(jnp.nan)

        return jnp.array(rs_stats)

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using JAX-optimized R/S analysis.

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

        # Determine window sizes
        if self.parameters["window_sizes"] is not None:
            window_sizes = jnp.array(self.parameters["window_sizes"], dtype=jnp.int32)
        else:
            min_size = self.parameters["min_window_size"]
            max_size = self.parameters["max_window_size"] or n // 4

            # Create window sizes with approximately equal spacing in log space
            window_sizes = jnp.unique(
                jnp.logspace(
                    jnp.log10(min_size),
                    jnp.log10(max_size),
                    num=min(20, max_size - min_size + 1),
                    dtype=jnp.int32,
                )
            )

        # Filter window sizes that are too large
        valid_mask = window_sizes <= n
        window_sizes = window_sizes[valid_mask]

        if len(window_sizes) < 3:
            raise ValueError("Need at least 3 window sizes for R/S analysis")

        # Calculate R/S statistics using JAX
        overlap = self.parameters["overlap"]
        rs_stats = self._calculate_rs_batch(data_jax, window_sizes, overlap)

        # Filter out invalid results
        valid_mask = jnp.isfinite(rs_stats) & (rs_stats > 0)
        valid_window_sizes = window_sizes[valid_mask]
        valid_rs_stats = rs_stats[valid_mask]

        if len(valid_rs_stats) < 3:
            raise ValueError("Insufficient valid R/S statistics for analysis")

        # Linear regression in log-log space
        log_sizes = jnp.log(valid_window_sizes.astype(jnp.float32))
        log_rs = jnp.log(valid_rs_stats.astype(jnp.float32))

        # Use JAX's linear algebra for regression
        X = jnp.column_stack([log_sizes, jnp.ones_like(log_sizes)])
        coeffs, residuals, rank, s = jnp.linalg.lstsq(X, log_rs, rcond=None)

        slope = coeffs[0]
        intercept = coeffs[1]

        # Calculate R-squared
        y_pred = X @ coeffs
        ss_res = jnp.sum((log_rs - y_pred) ** 2)
        ss_tot = jnp.sum((log_rs - jnp.mean(log_rs)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        # Calculate standard error
        n_points = len(log_rs)
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
            "window_sizes": valid_window_sizes.tolist(),
            "rs_statistics": valid_rs_stats.tolist(),
            "log_sizes": log_sizes.tolist(),
            "log_rs": log_rs.tolist(),
            "slope": float(slope),
            "n_points": int(n_points),
            "n_windows": len(valid_rs_stats),
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
            "p_value": self.results["p_value"],
            "n_windows": self.results["n_windows"],
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
            self.results["log_rs"],
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

        ax.set_xlabel("log(Window Size)")
        ax.set_ylabel("log(R/S)")
        ax.set_title(
            f'R/S Scaling (JAX Optimized)\nH = {self.results["hurst_parameter"]:.3f}, R² = {self.results["r_squared"]:.3f}'
        )
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        if show:
            plt.show()

        plt.close(fig)
