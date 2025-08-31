"""
Multifractal Wavelet Leaders Estimator.

This module implements Multifractal Wavelet Leaders analysis for estimating
multifractal properties of time series data using wavelet leaders.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
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


class MultifractalWaveletLeadersEstimator(BaseEstimator):
    """
    Multifractal Wavelet Leaders estimator.

    This estimator uses wavelet leaders to analyze multifractal properties
    of time series data, providing robust estimates of the multifractal spectrum.
    """

    def __init__(
        self,
        wavelet: str = "db4",
        scales: Optional[List[int]] = None,
        min_scale: int = 2,
        max_scale: int = 32,
        num_scales: int = 10,
        q_values: Optional[List[float]] = None,
        **kwargs,
    ):
        """
        Initialize Multifractal Wavelet Leaders estimator.

        Parameters
        ----------
        wavelet : str, default='db4'
            Wavelet to use for analysis
        scales : list of int, optional
            List of scales for analysis. If None, will be generated from min_scale to max_scale
        min_scale : int, default=4
            Minimum scale for analysis
        max_scale : int, default=64
            Maximum scale for analysis
        num_scales : int, default=15
            Number of scales to use if scales is None
        q_values : list of float, optional
            List of q values for multifractal analysis. Default: [-5, -3, -1, 0, 1, 3, 5]
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
            wavelet=wavelet,
            scales=scales,
            min_scale=min_scale,
            max_scale=max_scale,
            num_scales=num_scales,
            q_values=q_values,
            **kwargs,
        )

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not isinstance(self.parameters["wavelet"], str):
            raise ValueError("wavelet must be a string")

        if not isinstance(self.parameters["scales"], (list, np.ndarray)):
            raise ValueError("scales must be a list or array")

        if not isinstance(self.parameters["q_values"], (list, np.ndarray)):
            raise ValueError("q_values must be a list or array")

        if self.parameters["min_scale"] <= 0:
            raise ValueError("min_scale must be positive")

        if self.parameters["max_scale"] <= self.parameters["min_scale"]:
            raise ValueError("max_scale must be greater than min_scale")

    def _compute_wavelet_coefficients(self, data: np.ndarray, scale: int) -> np.ndarray:
        """
        Compute wavelet coefficients at a given scale.

        Parameters
        ----------
        data : np.ndarray
            Time series data
        scale : int
            Scale for wavelet analysis

        Returns
        -------
        np.ndarray
            Wavelet coefficients
        """
        try:
            import pywt
        except ImportError:
            raise ImportError("pywt (PyWavelets) is required for wavelet analysis")

        # Compute wavelet coefficients
        coeffs = pywt.wavedec(data, self.parameters["wavelet"], level=scale)

        # Return detail coefficients at the specified scale
        if scale <= len(coeffs) - 1:
            return coeffs[scale]
        else:
            # If scale is too large, use the highest available level
            return coeffs[-1]

    def _compute_wavelet_leaders(self, data: np.ndarray, scale: int) -> np.ndarray:
        """
        Compute wavelet leaders at a given scale.

        Parameters
        ----------
        data : np.ndarray
            Time series data
        scale : int
            Scale for analysis

        Returns
        -------
        np.ndarray
            Wavelet leaders
        """
        try:
            import pywt
        except ImportError:
            raise ImportError("pywt (PyWavelets) is required for wavelet analysis")

        # Compute wavelet coefficients at multiple scales
        coeffs = pywt.wavedec(data, self.parameters["wavelet"], level=min(scale, 8))

        # For wavelet leaders, we need coefficients at the current scale and finer scales
        if scale <= len(coeffs) - 1:
            current_coeffs = coeffs[scale]
        else:
            current_coeffs = coeffs[-1]

        # Compute wavelet leaders as the maximum of coefficients at current and finer scales
        leaders = np.zeros_like(current_coeffs)

        for i in range(len(current_coeffs)):
            # Find the maximum absolute coefficient value across scales for this position
            max_val = 0
            for j in range(min(scale + 1, len(coeffs))):
                if i < len(coeffs[j]):
                    max_val = max(max_val, abs(coeffs[j][i]))
            leaders[i] = max_val

        return leaders

    def _compute_structure_functions(
        self, data: np.ndarray, q: float, scale: int
    ) -> float:
        """
        Compute structure function for a given q and scale.

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
            Structure function value
        """
        leaders = self._compute_wavelet_leaders(data, scale)

        # Remove zeros to avoid log(0)
        valid_leaders = leaders[leaders > 0]

        if len(valid_leaders) == 0:
            return np.nan

        # Compute q-th order structure function
        if q == 0:
            # Special case for q = 0
            sq = np.exp(np.mean(np.log(valid_leaders)))
        else:
            sq = np.mean(valid_leaders**q) ** (1 / q)

        return sq

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate multifractal properties using Wavelet Leaders.

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
            - 'structure_functions': Dictionary of Sq(j) for each q
        """
        # Adjust scales for data length
        max_safe_scale = min(self.parameters["max_scale"], len(data) // 8)
        if max_safe_scale < self.parameters["min_scale"]:
            raise ValueError(f"Data length {len(data)} is too short for wavelet leaders analysis")
        
        # Update scales if needed
        if max_safe_scale < self.parameters["max_scale"]:
            safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
            if len(safe_scales) >= 3:
                self.parameters["scales"] = np.array(safe_scales)
                self.parameters["max_scale"] = max_safe_scale
            else:
                warnings.warn(
                    f"Data length ({len(data)}) may be too short for reliable wavelet leaders analysis"
                )

        scales = self.parameters["scales"]
        q_values = self.parameters["q_values"]

        # Compute structure functions for all q and scales
        structure_functions = {}
        for q in q_values:
            sq_values = []
            for scale in scales:
                sq = self._compute_structure_functions(data, q, scale)
                sq_values.append(sq)
            structure_functions[q] = np.array(sq_values)

        # Fit power law for each q to get generalized Hurst exponents
        generalized_hurst = {}
        log_scales = np.log(scales)

        for q in q_values:
            sq_vals = structure_functions[q]
            valid_mask = ~np.isnan(sq_vals) & (sq_vals > 0)

            if np.sum(valid_mask) < 3:
                generalized_hurst[q] = np.nan
                continue

            log_sq = np.log(sq_vals[valid_mask])
            log_j = log_scales[valid_mask]

            try:
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    log_j, log_sq
                )
                generalized_hurst[q] = slope
            except (ValueError, np.linalg.LinAlgError):
                generalized_hurst[q] = np.nan

        # Extract standard Hurst exponent (q=2)
        hurst_parameter = generalized_hurst.get(2, np.nan)

        # Compute multifractal spectrum
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
            "structure_functions": {
                q: sq.tolist() if hasattr(sq, "tolist") else list(sq)
                for q, sq in structure_functions.items()
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
        Plot Multifractal Wavelet Leaders analysis results.

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

        # Plot 2: Structure functions
        scales = self.results["scales"]
        for q, sq_vals in self.results["structure_functions"].items():
            valid_mask = ~np.isnan(sq_vals) & (np.array(sq_vals) > 0)
            if np.any(valid_mask):
                axes[0, 1].loglog(
                    np.array(scales)[valid_mask],
                    np.array(sq_vals)[valid_mask],
                    "o-",
                    label=f"q={q}",
                    alpha=0.7,
                )

        axes[0, 1].set_title("Structure Functions Sq(j)")
        axes[0, 1].set_xlabel("Scale j")
        axes[0, 1].set_ylabel("Sq(j)")
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

        summary = f"Multifractal Wavelet Leaders Analysis Results:\n"
        summary += f"Hurst Parameter (q=2): {hurst:.4f}\n"
        summary += f"Generalized Hurst Exponents:\n"

        for q, h in generalized_hurst.items():
            if not np.isnan(h):
                summary += f"  h({q}) = {h:.4f}\n"

        return summary
