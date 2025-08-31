"""
Autoregressive Fractionally Integrated Moving Average (ARFIMA) model implementation.

This module provides a class for generating ARFIMA time series with long-range dependence.
"""

import numpy as np
from typing import Optional, Dict, Any, List
import sys
import os
from scipy import signal
from scipy.special import gamma

from ..base_model import BaseModel


class ARFIMAModel(BaseModel):
    """
    Autoregressive Fractionally Integrated Moving Average (ARFIMA) model.

    ARFIMA(p,d,q) process combines autoregressive (AR), fractionally integrated (FI),
    and moving average (MA) components. The fractional integration parameter d
    controls long-range dependence.

    Parameters
    ----------
    d : float
        Fractional integration parameter (-0.5 < d < 0.5)
    ar_params : List[float], optional
        Autoregressive parameters (default: [])
    ma_params : List[float], optional
        Moving average parameters (default: [])
    sigma : float, optional
        Standard deviation of innovations (default: 1.0)
    method : str, optional
        Generation method (default: 'spectral')
    """

    def __init__(
        self,
        d: float,
        ar_params: Optional[List[float]] = None,
        ma_params: Optional[List[float]] = None,
        sigma: float = 1.0,
        method: str = "spectral",
    ):
        """
        Initialize the ARFIMA model.

        Parameters
        ----------
        d : float
            Fractional integration parameter (-0.5 < d < 0.5)
        ar_params : List[float], optional
            Autoregressive parameters
        ma_params : List[float], optional
            Moving average parameters
        sigma : float, optional
            Standard deviation of innovations
        method : str, optional
            Generation method
        """
        if ar_params is None:
            ar_params = []
        if ma_params is None:
            ma_params = []

        super().__init__(
            d=d, ar_params=ar_params, ma_params=ma_params, sigma=sigma, method=method
        )

    def _validate_parameters(self) -> None:
        """Validate model parameters."""
        d = self.parameters["d"]
        ar_params = self.parameters["ar_params"]
        ma_params = self.parameters["ma_params"]
        sigma = self.parameters["sigma"]
        method = self.parameters["method"]

        if not -0.5 < d < 0.5:
            raise ValueError(
                "Fractional integration parameter d must be in (-0.5, 0.5)"
            )

        if sigma <= 0:
            raise ValueError("Standard deviation sigma must be positive")

        # Check AR polynomial stability
        if ar_params:
            ar_poly = np.poly1d([1] + [-x for x in ar_params])
            roots = ar_poly.roots
            if np.any(
                np.abs(roots) >= 1 - 1e-10
            ):  # Roots must be inside unit circle for stationarity
                raise ValueError("AR parameters must satisfy stationarity conditions")

        # Check MA polynomial invertibility
        if ma_params:
            ma_poly = np.poly1d([1] + ma_params)
            roots = ma_poly.roots
            if np.any(
                np.abs(roots) >= 1 - 1e-10
            ):  # Roots must be inside unit circle for invertibility
                raise ValueError("MA parameters must satisfy invertibility conditions")

        valid_methods = ["spectral", "simulation"]
        if method not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")

    def generate(self, n: int, seed: Optional[int] = None) -> np.ndarray:
        """
        Generate ARFIMA time series.

        Parameters
        ----------
        n : int
            Length of the time series to generate
        seed : int, optional
            Random seed for reproducibility

        Returns
        -------
        np.ndarray
            Generated ARFIMA time series of length n
        """
        if seed is not None:
            np.random.seed(seed)

        d = self.parameters["d"]
        ar_params = self.parameters["ar_params"]
        ma_params = self.parameters["ma_params"]
        sigma = self.parameters["sigma"]
        method = self.parameters["method"]

        if method == "spectral":
            return self._spectral_method(n, d, ar_params, ma_params, sigma)
        else:
            return self._simulation_method(n, d, ar_params, ma_params, sigma)

    def _spectral_method(
        self,
        n: int,
        d: float,
        ar_params: List[float],
        ma_params: List[float],
        sigma: float,
    ) -> np.ndarray:
        """
        Generate ARFIMA using efficient spectral method.

        This method generates the process in the frequency domain using FFT,
        which is much more efficient than time-domain simulation.
        """
        # Generate frequencies
        freqs = np.fft.fftfreq(n)

        # Spectral density of ARFIMA process
        spectral_density = self._compute_spectral_density(
            freqs, d, ar_params, ma_params, sigma
        )

        # Generate complex Gaussian noise
        noise = np.random.normal(0, 1, n) + 1j * np.random.normal(0, 1, n)
        noise = noise / np.sqrt(2)

        # Apply spectral filter
        filtered_noise = noise * np.sqrt(spectral_density)

        # Inverse FFT
        time_series = np.real(np.fft.ifft(filtered_noise))

        return time_series

    def _simulation_method(
        self,
        n: int,
        d: float,
        ar_params: List[float],
        ma_params: List[float],
        sigma: float,
    ) -> np.ndarray:
        """
        Generate ARFIMA using efficient simulation method.

        This method uses FFT-based fractional differencing and efficient
        AR/MA filtering with scipy.
        """
        # Generate white noise
        noise = np.random.normal(0, sigma, n + 1000)  # Extra for warm-up

        # Apply MA filter if needed
        if ma_params:
            ma_filtered = self._apply_ma_filter_efficient(noise, ma_params)
        else:
            ma_filtered = noise

        # Apply fractional differencing using FFT
        frac_diff = self._fractional_differencing_fft(ma_filtered, d)

        # Apply AR filter if needed
        if ar_params:
            ar_filtered = self._apply_ar_filter_efficient(frac_diff, ar_params)
        else:
            ar_filtered = frac_diff

        # Return the final n observations (discard warm-up)
        return ar_filtered[-n:]

    def _fractional_differencing_fft(self, data: np.ndarray, d: float) -> np.ndarray:
        """
        Apply fractional differencing operator (1-L)^d using FFT.

        This is much more efficient than the recursive method.

        Parameters
        ----------
        data : np.ndarray
            Input time series
        d : float
            Fractional integration parameter

        Returns
        -------
        np.ndarray
            Fractionally differenced series
        """
        n = len(data)

        # Compute the fractional differencing filter in frequency domain
        freqs = np.fft.fftfreq(n)

        # Handle zero frequency to avoid division by zero
        freqs_safe = np.where(np.abs(freqs) < 1e-10, 1e-10, freqs)

        # Fractional differencing filter: (1 - exp(-2πi*f))^d
        filter_fft = (1 - np.exp(-2j * np.pi * freqs_safe)) ** d

        # Apply filter using FFT
        data_fft = np.fft.fft(data)
        result_fft = data_fft * filter_fft
        result = np.real(np.fft.ifft(result_fft))

        return result

    def _apply_ar_filter_efficient(
        self, data: np.ndarray, ar_params: List[float]
    ) -> np.ndarray:
        """
        Apply autoregressive filter efficiently using scipy.

        Parameters
        ----------
        data : np.ndarray
            Input time series
        ar_params : List[float]
            AR parameters

        Returns
        -------
        np.ndarray
            AR filtered series
        """
        # Create AR filter coefficients
        ar_coeffs = [1.0] + [-x for x in ar_params]

        # Apply AR filter using scipy's lfilter
        result = signal.lfilter([1.0], ar_coeffs, data)

        return result

    def _apply_ma_filter_efficient(
        self, data: np.ndarray, ma_params: List[float]
    ) -> np.ndarray:
        """
        Apply moving average filter efficiently using scipy.

        Parameters
        ----------
        data : np.ndarray
            Input time series
        ma_params : List[float]
            MA parameters

        Returns
        -------
        np.ndarray
            MA filtered series
        """
        # Create MA filter coefficients
        ma_coeffs = [1.0] + ma_params

        # Apply MA filter using scipy's lfilter
        result = signal.lfilter(ma_coeffs, [1.0], data)

        return result

    def _compute_spectral_density(
        self,
        freqs: np.ndarray,
        d: float,
        ar_params: List[float],
        ma_params: List[float],
        sigma: float,
    ) -> np.ndarray:
        """
        Compute spectral density of ARFIMA process.

        Parameters
        ----------
        freqs : np.ndarray
            Frequencies
        d : float
            Fractional integration parameter
        ar_params : List[float]
            AR parameters
        ma_params : List[float]
            MA parameters
        sigma : float
            Standard deviation

        Returns
        -------
        np.ndarray
            Spectral density
        """
        # Handle zero frequency to avoid division by zero
        freqs_safe = np.where(np.abs(freqs) < 1e-10, 1e-10, freqs)

        # Fractional integration component
        frac_component = np.abs(1 - np.exp(-2j * np.pi * freqs_safe)) ** (-2 * d)

        # AR component
        ar_component = 1.0
        if ar_params:
            ar_poly = np.poly1d([1] + [-x for x in ar_params])
            ar_component = 1.0 / np.abs(ar_poly(np.exp(-2j * np.pi * freqs_safe))) ** 2

        # MA component
        ma_component = 1.0
        if ma_params:
            ma_poly = np.poly1d([1] + ma_params)
            ma_component = np.abs(ma_poly(np.exp(-2j * np.pi * freqs_safe))) ** 2

        # Combine components
        spectral_density = sigma**2 * frac_component * ar_component * ma_component

        return spectral_density

    def get_theoretical_properties(self) -> Dict[str, Any]:
        """
        Get theoretical properties of ARFIMA process.

        Returns
        -------
        dict
            Dictionary containing theoretical properties
        """
        d = self.parameters["d"]
        ar_params = self.parameters["ar_params"]
        ma_params = self.parameters["ma_params"]
        sigma = self.parameters["sigma"]

        return {
            "fractional_integration": d,
            "ar_order": len(ar_params),
            "ma_order": len(ma_params),
            "innovation_variance": sigma**2,
            "long_range_dependence": d > 0,
            "stationary": True,
            "invertible": True,
            "autocorrelation_decay": "power_law" if d > 0 else "exponential",
        }

    def get_increments(self, arfima: np.ndarray) -> np.ndarray:
        """
        Get the increments of ARFIMA process.

        Parameters
        ----------
        arfima : np.ndarray
            ARFIMA time series

        Returns
        -------
        np.ndarray
            Increments (differences)
        """
        return np.diff(arfima)
