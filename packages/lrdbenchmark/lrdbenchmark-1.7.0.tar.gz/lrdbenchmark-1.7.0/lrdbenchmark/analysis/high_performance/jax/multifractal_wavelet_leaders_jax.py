"""
JAX-optimized Multifractal Wavelet Leaders Estimator.

This module implements JAX-optimized Multifractal Wavelet Leaders analysis for estimating
multifractal properties of time series data using wavelet leaders.
"""

import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from typing import Dict, List, Tuple, Any, Optional
from models.estimators.base_estimator import BaseEstimator


class MultifractalWaveletLeadersEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Multifractal Wavelet Leaders estimator.

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
        use_gpu: bool = False,
        **kwargs,
    ):
        """
        Initialize JAX-optimized Multifractal Wavelet Leaders estimator.

        Parameters
        ----------
        wavelet : str, default='db4'
            Wavelet to use for analysis
        scales : list of int, optional
            List of scales for analysis. If None, will be generated from min_scale to max_scale
        min_scale : int, default=2
            Minimum scale for analysis
        max_scale : int, default=32
            Maximum scale for analysis
        num_scales : int, default=10
            Number of scales to use if scales is None
        q_values : list of float, optional
            List of q values for multifractal analysis. Default: [-5, -3, -1, 0, 1, 3, 5]
        use_gpu : bool, default=False
            Whether to use GPU acceleration
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
            use_gpu=use_gpu,
            **kwargs,
        )

        # Store use_gpu as instance attribute
        self.use_gpu = use_gpu

        self._validate_parameters()
        self._jit_functions()

        # GPU setup
        if self.use_gpu:
            try:
                jax.devices("gpu")
                print("JAX Multifractal Wavelet Leaders: Using GPU acceleration")
            except:
                print("JAX Multifractal Wavelet Leaders: GPU not available, using CPU")
                self.use_gpu = False

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

    def _jit_functions(self):
        """JIT compile the core computation functions."""
        # Note: Functions have dynamic parameters, so we don't JIT them to avoid tracing issues
        pass

    def _compute_wavelet_coefficients_jax(
        self, data: jnp.ndarray, scale: int
    ) -> jnp.ndarray:
        """
        Compute wavelet coefficients at a given scale using JAX.

        Parameters
        ----------
        data : jnp.ndarray
            Time series data
        scale : int
            Scale for analysis

        Returns
        -------
        jnp.ndarray
            Wavelet coefficients
        """
        # For JAX compatibility, we'll use a simplified approach
        # In practice, you might want to use a JAX-compatible wavelet library

        # Downsample data by 2^scale
        step = 2**scale
        if step >= len(data):
            return jnp.array([])

        # Create downsampled version
        downsampled = data[::step]

        # Compute differences as approximation of wavelet coefficients
        if len(downsampled) > 1:
            coeffs = jnp.diff(downsampled)
        else:
            coeffs = jnp.array([])

        return coeffs

    def _compute_leaders_jax(self, coeffs: jnp.ndarray) -> jnp.ndarray:
        """
        Compute wavelet leaders from coefficients using JAX.

        Parameters
        ----------
        coeffs : jnp.ndarray
            Wavelet coefficients

        Returns
        -------
        jnp.ndarray
            Wavelet leaders
        """
        if len(coeffs) == 0:
            return jnp.array([])

        # Compute local maxima (simplified leaders)
        leaders = []
        for i in range(1, len(coeffs) - 1):
            if coeffs[i] > coeffs[i - 1] and coeffs[i] > coeffs[i + 1]:
                leaders.append(jnp.abs(coeffs[i]))

        if len(leaders) == 0:
            # If no local maxima, use absolute values
            leaders = [jnp.abs(coeff) for coeff in coeffs]

        return jnp.array(leaders)

    def _linear_regression_jax(
        self, x: jnp.ndarray, y: jnp.ndarray
    ) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
        """
        Perform linear regression using JAX.

        Args:
            x: Independent variable
            y: Dependent variable

        Returns:
            Tuple of (slope, intercept, r_squared)
        """
        # Center the data
        x_mean = jnp.mean(x)
        y_mean = jnp.mean(y)

        x_centered = x - x_mean
        y_centered = y - y_mean

        # Compute slope
        numerator = jnp.sum(x_centered * y_centered)
        denominator = jnp.sum(x_centered**2)

        if denominator == 0:
            slope = jnp.array(0.0)
        else:
            slope = numerator / denominator

        # Compute intercept
        intercept = y_mean - slope * x_mean

        # Compute R-squared
        y_pred = slope * x + intercept
        ss_res = jnp.sum((y - y_pred) ** 2)
        ss_tot = jnp.sum((y - y_mean) ** 2)

        if ss_tot == 0:
            r_squared = jnp.array(0.0)
        else:
            r_squared = 1 - (ss_res / ss_tot)

        return slope, intercept, r_squared

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate multifractal properties using JAX-optimized Multifractal Wavelet Leaders.

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
            - 'leaders_functions': Dictionary of S(q,j) for each q
        """
        data = jnp.asarray(data)

        if len(data) < 2 * self.parameters["max_scale"]:
            import warnings

            warnings.warn(
                f"Data length ({len(data)}) may be too short for scale {self.parameters['max_scale']}"
            )

        scales = self.parameters["scales"]
        q_values = self.parameters["q_values"]

        # Compute leaders functions for all q and scales
        leaders_functions = {}
        for q in q_values:
            sq_values = []
            for scale in scales:
                # Compute wavelet coefficients
                coeffs = self._compute_wavelet_coefficients_jax(data, scale)

                if len(coeffs) > 0:
                    # Compute leaders
                    leaders = self._compute_leaders_jax(coeffs)

                    if len(leaders) > 0:
                        # Compute q-th order structure function
                        if q == 0:
                            # Special case for q = 0
                            sq = jnp.exp(jnp.mean(jnp.log(leaders)))
                        else:
                            sq = jnp.mean(leaders**q) ** (1 / q)
                    else:
                        sq = jnp.nan
                else:
                    sq = jnp.nan

                sq_values.append(float(sq))
            leaders_functions[q] = np.array(sq_values)

        # Fit power law for each q to get generalized Hurst exponents
        generalized_hurst = {}
        log_scales = np.log(scales)

        for q in q_values:
            sq_vals = leaders_functions[q]
            # Filter out NaN values
            valid_mask = ~np.isnan(sq_vals)
            if np.sum(valid_mask) >= 2:
                x = jnp.array(log_scales[valid_mask])
                y = jnp.array(np.log(sq_vals[valid_mask]))
                slope, intercept, r_squared = self._linear_regression_jax(x, y)
                generalized_hurst[q] = float(slope)
            else:
                generalized_hurst[q] = np.nan

        # Get Hurst parameter (q=2)
        hurst_parameter = generalized_hurst.get(2, 0.5)

        # Compute multifractal spectrum (simplified)
        q_array = np.array(list(generalized_hurst.keys()))
        h_array = np.array(list(generalized_hurst.values()))

        # Filter out NaN values
        valid_mask = ~np.isnan(h_array)
        if np.sum(valid_mask) >= 3:
            q_valid = q_array[valid_mask]
            h_valid = h_array[valid_mask]

            # Compute alpha and f(alpha) using Legendre transform
            alpha = h_valid + q_valid * np.gradient(h_valid, q_valid)
            f_alpha = q_valid * alpha - h_valid
        else:
            alpha = np.array([0.5])
            f_alpha = np.array([1.0])

        # Store results
        self.results = {
            "hurst_parameter": float(hurst_parameter),
            "generalized_hurst": generalized_hurst,
            "multifractal_spectrum": {
                "alpha": alpha.tolist(),
                "f_alpha": f_alpha.tolist(),
            },
            "scales": scales.tolist(),
            "q_values": q_values,
            "leaders_functions": leaders_functions,
        }

        return self.results
