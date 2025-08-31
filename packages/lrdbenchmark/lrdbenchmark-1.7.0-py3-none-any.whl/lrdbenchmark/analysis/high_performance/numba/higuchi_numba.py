import numpy as np
from numba import jit, prange
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, cache=True)
def _calculate_segment_length_numba(
    data: np.ndarray, m: int, k: int, n_m: int, n: int
) -> float:
    """
    Calculate curve length for a specific segment using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
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
    float
        Curve length for this segment.
    """
    total_length = 0.0
    valid_count = 0

    for i in range(n_m):
        idx1 = m + i * k
        idx2 = m + (i + 1) * k

        if idx2 < n:
            # Add the distance between consecutive points
            total_length += abs(data[idx2] - data[idx1])
            valid_count += 1

    # Normalize by the number of intervals
    if valid_count > 0:
        length = total_length * (n - 1) / (k**2 * valid_count)
    else:
        length = 0.0

    return length


@jit(nopython=True, cache=True)
def _calculate_curve_length_numba(data: np.ndarray, k: int) -> float:
    """
    Calculate the average curve length for a given time interval k using Numba.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    k : int
        Time interval for curve length calculation.

    Returns
    -------
    float
        Average curve length across all possible starting points.
    """
    n = len(data)
    total_length = 0.0
    valid_count = 0

    # Calculate curve length for each starting point
    for m in range(k):
        # Number of points in this segment
        n_m = (n - m - 1) // k

        if n_m >= 1:
            # Calculate curve length for this segment
            length = _calculate_segment_length_numba(data, m, k, n_m, n)
            if length > 0:
                total_length += length
                valid_count += 1

    # Return average length
    if valid_count > 0:
        return total_length / valid_count
    else:
        return 0.0


@jit(nopython=True, cache=True)
def _calculate_curve_lengths_batch_numba(
    data: np.ndarray, k_values: np.ndarray
) -> np.ndarray:
    """
    Calculate curve lengths for multiple k values using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    k_values : np.ndarray
        Array of k values to calculate curve lengths for.

    Returns
    -------
    np.ndarray
        Array of curve lengths for each k value.
    """
    n_k = len(k_values)
    curve_lengths = np.zeros(n_k, dtype=np.float64)

    for i in prange(n_k):
        curve_lengths[i] = _calculate_curve_length_numba(data, k_values[i])

    return curve_lengths


class HiguchiEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Higuchi Method estimator for fractal dimension and Hurst parameter.

    This implementation uses Numba JIT compilation for significant CPU performance
    improvements, especially for large datasets and multiple k values.

    Parameters
    ----------
    min_k : int, default=2
        Minimum time interval for curve length calculation.
    max_k : int, optional
        Maximum time interval. If None, uses n/4 where n is data length.
    k_values : List[int], optional
        Specific k values to use. If provided, overrides min/max.
    """

    def __init__(self, min_k: int = 2, max_k: int = None, k_values: List[int] = None):
        super().__init__(min_k=min_k, max_k=max_k, k_values=k_values)
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

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the fractal dimension and Hurst parameter using Numba-optimized Higuchi method.

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

        # Convert to numpy array for Numba
        k_values_np = np.array(k_values, dtype=np.int32)

        # Calculate curve lengths for each k using Numba
        curve_lengths = _calculate_curve_lengths_batch_numba(data, k_values_np)

        # Filter invalid points (non-positive curve lengths)
        valid_mask = (
            np.isfinite(curve_lengths)
            & (curve_lengths > 0)
            & np.isfinite(k_values_np)
            & (k_values_np > 1)
        )
        valid_k = k_values_np[valid_mask]
        valid_lengths = curve_lengths[valid_mask]

        if valid_k.size < 3:
            raise ValueError(
                "Insufficient valid Higuchi points (need >=3 after filtering non-positive values)"
            )

        # Fit power law relationship: log(L) = -D * log(k) + c
        log_k = np.log(valid_k.astype(np.float64))
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
        ax1.set_title("Higuchi Scaling Relationship (Numba)")
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
