"""
JAX-optimized Multifractal Detrended Fluctuation Analysis (MFDFA) Estimator.

This module implements JAX-optimized MFDFA for estimating multifractal properties
of time series data, including the generalized Hurst exponent.
"""

import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from typing import Dict, List, Tuple, Any, Optional
from models.estimators.base_estimator import BaseEstimator


class MFDFAEstimatorJAX(BaseEstimator):
    """
    JAX-optimized Multifractal Detrended Fluctuation Analysis (MFDFA) estimator.

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
        use_gpu: bool = False,
        **kwargs,
    ):
        """
        Initialize JAX-optimized MFDFA estimator.

        Parameters
        ----------
        q_values : list of float, optional
            List of q values for multifractal analysis. Default: [-5, -3, -1, 0, 1, 3, 5]
        scales : list of int, optional
            List of scales for analysis. If None, will be generated from min_scale to max_scale
        min_scale : int, default=8
            Minimum scale for analysis
        max_scale : int, default=50
            Maximum scale for analysis
        num_scales : int, default=15
            Number of scales to use if scales is None
        order : int, default=1
            Order of polynomial for detrending
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
            q_values=q_values,
            scales=scales,
            min_scale=min_scale,
            max_scale=max_scale,
            num_scales=num_scales,
            order=order,
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
                print("JAX MFDFA: Using GPU acceleration")
            except:
                print("JAX MFDFA: GPU not available, using CPU")
                self.use_gpu = False

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

    def _jit_functions(self):
        """JIT compile the core computation functions."""
        # Note: Functions have dynamic parameters, so we don't JIT them to avoid tracing issues
        pass

    def _detrend_series_jax(
        self, series: jnp.ndarray, scale: int, order: int
    ) -> jnp.ndarray:
        """
        Detrend a series segment using polynomial fitting with JAX.

        Parameters
        ----------
        series : jnp.ndarray
            Series segment to detrend
        scale : int
            Scale of the segment
        order : int
            Order of polynomial for detrending

        Returns
        -------
        jnp.ndarray
            Detrended series
        """
        if order == 0:
            return series - jnp.mean(series)
        else:
            x = jnp.arange(scale)
            # Use JAX's polyfit equivalent
            coeffs = jnp.polyfit(x, series, order)
            trend = jnp.polyval(coeffs, x)
            return series - trend

    def _compute_fluctuation_function_jax(
        self, data: jnp.ndarray, q: float, scale: int
    ) -> float:
        """
        Compute fluctuation function for a given q and scale using JAX.

        Parameters
        ----------
        data : jnp.ndarray
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
            return jnp.nan

        # Reshape data into segments
        segments = data[: n_segments * scale].reshape(n_segments, scale)

        # Compute variance for each segment
        variances = []
        for i in range(n_segments):
            segment = segments[i]
            detrended = self._detrend_series_jax(
                segment, scale, self.parameters["order"]
            )
            variance = jnp.mean(detrended**2)
            variances.append(variance)

        variances = jnp.array(variances)

        # Compute q-th order fluctuation function
        if q == 0:
            # Special case for q = 0
            fq = jnp.exp(0.5 * jnp.mean(jnp.log(variances)))
        else:
            fq = jnp.mean(variances ** (q / 2)) ** (1 / q)

        return fq

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
        Estimate multifractal properties using JAX-optimized MFDFA.

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
        data = jnp.asarray(data)

        if len(data) < 2 * self.parameters["max_scale"]:
            import warnings

            warnings.warn(
                f"Data length ({len(data)}) may be too short for scale {self.parameters['max_scale']}"
            )

        scales = self.parameters["scales"]
        q_values = self.parameters["q_values"]

        # Compute fluctuation functions for all q and scales
        fluctuation_functions = {}
        for q in q_values:
            fq_values = []
            for scale in scales:
                fq = self._compute_fluctuation_function_jax(data, q, scale)
                fq_values.append(float(fq))
            fluctuation_functions[q] = np.array(fq_values)

        # Fit power law for each q to get generalized Hurst exponents
        generalized_hurst = {}
        log_scales = np.log(scales)

        for q in q_values:
            fq_vals = fluctuation_functions[q]
            # Filter out NaN values
            valid_mask = ~np.isnan(fq_vals)
            if np.sum(valid_mask) >= 2:
                x = jnp.array(log_scales[valid_mask])
                y = jnp.array(np.log(fq_vals[valid_mask]))
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
            "fluctuation_functions": fluctuation_functions,
        }

        return self.results
