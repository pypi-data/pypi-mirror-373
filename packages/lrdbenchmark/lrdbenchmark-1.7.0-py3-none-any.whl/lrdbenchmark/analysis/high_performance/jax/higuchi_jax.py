import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class HiguchiEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Higuchi Method estimator for fractal dimension and Hurst parameter.

    This implementation uses JAX for GPU acceleration and vectorized computations,
    providing significant performance improvements for large datasets.

    Parameters
    ----------
    min_k : int, default=2
        Minimum time interval for curve length calculation.
    max_k : int, optional
        Maximum time interval. If None, uses n/4 where n is data length.
    k_values : List[int], optional
        Specific k values to use. If provided, overrides min/max.
    use_gpu : bool, default=False
        Whether to use GPU acceleration if available.
    """

    def __init__(
        self,
        min_k: int = 2,
        max_k: int = None,
        k_values: List[int] = None,
        use_gpu: bool = False,
    ):
        super().__init__(min_k=min_k, max_k=max_k, k_values=k_values, use_gpu=use_gpu)
        self._validate_parameters()
        self._setup_jax()

    def _setup_jax(self) -> None:
        """Setup JAX configuration for GPU acceleration if requested."""
        if self.parameters["use_gpu"]:
            try:
                # Check if GPU is available
                devices = jax.devices()
                gpu_devices = [d for d in devices if d.platform == "gpu"]
                if gpu_devices:
                    print(f"Using GPU acceleration with {len(gpu_devices)} device(s)")
                    # Set default device to first GPU
                    jax.config.update("jax_platform_name", "gpu")
                else:
                    print("GPU requested but not available, falling back to CPU")
                    self.parameters["use_gpu"] = False
            except Exception as e:
                print(f"GPU setup failed: {e}, falling back to CPU")
                self.parameters["use_gpu"] = False

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

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the fractal dimension and Hurst parameter using JAX-optimized Higuchi method.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing estimation results.
        """
        if len(data) < 10:
            raise ValueError("Data length must be at least 10 for Higuchi method")

        # Convert to JAX array
        data_jax = jnp.array(data, dtype=jnp.float32)

        # Determine k values
        if self.parameters["k_values"] is not None:
            k_values = self.parameters["k_values"]
        else:
            max_k = self.parameters["max_k"]
            if max_k is None:
                max_k = len(data) // 4

            # Generate k values (typically powers of 2 or similar)
            k_values = []
            k = self.parameters["min_k"]
            while k <= max_k and k <= len(data) // 2:
                k_values.append(k)
                k = int(k * 1.5)  # Geometric progression

        if len(k_values) < 3:
            raise ValueError("Need at least 3 k values for reliable estimation")

        # Calculate curve lengths for each k using JAX
        curve_lengths = self._calculate_curve_lengths_batch(data_jax, k_values)

        # Convert back to numpy for statistical analysis
        curve_lengths_np = np.array(curve_lengths)
        k_values_np = np.array(k_values, dtype=float)

        # Filter invalid points (non-positive curve lengths)
        valid_mask = (
            np.isfinite(curve_lengths_np)
            & (curve_lengths_np > 0)
            & np.isfinite(k_values_np)
            & (k_values_np > 1)
        )
        valid_k = k_values_np[valid_mask]
        valid_lengths = curve_lengths_np[valid_mask]

        if valid_k.size < 3:
            raise ValueError(
                "Insufficient valid Higuchi points (need >=3 after filtering non-positive values)"
            )

        # Fit power law relationship: log(L) = -D * log(k) + c
        log_k = np.log(valid_k)
        log_lengths = np.log(valid_lengths)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_k, log_lengths
        )

        # Fractal dimension is the negative of the slope
        D = -slope

        # Hurst parameter: H = 2 - D
        H = 2 - D

        # Calculate confidence interval for fractal dimension
        n_points = len(k_values)
        t_critical = stats.t.ppf(0.975, n_points - 2)  # 95% CI
        ci_lower = D - t_critical * std_err
        ci_upper = D + t_critical * std_err

        self.results = {
            "fractal_dimension": D,
            "hurst_parameter": H,
            "k_values": valid_k.tolist(),
            "curve_lengths": valid_lengths.tolist(),
            "r_squared": r_value**2,
            "std_error": std_err,
            "confidence_interval": (ci_lower, ci_upper),
            "p_value": p_value,
            "intercept": intercept,
            "slope": slope,
            "log_k": log_k,
            "log_lengths": log_lengths,
        }

        return self.results

    def _calculate_curve_lengths_batch(
        self, data: jnp.ndarray, k_values: List[int]
    ) -> List[float]:
        """
        Calculate curve lengths for multiple k values using JAX vectorization.

        Parameters
        ----------
        data : jnp.ndarray
            Input time series data as JAX array.
        k_values : List[int]
            List of k values to calculate curve lengths for.

        Returns
        -------
        List[float]
            List of curve lengths for each k value.
        """
        curve_lengths = []
        for k in k_values:
            length = self._calculate_curve_length_jax(data, k)
            curve_lengths.append(float(length))
        return curve_lengths

    def _calculate_curve_length_jax(self, data: jnp.ndarray, k: int) -> jnp.ndarray:
        """
        Calculate the average curve length for a given time interval k using JAX.

        Parameters
        ----------
        data : jnp.ndarray
            Input time series data as JAX array.
        k : int
            Time interval for curve length calculation.

        Returns
        -------
        jnp.ndarray
            Average curve length across all possible starting points.
        """
        n = len(data)
        lengths = []

        # Calculate curve length for each starting point
        for m in range(k):
            # Number of points in this segment
            n_m = (n - m - 1) // k

            if n_m < 1:
                continue

            # Calculate curve length for this segment using JAX
            length = self._calculate_segment_length_jax(data, m, k, n_m, n)
            lengths.append(length)

        # Return average length
        if not lengths:
            raise ValueError(f"No valid curve lengths calculated for k = {k}")

        return jnp.mean(jnp.array(lengths))

    def _calculate_segment_length_jax(
        self, data: jnp.ndarray, m: int, k: int, n_m: int, n: int
    ) -> jnp.ndarray:
        """
        Calculate curve length for a specific segment using JAX vectorization.

        Parameters
        ----------
        data : jnp.ndarray
            Input time series data.
        m : int
            Starting point index.
        k : int
            Time interval.
        n_m : int
            Number of points in this segment.
        n : int
            Total data length.

        Returns
        -------
        jnp.ndarray
            Curve length for this segment.
        """
        # Create indices for the segment
        indices1 = jnp.arange(n_m) * k + m
        indices2 = (jnp.arange(n_m) + 1) * k + m

        # Ensure indices2 doesn't exceed data length
        valid_mask = indices2 < n

        if not jnp.any(valid_mask):
            return jnp.array(0.0)

        # Get valid indices
        valid_indices1 = indices1[valid_mask]
        valid_indices2 = indices2[valid_mask]

        # Calculate distances between consecutive points
        distances = jnp.abs(data[valid_indices2] - data[valid_indices1])

        # Sum distances
        total_length = jnp.sum(distances)

        # Normalize by the number of intervals
        if jnp.sum(valid_mask) > 0:
            length = total_length * (n - 1) / (k**2 * jnp.sum(valid_mask))
        else:
            length = jnp.array(0.0)

        return length

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for the estimated parameters.

        Parameters
        ----------
        confidence_level : float, default=0.95
            Confidence level for the intervals.

        Returns
        -------
        Dict[str, Tuple[float, float]]
            Dictionary containing confidence intervals.
        """
        if not self.results:
            return {}

        # Calculate confidence interval for fractal dimension
        n_points = len(self.results["k_values"])
        t_critical = stats.t.ppf((1 + confidence_level) / 2, n_points - 2)

        D = self.results["fractal_dimension"]
        std_err = self.results["std_error"]

        ci_lower_D = D - t_critical * std_err
        ci_upper_D = D + t_critical * std_err

        # Convert to Hurst parameter confidence interval
        ci_upper_H = 2 - ci_lower_D  # Note the reversal due to H = 2 - D
        ci_lower_H = 2 - ci_upper_D

        return {
            "fractal_dimension": (ci_lower_D, ci_upper_D),
            "hurst_parameter": (ci_lower_H, ci_upper_H),
        }

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the estimation.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing quality metrics.
        """
        if not self.results:
            return {}

        return {
            "r_squared": self.results["r_squared"],
            "p_value": self.results["p_value"],
            "std_error": self.results["std_error"],
            "n_k_values": len(self.results["k_values"]),
        }

    def plot_scaling(self, save_path: str = None) -> None:
        """
        Plot the Higuchi scaling relationship.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot. If None, displays the plot.
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        k_values = self.results["k_values"]
        curve_lengths = self.results["curve_lengths"]
        D = self.results["fractal_dimension"]
        H = self.results["hurst_parameter"]
        r_squared = self.results["r_squared"]

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Curve length vs k (log-log)
        log_k = np.log(k_values)
        log_lengths = np.log(curve_lengths)

        ax1.scatter(log_k, log_lengths, color="blue", alpha=0.7, label="Data points")

        # Plot fitted line
        x_fit = np.array([min(log_k), max(log_k)])
        y_fit = -D * x_fit + self.results["intercept"]
        ax1.plot(
            x_fit,
            y_fit,
            "r--",
            linewidth=2,
            label=f"Fit: D = {D:.3f} (R² = {r_squared:.3f})",
        )

        ax1.set_xlabel("log(k)")
        ax1.set_ylabel("log(Curve Length)")
        ax1.set_title("Higuchi Scaling Relationship (JAX)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Curve length vs k (linear scale)
        ax2.scatter(
            k_values, curve_lengths, color="green", alpha=0.7, label="Data points"
        )

        # Plot fitted curve
        x_fit_linear = np.linspace(min(k_values), max(k_values), 100)
        y_fit_linear = np.exp(self.results["intercept"]) * (x_fit_linear ** (-D))
        ax2.plot(
            x_fit_linear,
            y_fit_linear,
            "r--",
            linewidth=2,
            label=f"Power law fit: D = {D:.3f}",
        )

        ax2.set_xlabel("Time Interval k")
        ax2.set_ylabel("Curve Length")
        ax2.set_title("Curve Length vs Time Interval")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Add text box with results
        textstr = (
            f"Fractal Dimension: {D:.3f}\nHurst Parameter: {H:.3f}\nR²: {r_squared:.3f}"
        )
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        ax2.text(
            0.05,
            0.95,
            textstr,
            transform=ax2.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=props,
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {save_path}")
        else:
            plt.show()

        plt.close()
