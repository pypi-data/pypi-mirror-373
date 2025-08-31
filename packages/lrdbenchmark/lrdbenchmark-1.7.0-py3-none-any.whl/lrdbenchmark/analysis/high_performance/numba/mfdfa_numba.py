"""
Numba-optimized Multifractal Detrended Fluctuation Analysis (MFDFA) Estimator.

This module implements Numba-optimized MFDFA for estimating multifractal properties
of time series data, including the generalized Hurst exponent.
"""

import numpy as np
from numba import jit, prange
from typing import Dict, List, Tuple, Any, Optional
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, cache=True)
def _detrend_series_numba(series: np.ndarray, scale: int, order: int) -> np.ndarray:
    """
    Detrend a series segment using polynomial fitting with Numba.

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
        mean_val = 0.0
        for i in range(len(series)):
            mean_val += series[i]
        mean_val /= len(series)

        result = np.empty(len(series))
        for i in range(len(series)):
            result[i] = series[i] - mean_val
        return result
    else:
        # Simple linear detrending for Numba compatibility
        x = np.arange(scale, dtype=np.float64)

        # Compute means
        x_mean = 0.0
        y_mean = 0.0
        for i in range(scale):
            x_mean += x[i]
            y_mean += series[i]
        x_mean /= scale
        y_mean /= scale

        # Compute slope
        numerator = 0.0
        denominator = 0.0
        for i in range(scale):
            x_centered = x[i] - x_mean
            y_centered = series[i] - y_mean
            numerator += x_centered * y_centered
            denominator += x_centered**2

        if denominator == 0.0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Compute intercept
        intercept = y_mean - slope * x_mean

        # Detrend
        result = np.empty(scale)
        for i in range(scale):
            trend = slope * x[i] + intercept
            result[i] = series[i] - trend

        return result


@jit(nopython=True, cache=True)
def _compute_fluctuation_function_numba(
    data: np.ndarray, q: float, scale: int, order: int
) -> float:
    """
    Compute fluctuation function for a given q and scale using Numba.

    Parameters
    ----------
    data : np.ndarray
        Time series data
    q : float
        Moment order
    scale : int
        Scale for analysis
    order : int
        Order of polynomial for detrending

    Returns
    -------
    float
        Fluctuation function value
    """
    n_segments = len(data) // scale
    if n_segments == 0:
        return np.nan

    # Compute variance for each segment
    variances = np.empty(n_segments)

    for seg_idx in range(n_segments):
        start_idx = seg_idx * scale
        end_idx = start_idx + scale

        # Extract segment
        segment = np.empty(scale)
        for i in range(scale):
            segment[i] = data[start_idx + i]

        # Detrend segment
        detrended = _detrend_series_numba(segment, scale, order)

        # Compute variance
        variance = 0.0
        for i in range(scale):
            variance += detrended[i] ** 2
        variance /= scale

        variances[seg_idx] = variance

    # Compute q-th order fluctuation function
    if q == 0:
        # Special case for q = 0
        log_sum = 0.0
        for i in range(n_segments):
            if variances[i] > 0:
                log_sum += np.log(variances[i])
        fq = np.exp(0.5 * log_sum / n_segments)
    else:
        # General case
        sum_val = 0.0
        for i in range(n_segments):
            sum_val += variances[i] ** (q / 2)
        fq = (sum_val / n_segments) ** (1 / q)

    return fq


@jit(nopython=True, cache=True)
def _linear_regression_numba(
    x: np.ndarray, y: np.ndarray
) -> Tuple[float, float, float]:
    """
    Perform linear regression using Numba.

    Args:
        x: Independent variable
        y: Dependent variable

    Returns:
        Tuple of (slope, intercept, r_squared)
    """
    n = len(x)
    if n < 2:
        return 0.0, 0.0, 0.0

    # Center the data
    x_mean = 0.0
    y_mean = 0.0

    for i in range(n):
        x_mean += x[i]
        y_mean += y[i]

    x_mean /= n
    y_mean /= n

    # Compute slope
    numerator = 0.0
    denominator = 0.0

    for i in range(n):
        x_centered = x[i] - x_mean
        y_centered = y[i] - y_mean
        numerator += x_centered * y_centered
        denominator += x_centered**2

    if denominator == 0.0:
        slope = 0.0
    else:
        slope = numerator / denominator

    # Compute intercept
    intercept = y_mean - slope * x_mean

    # Compute R-squared
    ss_res = 0.0
    ss_tot = 0.0

    for i in range(n):
        y_pred = slope * x[i] + intercept
        ss_res += (y[i] - y_pred) ** 2
        ss_tot += (y[i] - y_mean) ** 2

    if ss_tot == 0.0:
        r_squared = 0.0
    else:
        r_squared = 1.0 - (ss_res / ss_tot)

    return slope, intercept, r_squared


class MFDFAEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Multifractal Detrended Fluctuation Analysis (MFDFA) estimator.

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
        Initialize Numba-optimized MFDFA estimator.

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
        print("Numba MFDFA: Using JIT-compiled optimization")

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

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate multifractal properties using Numba-optimized MFDFA.

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
        data = np.asarray(data, dtype=np.float64)

        if len(data) < 2 * self.parameters["max_scale"]:
            import warnings

            warnings.warn(
                f"Data length ({len(data)}) may be too short for scale {self.parameters['max_scale']}"
            )

        scales = self.parameters["scales"]
        q_values = self.parameters["q_values"]
        order = self.parameters["order"]

        # Compute fluctuation functions for all q and scales
        fluctuation_functions = {}
        for q in q_values:
            fq_values = []
            for scale in scales:
                fq = _compute_fluctuation_function_numba(data, q, scale, order)
                fq_values.append(fq)
            fluctuation_functions[q] = np.array(fq_values)

        # Fit power law for each q to get generalized Hurst exponents
        generalized_hurst = {}
        log_scales = np.log(scales)

        for q in q_values:
            fq_vals = fluctuation_functions[q]
            # Filter out NaN values
            valid_mask = ~np.isnan(fq_vals)
            if np.sum(valid_mask) >= 2:
                x = np.array(log_scales[valid_mask], dtype=np.float64)
                y = np.array(np.log(fq_vals[valid_mask]), dtype=np.float64)
                slope, intercept, r_squared = _linear_regression_numba(x, y)
                generalized_hurst[q] = slope
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
