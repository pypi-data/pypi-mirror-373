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
def _calculate_overlapping_moving_average_numba(
    cumsum: np.ndarray, window_size: int
) -> np.ndarray:
    """
    Calculate overlapping moving average using Numba JIT compilation.

    Parameters
    ----------
    cumsum : np.ndarray
        Cumulative sum of the time series.
    window_size : int
        Size of the moving average window.

    Returns
    -------
    np.ndarray
        Moving average values.
    """
    n = len(cumsum)
    half_window = window_size // 2
    moving_avg = np.zeros_like(cumsum)

    for i in range(n):
        start = max(0, i - half_window)
        end = min(n, i + half_window + 1)
        moving_avg[i] = np.mean(cumsum[start:end])

    return moving_avg


@jit(nopython=True, cache=True)
def _calculate_non_overlapping_moving_average_numba(
    cumsum: np.ndarray, window_size: int
) -> np.ndarray:
    """
    Calculate non-overlapping moving average using Numba JIT compilation.

    Parameters
    ----------
    cumsum : np.ndarray
        Cumulative sum of the time series.
    window_size : int
        Size of the moving average window.

    Returns
    -------
    np.ndarray
        Moving average values.
    """
    n = len(cumsum)
    moving_avg = np.zeros_like(cumsum)

    for i in range(0, n, window_size):
        end = min(i + window_size, n)
        window_mean = np.mean(cumsum[i:end])
        for j in range(i, end):
            moving_avg[j] = window_mean

    return moving_avg


@jit(nopython=True, cache=True)
def _calculate_fluctuation_numba(
    data: np.ndarray, window_size: int, overlap: bool
) -> float:
    """
    Calculate the fluctuation function for a given window size using Numba.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    window_size : int
        Size of the window for DMA calculation.
    overlap : bool
        Whether to use overlapping windows.

    Returns
    -------
    float
        Fluctuation value for the given window size.
    """
    n = len(data)

    # Calculate cumulative sum
    mean_val = np.mean(data)
    cumsum = np.zeros(n)
    cumsum[0] = data[0] - mean_val
    for i in range(1, n):
        cumsum[i] = cumsum[i - 1] + (data[i] - mean_val)

    # Calculate moving average
    if overlap:
        moving_avg = _calculate_overlapping_moving_average_numba(cumsum, window_size)
    else:
        moving_avg = _calculate_non_overlapping_moving_average_numba(
            cumsum, window_size
        )

    # Calculate detrended series
    detrended = cumsum - moving_avg

    # Calculate fluctuation (root mean square)
    sum_squares = 0.0
    for i in range(n):
        sum_squares += detrended[i] ** 2

    fluctuation = np.sqrt(sum_squares / n)

    return fluctuation


@jit(nopython=True, cache=True)
def _calculate_fluctuations_batch_numba(
    data: np.ndarray, window_sizes: np.ndarray, overlap: bool
) -> np.ndarray:
    """
    Calculate fluctuation values for multiple window sizes using Numba JIT compilation.

    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    window_sizes : np.ndarray
        Array of window sizes to calculate fluctuations for.
    overlap : bool
        Whether to use overlapping windows.

    Returns
    -------
    np.ndarray
        Array of fluctuation values for each window size.
    """
    n_windows = len(window_sizes)
    fluctuation_values = np.zeros(n_windows, dtype=np.float64)

    for i in prange(n_windows):
        fluctuation_values[i] = _calculate_fluctuation_numba(
            data, window_sizes[i], overlap
        )

    return fluctuation_values


class DMAEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Detrended Moving Average (DMA) estimator for Hurst parameter.

    This implementation uses Numba JIT compilation for significant CPU performance
    improvements, especially for large datasets and multiple window sizes.

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
    """

    def __init__(
        self,
        min_window_size: int = 4,
        max_window_size: int = None,
        window_sizes: List[int] = None,
        overlap: bool = True,
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

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using Numba-optimized DMA method.

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
            raise ValueError("Data length must be at least 10 for DMA analysis")

        # Determine window sizes
        if self.parameters["window_sizes"] is not None:
            window_sizes = self.parameters["window_sizes"]
        else:
            max_size = self.parameters["max_window_size"]
            if max_size is None:
                max_size = len(data) // 4

            # Generate window sizes (powers of 2 or similar)
            window_sizes = []
            size = self.parameters["min_window_size"]
            while size <= max_size and size <= len(data) // 2:
                window_sizes.append(size)
                size = int(size * 1.5)  # Geometric progression

        if len(window_sizes) < 3:
            raise ValueError("Need at least 3 window sizes for reliable estimation")

        # Convert to numpy array for Numba
        window_sizes_np = np.array(window_sizes, dtype=np.int32)

        # Calculate fluctuation values for each window size using Numba
        fluctuation_values = _calculate_fluctuations_batch_numba(
            data, window_sizes_np, self.parameters["overlap"]
        )

        # Filter out non-positive or non-finite fluctuations before log
        valid_mask = (
            np.isfinite(fluctuation_values)
            & (fluctuation_values > 0)
            & np.isfinite(window_sizes_np)
            & (window_sizes_np > 1)
        )
        valid_sizes = window_sizes_np[valid_mask]
        valid_fluct = fluctuation_values[valid_mask]

        if valid_sizes.size < 3:
            raise ValueError(
                "Insufficient valid fluctuation points for DMA (need >=3 after filtering non-positive values)"
            )

        # Fit power law relationship: log(F) = H * log(n) + c using filtered points
        log_sizes = np.log(valid_sizes.astype(np.float64))
        log_fluctuations = np.log(valid_fluct)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_sizes, log_fluctuations
        )

        # Hurst parameter is the slope
        H = slope

        # Calculate confidence interval
        n_points = len(window_sizes)
        t_critical = stats.t.ppf(0.975, n_points - 2)  # 95% CI
        ci_lower = H - t_critical * std_err
        ci_upper = H + t_critical * std_err

        self.results = {
            "hurst_parameter": H,
            "window_sizes": valid_sizes.tolist(),
            "fluctuation_values": valid_fluct.tolist(),
            "r_squared": r_value**2,
            "std_error": std_err,
            "confidence_interval": (ci_lower, ci_upper),
            "p_value": p_value,
            "intercept": intercept,
            "slope": slope,
            "log_sizes": log_sizes,
            "log_fluctuations": log_fluctuations,
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
        Plot the DMA scaling relationship.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot. If None, displays the plot.
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        window_sizes = self.results["window_sizes"]
        fluctuation_values = self.results["fluctuation_values"]
        H = self.results["hurst_parameter"]
        r_squared = self.results["r_squared"]

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Fluctuation vs window size (log-log)
        log_sizes = np.log(window_sizes)
        log_fluctuations = np.log(fluctuation_values)

        ax1.scatter(
            log_sizes, log_fluctuations, color="blue", alpha=0.7, label="Data points"
        )

        # Plot fitted line
        x_fit = np.array([min(log_sizes), max(log_sizes)])
        y_fit = H * x_fit + self.results["intercept"]
        ax1.plot(
            x_fit,
            y_fit,
            "r--",
            linewidth=2,
            label=f"Fit: H = {H:.3f} (R² = {r_squared:.3f})",
        )

        ax1.set_xlabel("log(Window Size)")
        ax1.set_ylabel("log(Fluctuation)")
        ax1.set_title("DMA Scaling Relationship (Numba)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Fluctuation vs window size (linear scale)
        ax2.scatter(
            window_sizes,
            fluctuation_values,
            color="green",
            alpha=0.7,
            label="Data points",
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
        ax2.set_ylabel("Fluctuation")
        ax2.set_title("Fluctuation vs Window Size")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {save_path}")
        else:
            plt.show()

        plt.close()
