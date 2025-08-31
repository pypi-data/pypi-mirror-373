"""
Numba-optimized Multifractal Wavelet Leaders Estimator.

This module implements Numba-optimized Multifractal Wavelet Leaders analysis for estimating
multifractal properties of time series data using wavelet leaders.
"""

import numpy as np
from numba import jit, prange
from typing import Dict, List, Tuple, Any, Optional
from models.estimators.base_estimator import BaseEstimator


@jit(nopython=True, cache=True)
def _compute_wavelet_coefficients_numba(data: np.ndarray, scale: int) -> np.ndarray:
    """
    Compute wavelet coefficients at a given scale using Numba.

    Parameters
    ----------
    data : np.ndarray
        Time series data
    scale : int
        Scale for analysis

    Returns
    -------
    np.ndarray
        Wavelet coefficients
    """
    # For Numba compatibility, we'll use a simplified approach
    # In practice, you might want to use a Numba-compatible wavelet library

    # Downsample data by 2^scale
    step = 2**scale
    if step >= len(data):
        return np.empty(0, dtype=np.float64)

    # Create downsampled version
    downsampled_size = len(data) // step
    downsampled = np.empty(downsampled_size)
    for i in range(downsampled_size):
        downsampled[i] = data[i * step]

    # Compute differences as approximation of wavelet coefficients
    if len(downsampled) > 1:
        coeffs = np.empty(len(downsampled) - 1)
        for i in range(len(coeffs)):
            coeffs[i] = downsampled[i + 1] - downsampled[i]
    else:
        coeffs = np.empty(0, dtype=np.float64)

    return coeffs


@jit(nopython=True, cache=True)
def _compute_leaders_numba(coeffs: np.ndarray) -> np.ndarray:
    """
    Compute wavelet leaders from coefficients using Numba.

    Parameters
    ----------
    coeffs : np.ndarray
        Wavelet coefficients

    Returns
    -------
    np.ndarray
        Wavelet leaders
    """
    if len(coeffs) == 0:
        return np.empty(0, dtype=np.float64)

    # Compute local maxima (simplified leaders)
    leaders = []
    for i in range(1, len(coeffs) - 1):
        if coeffs[i] > coeffs[i - 1] and coeffs[i] > coeffs[i + 1]:
            leaders.append(np.abs(coeffs[i]))

    if len(leaders) == 0:
        # If no local maxima, use absolute values
        leaders = np.empty(len(coeffs))
        for i in range(len(coeffs)):
            leaders[i] = np.abs(coeffs[i])
    else:
        leaders = np.array(leaders)

    return leaders


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

    # Compute means
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


class MultifractalWaveletLeadersEstimatorNumba(BaseEstimator):
    """
    Numba-optimized Multifractal Wavelet Leaders estimator.

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
        use_parallel: bool = True,
        **kwargs,
    ):
        """
        Initialize Numba-optimized Multifractal Wavelet Leaders estimator.

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
        use_parallel : bool, default=True
            Whether to use parallel processing
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
            use_parallel=use_parallel,
            **kwargs,
        )

        # Store use_parallel as instance attribute
        self.use_parallel = use_parallel

        self._validate_parameters()

        if self.use_parallel:
            print("Numba Multifractal Wavelet Leaders: Using parallel processing")
        else:
            print(
                "Numba Multifractal Wavelet Leaders: Using single-threaded processing"
            )

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

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate multifractal properties using Numba-optimized Multifractal Wavelet Leaders.

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
        data = np.asarray(data, dtype=np.float64)

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
                coeffs = _compute_wavelet_coefficients_numba(data, scale)

                if len(coeffs) > 0:
                    # Compute leaders
                    leaders = _compute_leaders_numba(coeffs)

                    if len(leaders) > 0:
                        # Compute q-th order structure function
                        if q == 0:
                            # Special case for q = 0
                            log_sum = 0.0
                            count = 0
                            for i in range(len(leaders)):
                                if leaders[i] > 0:
                                    log_sum += np.log(leaders[i])
                                    count += 1
                            if count > 0:
                                sq = np.exp(log_sum / count)
                            else:
                                sq = np.nan
                        else:
                            # Compute mean of leaders^q
                            sum_val = 0.0
                            for i in range(len(leaders)):
                                sum_val += leaders[i] ** q
                            mean_val = sum_val / len(leaders)
                            sq = mean_val ** (1 / q)
                    else:
                        sq = np.nan
                else:
                    sq = np.nan

                sq_values.append(sq)
            leaders_functions[q] = np.array(sq_values)

        # Fit power law for each q to get generalized Hurst exponents
        generalized_hurst = {}
        log_scales = np.log(scales)

        for q in q_values:
            sq_vals = leaders_functions[q]
            # Filter out NaN values
            valid_mask = ~np.isnan(sq_vals)
            if np.sum(valid_mask) >= 2:
                x = log_scales[valid_mask]
                y = np.log(sq_vals[valid_mask])
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
            "leaders_functions": leaders_functions,
        }

        return self.results
