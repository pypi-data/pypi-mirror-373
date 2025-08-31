"""
Multifractal Detrended Fluctuation Analysis (MFDFA) Estimator.

This module implements MFDFA for estimating multifractal properties
of time series data, including the generalized Hurst exponent.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
from scipy.signal import detrend
import warnings

# Add parent directory to path for imports
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)

from models.estimators.base_estimator import BaseEstimator


class MFDFAEstimator(BaseEstimator):
    """
    Multifractal Detrended Fluctuation Analysis (MFDFA) estimator.

    MFDFA extends DFA to analyze multifractal properties by computing
    fluctuation functions for different moments q.
    """

    def __init__(
        self,
        q_values: Optional[List[float]] = None,
        scales: Optional[List[int]] = None,
        min_scale: int = 8,
        max_scale: int = 50,
        num_scales: int = 15,
        order: int = 1,
        **kwargs,
    ):
        """
        Initialize MFDFA estimator.

        Parameters
        ----------
        q_values : list of float, optional
            List of q values for multifractal analysis. Default: [-5, -3, -1, 0, 1, 3, 5]
        scales : list of int, optional
            List of scales for analysis. If None, will be generated from min_scale to max_scale
        min_scale : int, default=10
            Minimum scale for analysis
        max_scale : int, default=100
            Maximum scale for analysis
        num_scales : int, default=20
            Number of scales to use if scales is None
        order : int, default=1
            Order of polynomial for detrending
        **kwargs : dict
            Additional parameters
        """
        if q_values is None:
            q_values = [-5, -3, -1, 0, 1, 2, 3, 5]

        if scales is None:
            scales = np.logspace(
                np.log10(min_scale), np.log10(max_scale), num_scales, dtype=int
            )

        super().__init__(
            q_values=q_values,
            scales=scales,
            min_scale=min_scale,
            max_scale=max_scale,
            num_scales=num_scales,
            order=order,
            **kwargs,
        )

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not isinstance(self.parameters["q_values"], (list, np.ndarray)):
            raise ValueError("q_values must be a list or array")

        if not isinstance(self.parameters["scales"], (list, np.ndarray)):
            raise ValueError("scales must be a list or array")

        if self.parameters["order"] < 0:
            raise ValueError("order must be non-negative")

        if self.parameters["min_scale"] <= 0:
            raise ValueError("min_scale must be positive")

        if self.parameters["max_scale"] <= self.parameters["min_scale"]:
            raise ValueError("max_scale must be greater than min_scale")

    def _detrend_series(self, series: np.ndarray, scale: int, order: int) -> np.ndarray:
        """
        Detrend a series segment using polynomial fitting.

        Parameters
        ----------
        series : np.ndarray
            Series segment to detrend
        scale : int
            Scale of the segment
        order : int
            Order of polynomial for detrending

        Returns
        -------
        np.ndarray
            Detrended series
        """
        if order == 0:
            return series - np.mean(series)
        else:
            x = np.arange(scale)
            coeffs = np.polyfit(x, series, order)
            trend = np.polyval(coeffs, x)
            return series - trend

    def _compute_fluctuation_function(
        self, data: np.ndarray, q: float, scale: int
    ) -> float:
        """
        Compute fluctuation function for a given q and scale.

        Parameters
        ----------
        data : np.ndarray
            Time series data
        q : float
            Moment order
        scale : int
            Scale for analysis

        Returns
        -------
        float
            Fluctuation function value
        """
        n_segments = len(data) // scale
        if n_segments == 0:
            return np.nan

        # Reshape data into segments
        segments = data[: n_segments * scale].reshape(n_segments, scale)

        # Compute variance for each segment
        variances = []
        for segment in segments:
            detrended = self._detrend_series(segment, scale, self.parameters["order"])
            variance = np.mean(detrended**2)
            variances.append(variance)

        # Compute q-th order fluctuation function
        if q == 0:
            # Special case for q = 0
            fq = np.exp(0.5 * np.mean(np.log(variances)))
        else:
            fq = np.mean(np.array(variances) ** (q / 2)) ** (1 / q)

        return fq

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate multifractal properties using MFDFA.

        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing:
            - 'hurst_parameter': Estimated Hurst exponent (q=2)
            - 'generalized_hurst': Dictionary of generalized Hurst exponents for each q
            - 'multifractal_spectrum': Dictionary with f(alpha) and alpha values
            - 'scales': List of scales used
            - 'q_values': List of q values used
            - 'fluctuation_functions': Dictionary of Fq(s) for each q
        """
        # Adjust scales for data length
        max_safe_scale = min(self.parameters["max_scale"], len(data) // 4)
        if max_safe_scale < self.parameters["min_scale"]:
            raise ValueError(f"Data length {len(data)} is too short for MFDFA analysis")
        
        # Update scales if needed
        if max_safe_scale < self.parameters["max_scale"]:
            safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
            if len(safe_scales) >= 3:
                self.parameters["scales"] = np.array(safe_scales)
                self.parameters["max_scale"] = max_safe_scale
            else:
                warnings.warn(
                    f"Data length ({len(data)}) may be too short for reliable MFDFA analysis"
                )

        scales = self.parameters["scales"]
        q_values = self.parameters["q_values"]

        # Compute fluctuation functions for all q and scales
        fluctuation_functions = {}
        for q in q_values:
            fq_values = []
            for scale in scales:
                fq = self._compute_fluctuation_function(data, q, scale)
                fq_values.append(fq)
            fluctuation_functions[q] = np.array(fq_values)

        # Fit power law for each q to get generalized Hurst exponents
        generalized_hurst = {}
        log_scales = np.log(scales)

        for q in q_values:
            fq_vals = fluctuation_functions[q]
            valid_mask = ~np.isnan(fq_vals) & (fq_vals > 0)

            if np.sum(valid_mask) < 3:
                generalized_hurst[q] = np.nan
                continue

            log_fq = np.log(fq_vals[valid_mask])
            log_s = log_scales[valid_mask]

            try:
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    log_s, log_fq
                )
                generalized_hurst[q] = slope
            except (ValueError, np.linalg.LinAlgError):
                generalized_hurst[q] = np.nan

        # Extract standard Hurst exponent (q=2)
        hurst_parameter = generalized_hurst.get(2, np.nan)

        # Compute multifractal spectrum if we have enough q values
        multifractal_spectrum = self._compute_multifractal_spectrum(
            generalized_hurst, q_values
        )

        # Store results
        self.results = {
            "hurst_parameter": hurst_parameter,
            "generalized_hurst": generalized_hurst,
            "multifractal_spectrum": multifractal_spectrum,
            "scales": scales.tolist() if hasattr(scales, "tolist") else list(scales),
            "q_values": q_values,
            "fluctuation_functions": {
                q: fq.tolist() if hasattr(fq, "tolist") else list(fq)
                for q, fq in fluctuation_functions.items()
            },
        }

        return self.results

    def _compute_multifractal_spectrum(
        self, generalized_hurst: Dict[float, float], q_values: List[float]
    ) -> Dict[str, List[float]]:
        """
        Compute the multifractal spectrum f(alpha) vs alpha.

        Parameters
        ----------
        generalized_hurst : dict
            Dictionary of generalized Hurst exponents
        q_values : list
            List of q values used

        Returns
        -------
        dict
            Dictionary with 'alpha' and 'f_alpha' values
        """
        # Filter out NaN values
        valid_q = [
            q for q in q_values if not np.isnan(generalized_hurst.get(q, np.nan))
        ]
        valid_h = [generalized_hurst[q] for q in valid_q]

        if len(valid_q) < 3:
            return {"alpha": [], "f_alpha": []}

        # Compute alpha and f(alpha) using Legendre transform
        alpha = []
        f_alpha = []

        for i in range(1, len(valid_q) - 1):
            # Compute alpha as derivative of h(q)
            dq = valid_q[i + 1] - valid_q[i - 1]
            dh = valid_h[i + 1] - valid_h[i - 1]
            alpha_val = valid_h[i] + valid_q[i] * (dh / dq)

            # Compute f(alpha) using Legendre transform
            f_alpha_val = valid_q[i] * alpha_val - valid_h[i]

            alpha.append(alpha_val)
            f_alpha.append(f_alpha_val)

        return {"alpha": alpha, "f_alpha": f_alpha}

    def get_confidence_interval(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for estimated parameters.

        Parameters
        ----------
        confidence_level : float, default=0.95
            Confidence level for intervals

        Returns
        -------
        dict
            Dictionary with confidence intervals for each parameter
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # For now, return simple intervals based on standard error
        # In practice, this would use bootstrap or other statistical methods
        hurst = self.results.get("hurst_parameter", np.nan)

        if np.isnan(hurst):
            return {"hurst_parameter": (np.nan, np.nan)}

        # Simple confidence interval (would need proper statistical analysis)
        std_err = 0.05  # Placeholder
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        margin = z_score * std_err

        return {"hurst_parameter": (max(0, hurst - margin), min(1, hurst + margin))}

    def plot_analysis(
        self, data: np.ndarray, figsize: Tuple[int, int] = (15, 10)
    ) -> None:
        """
        Plot MFDFA analysis results.

        Parameters
        ----------
        data : np.ndarray
            Original time series data
        figsize : tuple, default=(15, 10)
            Figure size
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=figsize)

        # Plot 1: Original time series
        axes[0, 0].plot(data, alpha=0.7)
        axes[0, 0].set_title("Original Time Series")
        axes[0, 0].set_xlabel("Time")
        axes[0, 0].set_ylabel("Value")
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Fluctuation functions
        scales = self.results["scales"]
        for q, fq_vals in self.results["fluctuation_functions"].items():
            valid_mask = ~np.isnan(fq_vals) & (np.array(fq_vals) > 0)
            if np.any(valid_mask):
                axes[0, 1].loglog(
                    np.array(scales)[valid_mask],
                    np.array(fq_vals)[valid_mask],
                    "o-",
                    label=f"q={q}",
                    alpha=0.7,
                )

        axes[0, 1].set_title("Fluctuation Functions Fq(s)")
        axes[0, 1].set_xlabel("Scale s")
        axes[0, 1].set_ylabel("Fq(s)")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Generalized Hurst exponents
        q_vals = list(self.results["generalized_hurst"].keys())
        h_vals = list(self.results["generalized_hurst"].values())
        valid_mask = ~np.isnan(h_vals)

        if np.any(valid_mask):
            axes[1, 0].plot(
                np.array(q_vals)[valid_mask],
                np.array(h_vals)[valid_mask],
                "o-",
                alpha=0.7,
            )
            axes[1, 0].axhline(
                y=0.5, color="r", linestyle="--", alpha=0.5, label="H=0.5"
            )

        axes[1, 0].set_title("Generalized Hurst Exponents h(q)")
        axes[1, 0].set_xlabel("q")
        axes[1, 0].set_ylabel("h(q)")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Plot 4: Multifractal spectrum
        spectrum = self.results["multifractal_spectrum"]
        if spectrum["alpha"] and spectrum["f_alpha"]:
            axes[1, 1].plot(spectrum["alpha"], spectrum["f_alpha"], "o-", alpha=0.7)
            axes[1, 1].set_title("Multifractal Spectrum f(α)")
            axes[1, 1].set_xlabel("α")
            axes[1, 1].set_ylabel("f(α)")
            axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def get_results_summary(self) -> str:
        """
        Get a summary of the estimation results.

        Returns
        -------
        str
            Summary string
        """
        if not self.results:
            return "No estimation results available."

        hurst = self.results.get("hurst_parameter", np.nan)
        generalized_hurst = self.results.get("generalized_hurst", {})

        summary = f"MFDFA Analysis Results:\n"
        summary += f"Hurst Parameter (q=2): {hurst:.4f}\n"
        summary += f"Generalized Hurst Exponents:\n"

        for q, h in generalized_hurst.items():
            if not np.isnan(h):
                summary += f"  h({q}) = {h:.4f}\n"

        return summary
