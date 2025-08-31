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
def _calculate_rs_window_numba(data: np.ndarray, start_idx: int, scale: int) -> float:
    """
    Calculate R/S statistic for a single window using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    start_idx : int
        Starting index for the window.
    scale : int
        Window size (scale).

    Returns
    -------
    float
        R/S statistic for this window.
    """
    end_idx = start_idx + scale
    window = data[start_idx:end_idx]

    # Calculate mean
    mean_val = 0.0
    for i in range(scale):
        mean_val += window[i]
    mean_val /= scale

    # Calculate cumulative deviation
    cum_dev = np.zeros(scale)
    cum_dev[0] = window[0] - mean_val
    for i in range(1, scale):
        cum_dev[i] = cum_dev[i - 1] + (window[i] - mean_val)

    # Calculate range
    min_val = cum_dev[0]
    max_val = cum_dev[0]
    for i in range(1, scale):
        if cum_dev[i] < min_val:
            min_val = cum_dev[i]
        if cum_dev[i] > max_val:
            max_val = cum_dev[i]
    R = max_val - min_val

    # Calculate standard deviation (sample std)
    sum_sq = 0.0
    for i in range(scale):
        diff = window[i] - mean_val
        sum_sq += diff * diff
    S = np.sqrt(sum_sq / (scale - 1))

    # Return R/S value
    if S > 0:
        return R / S
    else:
        return 0.0


@jit(nopython=True, cache=True)
def _calculate_rs_scale_numba(data: np.ndarray, scale: int) -> float:
    """
    Calculate average R/S statistic for a given scale using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    scale : int
        Window size (scale).

    Returns
    -------
    float
        Average R/S statistic for this scale.
    """
    n = len(data)
    num_windows = n // scale

    if num_windows == 0:
        return 0.0

    total_rs = 0.0
    valid_count = 0

    for i in prange(num_windows):
        start_idx = i * scale
        rs_val = _calculate_rs_window_numba(data, start_idx, scale)
        if rs_val > 0:
            total_rs += rs_val
            valid_count += 1

    if valid_count > 0:
        return total_rs / valid_count
    else:
        return 0.0


@jit(nopython=True, cache=True)
def _calculate_rs_values_batch_numba(
    data: np.ndarray, window_sizes: np.ndarray
) -> np.ndarray:
    """
    Calculate R/S values for multiple window sizes using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    window_sizes : np.ndarray
        Array of window sizes to calculate R/S for.

    Returns
    -------
    np.ndarray
        Array of R/S values for each window size.
    """
    n_scales = len(window_sizes)
    rs_values = np.zeros(n_scales, dtype=np.float64)

    for i in prange(n_scales):
        rs_values[i] = _calculate_rs_scale_numba(data, window_sizes[i])

    return rs_values


class RSEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Rescaled Range (R/S) Analysis estimator for Hurst parameter.

    This implementation uses Numba JIT compilation for significant CPU performance
    improvements, especially for large datasets and multiple window sizes.

    Parameters
    ----------
    min_window_size : int, default=10
        Minimum window size to use.
    max_window_size : int, optional
        Maximum window size. If None, uses n/4 where n is data length.
    window_sizes : List[int], optional
        Specific window sizes to use. If provided, overrides min/max.
    overlap : bool, default=False
        Whether to use overlapping windows.
    """

    def __init__(
        self,
        min_window_size: int = 10,
        max_window_size: int = None,
        window_sizes: List[int] = None,
        overlap: bool = False,
    ):
        super().__init__(
            min_window_size=min_window_size,
            max_window_size=max_window_size,
            window_sizes=window_sizes,
            overlap=overlap,
        )
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
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

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using Numba-optimized R/S analysis.

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
            raise ValueError("Data length must be at least 10 for R/S analysis")

        # Determine window sizes
        if self.parameters["window_sizes"] is not None:
            window_sizes = self.parameters["window_sizes"]
        else:
            max_size = self.parameters["max_window_size"]
            if max_size is None:
                max_size = len(data) // 4

            # Generate window sizes (logarithmic spacing)
            window_sizes = np.logspace(
                np.log10(self.parameters["min_window_size"]),
                np.log10(max_size),
                20,
                dtype=int,
            )
            window_sizes = np.unique(window_sizes)

        if len(window_sizes) < 3:
            raise ValueError("Need at least 3 window sizes for reliable estimation")

        if len(data) < min(window_sizes) * 2:
            raise ValueError(
                f"Data length ({len(data)}) must be at least {min(window_sizes) * 2}"
            )

        # Convert to numpy array for Numba
        window_sizes_np = np.array(window_sizes, dtype=np.int32)

        # Calculate R/S values for each window size using Numba
        rs_values = _calculate_rs_values_batch_numba(data, window_sizes_np)

        # Filter out non-positive R/S values
        valid_mask = np.isfinite(rs_values) & (rs_values > 0)
        valid_sizes = window_sizes_np[valid_mask]
        valid_rs = rs_values[valid_mask]

        if valid_sizes.size < 3:
            raise ValueError("Insufficient valid R/S points (need >=3 after filtering)")

        # Fit power law: R/S ~ scale^H
        log_scales = np.log(valid_sizes.astype(np.float64))
        log_rs = np.log(valid_rs)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_scales, log_rs
        )

        # Hurst parameter is the slope
        H = slope

        # Calculate confidence interval
        n_points = len(valid_sizes)
        t_critical = stats.t.ppf(0.975, n_points - 2)  # 95% CI
        ci_lower = H - t_critical * std_err
        ci_upper = H + t_critical * std_err

        self.results = {
            "hurst_parameter": H,
            "window_sizes": valid_sizes.tolist(),
            "rs_values": valid_rs.tolist(),
            "r_squared": r_value**2,
            "std_error": std_err,
            "confidence_interval": (ci_lower, ci_upper),
            "p_value": p_value,
            "intercept": intercept,
            "slope": slope,
            "log_scales": log_scales,
            "log_rs": log_rs,
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

        # Calculate confidence interval for Hurst parameter
        n_points = len(self.results["window_sizes"])
        t_critical = stats.t.ppf((1 + confidence_level) / 2, n_points - 2)

        H = self.results["hurst_parameter"]
        std_err = self.results["std_error"]

        ci_lower = H - t_critical * std_err
        ci_upper = H + t_critical * std_err

        return {"hurst_parameter": (ci_lower, ci_upper)}

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
            "n_windows": len(self.results["window_sizes"]),
        }

    def plot_scaling(self, save_path: str = None) -> None:
        """
        Plot the R/S scaling relationship.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot. If None, displays the plot.
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        window_sizes = self.results["window_sizes"]
        rs_values = self.results["rs_values"]
        H = self.results["hurst_parameter"]
        r_squared = self.results["r_squared"]

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: R/S vs window size (log-log)
        log_scales = np.log(window_sizes)
        log_rs = np.log(rs_values)

        ax1.scatter(log_scales, log_rs, color="blue", alpha=0.7, label="Data points")

        # Plot fitted line
        x_fit = np.array([min(log_scales), max(log_scales)])
        y_fit = H * x_fit + self.results["intercept"]
        ax1.plot(
            x_fit,
            y_fit,
            "r--",
            linewidth=2,
            label=f"Fit: H = {H:.3f} (R² = {r_squared:.3f})",
        )

        ax1.set_xlabel("log(Window Size)")
        ax1.set_ylabel("log(R/S)")
        ax1.set_title("R/S Scaling Relationship (Numba)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: R/S vs window size (linear scale)
        ax2.scatter(
            window_sizes, rs_values, color="green", alpha=0.7, label="Data points"
        )

        # Plot fitted curve
        x_fit_linear = np.linspace(min(window_sizes), max(window_sizes), 100)
        y_fit_linear = np.exp(self.results["intercept"]) * (x_fit_linear**H)
        ax2.plot(
            x_fit_linear,
            y_fit_linear,
            "r--",
            linewidth=2,
            label=f"Power law fit: H = {H:.3f}",
        )

        ax2.set_xlabel("Window Size")
        ax2.set_ylabel("R/S")
        ax2.set_title("R/S vs Window Size")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Add text box with results
        textstr = f"Hurst Parameter: {H:.3f}\nR²: {r_squared:.3f}"
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
