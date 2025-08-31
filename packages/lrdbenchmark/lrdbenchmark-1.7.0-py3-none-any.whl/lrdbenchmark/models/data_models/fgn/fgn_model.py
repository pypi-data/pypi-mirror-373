from typing import Optional, Dict, Any
import numpy as np

from ..base_model import BaseModel


class FractionalGaussianNoise(BaseModel):
    """
    Fractional Gaussian Noise (fGn) generator.

    fGn is the stationary increment process of fractional Brownian motion (fBm).
    This class generates fGn directly using the circulant embedding approach on
    the autocovariance function of fGn.
    """

    def __init__(self, H: float, sigma: float = 1.0, method: str = "circulant") -> None:
        super().__init__(H=H, sigma=sigma, method=method)

    def _validate_parameters(self) -> None:
        H = self.parameters.get("H")
        sigma = self.parameters.get("sigma")
        method = self.parameters.get("method")

        if not isinstance(H, (int, float)) or not (0 < H < 1):
            raise ValueError("H must be a float in (0, 1)")
        if not isinstance(sigma, (int, float)) or sigma <= 0:
            raise ValueError("sigma must be a positive float")
        if method not in {"circulant", "cholesky"}:
            raise ValueError("method must be one of {'circulant', 'cholesky'}")

    def generate(self, n: int, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            np.random.seed(seed)

        H = self.parameters["H"]
        sigma = self.parameters["sigma"]
        method = self.parameters["method"]

        if method == "circulant":
            return self._circulant_method(n, H, sigma)
        else:
            return self._cholesky_method(n, H, sigma)

    def _autocovariance_fgn(self, H: float, sigma: float, n: int) -> np.ndarray:
        # γ(k) = (σ^2 / 2)(|k+1|^{2H} - 2|k|^{2H} + |k-1|^{2H}) for k >= 0
        k = np.arange(0, n)
        gamma = (
            (sigma**2)
            * 0.5
            * (
                np.power(k + 1, 2 * H)
                - 2 * np.power(k, 2 * H)
                + np.power(np.maximum(0, k - 1), 2 * H)
            )
        )
        return gamma

    def _circulant_method(self, n: int, H: float, sigma: float) -> np.ndarray:
        # Build circulant embedding of covariance for length n
        gamma = self._autocovariance_fgn(H, sigma, n)
        first_row = np.concatenate([gamma, gamma[1 : n - 1][::-1]])

        # Eigenvalues of the circulant matrix
        eigenvalues = np.fft.fft(first_row)
        eigenvalues = np.maximum(eigenvalues.real, 0.0)

        # Generate complex Gaussian noise with matching length
        z = (
            np.random.normal(0, 1, len(eigenvalues))
            + 1j * np.random.normal(0, 1, len(eigenvalues))
        ) / np.sqrt(2)

        # Filter
        y = np.fft.ifft(z * np.sqrt(eigenvalues))
        x = np.real(y[:n])
        return x

    def _cholesky_method(self, n: int, H: float, sigma: float) -> np.ndarray:
        # Construct Toeplitz covariance matrix from autocovariance
        gamma = self._autocovariance_fgn(H, sigma, n)
        cov = np.empty((n, n))
        for i in range(n):
            for j in range(n):
                cov[i, j] = gamma[abs(i - j)]

        # Regularize if needed and sample
        try:
            L = np.linalg.cholesky(cov)
        except np.linalg.LinAlgError:
            cov = cov + 1e-10 * np.eye(n)
            L = np.linalg.cholesky(cov)

        z = np.random.normal(0.0, 1.0, n)
        x = L @ z
        return x

    def get_theoretical_properties(self) -> Dict[str, Any]:
        H = self.parameters["H"]
        sigma = self.parameters["sigma"]
        return {
            "hurst_parameter": H,
            "variance": sigma**2,
            "stationary": True,
            "gaussian": True,
            "long_range_dependence": H > 0.5,
        }
