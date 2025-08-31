import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os
import warnings

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class HiguchiEstimator(BaseEstimator):
    """
    Higuchi Method estimator for fractal dimension and Hurst parameter.

    The Higuchi method is an efficient algorithm for estimating the fractal
    dimension of a time series. It is based on the relationship between the
    length of the curve and the time interval used to measure it.

    The method works by:
    1. Computing the curve length for different time intervals k
    2. Fitting a power law relationship: L(k) ~ k^(-D)
    3. The fractal dimension D is related to the Hurst parameter H by: H = 2 - D

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
        
        # Step 1: Calculate the mean and create Y vector (cumulative sum of differences)
        X_mean = np.mean(data)
        Y = np.zeros(n)
        for i in range(n):
            Y[i] = np.sum(data[:i+1] - X_mean)
        
        # Step 2: Generate k values according to the research paper algorithm
        k_values = []
        n_k = 10  # Number of k values as specified in the paper
        
        for idx in range(1, n_k + 1):
            if idx > 4:
                # For idx > 4: m = floor(2^(idx+5)/4)
                m = int(2**((idx + 5) / 4))
            else:
                # For idx <= 4: m = idx
                m = idx
            
            # Ensure m is not too large
            if m >= n // 2:
                break
                
            k_values.append(m)
        
        if len(k_values) < 3:
            raise ValueError("Insufficient k values generated for Higuchi analysis")
        
        # Step 3: Calculate curve lengths for each k value
        curve_lengths = []
        for k in k_values:
            try:
                length = self._calculate_curve_length_higuchi(Y, k)
                if np.isfinite(length) and length > 0:
                    curve_lengths.append(length)
                else:
                    curve_lengths.append(np.nan)
            except Exception:
                curve_lengths.append(np.nan)
        
        # Step 4: Calculate normalized statistics S according to the paper
        S_values = []
        for i, k in enumerate(k_values):
            if i < len(curve_lengths) and np.isfinite(curve_lengths[i]):
                # S_idx = (N-1) * L_k / m² (equation 51-52 from the paper)
                S = (n - 1) * curve_lengths[i] / (k * k)
                S_values.append(S)
            else:
                S_values.append(np.nan)
        
        # Step 5: Filter valid points and perform linear regression
        S_values = np.array(S_values)
        k_values = np.array(k_values)
        valid_mask = (
            np.isfinite(S_values)
            & (S_values > 0)
            & np.isfinite(k_values)
            & (k_values > 1)
        )
        valid_k = np.array(k_values)[valid_mask]
        valid_S = np.array(S_values)[valid_mask]
        
        if len(valid_S) < 3:
            raise ValueError(
                f"Insufficient valid Higuchi points (need >=3, got {len(valid_S)})"
            )
        
        # Step 6: Linear regression in log-log space
        log_k = np.log(valid_k.astype(float))
        log_S = np.log(valid_S.astype(float))
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_k, log_S
        )
        
        # Step 7: Calculate Hurst parameter according to the paper
        # From the paper: H = β_HM + 2 where β_HM is the slope
        # This means: H = slope + 2
        H = slope + 2
        
        # Validate Hurst parameter range
        if H < -0.5 or H > 1.5:
            warnings.warn(f"Estimated Hurst parameter H={H:.6f} is outside typical range [-0.5, 1.5]")
        
        # Ensure H is within reasonable bounds
        H = np.clip(H, -1.0, 2.0)
        
        # Calculate confidence interval
        n_points = len(valid_S)
        t_critical = stats.t.ppf(0.975, n_points - 2)  # 95% CI
        ci_lower = H - t_critical * std_err
        ci_upper = H + t_critical * std_err
        
        # Store results
        self.results = {
            "hurst_parameter": H,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_error": std_err,
            "confidence_interval": (ci_lower, ci_upper),
            "k_values": valid_k.tolist(),
            "curve_lengths": [curve_lengths[i] for i in range(len(k_values)) if valid_mask[i]],
            "S_values": valid_S.tolist(),
            "log_k": log_k,
            "log_S": log_S,
            "n_points": len(valid_S),
            "method": "Higuchi (Research Paper Implementation)"
        }
        
        return self.results

    def _calculate_curve_length_higuchi(self, Y: np.ndarray, k: int) -> float:
        """
        Calculate curve length using the correct Higuchi method from the research paper.
        
        Parameters
        ----------
        Y : np.ndarray
            Cumulative sum vector Y
        k : int
            Time interval k
            
        Returns
        -------
        float
            Average curve length L_k
        """
        n = len(Y)
        
        # Calculate k segments: k = floor(N/m) where m is the time interval
        num_segments = n // k
        
        if num_segments < 2:
            return np.nan
        
        # Calculate L_k according to the paper:
        # L_k = average over i of (average over j of |Y_{j+m} - Y_j|)
        # where i ranges from 1 to k-1, and j ranges from (i-1)*m+1 to i*m
        
        total_length = 0.0
        valid_segments = 0
        
        for i in range(1, num_segments):
            # For segment i, calculate average of |Y_{j+k} - Y_j|
            segment_length = 0.0
            segment_count = 0
            
            start_idx = (i - 1) * k
            end_idx = i * k
            
            for j in range(start_idx, end_idx):
                if j + k < n:
                    diff = abs(Y[j + k] - Y[j])
                    segment_length += diff
                    segment_count += 1
            
            if segment_count > 0:
                segment_length /= segment_count
                total_length += segment_length
                valid_segments += 1
        
        if valid_segments == 0:
            return np.nan
        
        return total_length / valid_segments

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
        ax1.set_title("Higuchi Scaling Relationship")
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
