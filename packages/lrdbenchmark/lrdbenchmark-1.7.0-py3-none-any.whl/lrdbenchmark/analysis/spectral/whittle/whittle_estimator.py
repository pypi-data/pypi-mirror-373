"""
Whittle-based Hurst parameter estimator with adaptive spectral approach.

This module implements a robust Whittle-based estimator for the Hurst parameter
using adaptive spectral methods with intelligent method selection.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats, signal, optimize
# Import base estimator
try:
    from models.estimators.base_estimator import BaseEstimator
except ImportError:
    # Fallback if base estimator not available
    class BaseEstimator:
        def __init__(self, **kwargs):
            self.parameters = kwargs


class WhittleEstimator(BaseEstimator):
    """
    Whittle-based Hurst parameter estimator with adaptive spectral approach.

    This estimator uses adaptive spectral methods with intelligent method selection
    to provide robust Hurst parameter estimation.

    Parameters
    ----------
    min_freq_ratio : float, optional (default=0.01)
        Minimum frequency ratio (relative to Nyquist) for fitting.
    max_freq_ratio : float, optional (default=0.1)
        Maximum frequency ratio (relative to Nyquist) for fitting.
    use_local_whittle : bool, optional (default=False)
        Whether to attempt Local Whittle estimation as fallback.
    use_welch : bool, optional (default=True)
        Whether to use Welch's method for PSD estimation.
    window : str, optional (default='hann')
        Window function for Welch's method.
    nperseg : int, optional (default=None)
        Length of each segment for Welch's method. If None, uses adaptive selection.
    """

    def __init__(
        self,
        min_freq_ratio=0.01,
        max_freq_ratio=0.1,
        use_local_whittle=False,
        use_welch=True,
        window="hann",
        nperseg=None,
    ):
        super().__init__()
        self.min_freq_ratio = min_freq_ratio
        self.max_freq_ratio = max_freq_ratio
        self.use_local_whittle = use_local_whittle
        self.use_welch = use_welch
        self.window = window
        self.nperseg = nperseg
        self.results = {}
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not (0 < self.min_freq_ratio < self.max_freq_ratio < 0.5):
            raise ValueError(
                "Frequency ratios must satisfy: 0 < min_freq_ratio < max_freq_ratio < 0.5"
            )

        if self.nperseg is not None and self.nperseg < 2:
            raise ValueError("nperseg must be at least 2")

    def estimate(self, data):
        """
        Estimate Hurst parameter using adaptive spectral approach with intelligent method selection.

        Parameters
        ----------
        data : array-like
            Time series data.

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        data = np.asarray(data)
        n = len(data)

        # Adaptive bandwidth selection based on data length and characteristics
        bandwidth_info = self._adaptive_bandwidth_selection(data)
        
        # Method 1: Traditional Spectral Approach with adaptive bandwidth
        hurst_spectral, spectral_quality = self._spectral_approach_adaptive(data, bandwidth_info)
        
        # Method 2: Local Whittle (Research Paper) - kept for comparison if enabled
        if self.use_local_whittle:
            try:
                hurst_local_whittle = self._local_whittle_approach(data)
                local_whittle_available = True
            except Exception as e:
                hurst_local_whittle = 0.5  # fallback
                local_whittle_available = False
        else:
            hurst_local_whittle = 0.5
            local_whittle_available = False
        
        # Intelligent method selection based on quality metrics
        hurst, method_used, selection_reason = self._select_best_method(
            hurst_spectral, spectral_quality, 
            hurst_local_whittle, local_whittle_available
        )
        
        # Compute final results using the selected method
        if method_used.startswith("Spectral"):
            T, S, scale = self._get_spectral_data_adaptive(data, bandwidth_info)
        else:
            T, S, scale = self._get_local_whittle_data(data)
        
        # Compute R-squared and other metrics
        model_spectrum = self._fgn_spectrum(T, hurst, scale)
        log_model = np.log(model_spectrum)
        log_periodogram = np.log(S)
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_model, log_periodogram
        )
        r_squared = r_value**2
        
        self.results = {
            "hurst_parameter": float(hurst),
            "d_parameter": float(hurst - 0.5),  # d = H - 0.5 for fGn
            "scale_parameter": float(scale),
            "r_squared": float(r_squared),
            "slope": float(slope),
            "intercept": float(intercept),
            "p_value": float(p_value),
            "std_error": float(std_err),
            "m": int(len(T)),
            "log_model": log_model,
            "log_periodogram": log_periodogram,
            "frequency": T,
            "periodogram": S,
            "method": method_used,
            "selection_reason": selection_reason,
            "spectral_estimate": float(hurst_spectral),
            "local_whittle_estimate": float(hurst_local_whittle) if local_whittle_available else None,
            "bandwidth_info": bandwidth_info,
            "spectral_quality": spectral_quality
        }
        return self.results

    def _adaptive_bandwidth_selection(self, data):
        """
        Adaptive bandwidth selection based on data characteristics.
        
        Returns
        -------
        dict
            Dictionary containing bandwidth parameters
        """
        n = len(data)
        
        # Base bandwidth selection
        if n < 500:
            # Small datasets: use wider bandwidth for stability
            min_freq = 0.02
            max_freq = 0.25
            nperseg = min(n // 4, 64)
        elif n < 2000:
            # Medium datasets: balanced approach
            min_freq = 0.015
            max_freq = 0.22
            nperseg = min(n // 8, 128)
        else:
            # Large datasets: can use narrower bandwidth for precision
            min_freq = 0.01
            max_freq = 0.2
            nperseg = min(n // 8, 256)
        
        # Adjust based on data variance (indicator of noise level)
        data_var = np.var(data)
        if data_var > 10:  # High variance data
            min_freq = max(min_freq, 0.025)  # Avoid very low frequencies
            max_freq = min(max_freq, 0.18)   # Avoid very high frequencies
        
        # Ensure we have enough frequency points
        expected_freqs = int((max_freq - min_freq) * n / 2)
        if expected_freqs < 10:
            # Expand bandwidth if too few points
            min_freq = max(0.005, min_freq - 0.01)
            max_freq = min(0.3, max_freq + 0.01)
        
        return {
            'min_freq': min_freq,
            'max_freq': max_freq,
            'nperseg': nperseg,
            'data_length': n,
            'data_variance': data_var
        }
    
    def _spectral_approach_adaptive(self, data, bandwidth_info):
        """
        Adaptive spectral approach using periodogram and power law fitting.
        """
        n = len(data)
        
        # Use adaptive bandwidth parameters
        min_freq = bandwidth_info['min_freq']
        max_freq = bandwidth_info['max_freq']
        nperseg = bandwidth_info['nperseg']
        
        # Compute periodogram using Welch's method with adaptive parameters
        freqs, psd = signal.welch(data, nperseg=nperseg, scaling='density')
        
        # Select frequency range for fitting
        mask = (freqs >= min_freq) & (freqs <= max_freq) & (psd > 0)
        freqs_sel = freqs[mask]
        psd_sel = psd[mask]
        
        if len(freqs_sel) < 5:
            # Fallback to wider bandwidth if insufficient points
            min_freq = max(0.005, min_freq - 0.01)
            max_freq = min(0.4, max_freq + 0.01)
            mask = (freqs >= min_freq) & (freqs <= max_freq) & (psd > 0)
            freqs_sel = freqs[mask]
            psd_sel = psd[mask]
            
            if len(freqs_sel) < 3:
                raise ValueError("Insufficient frequency points for spectral analysis")
        
        # Power law fit: PSD(f) ~ f^(-β) where β = 2H - 1
        log_f = np.log(freqs_sel)
        log_psd = np.log(psd_sel)
        
        # Linear regression in log-log space
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_f, log_psd)
        
        # β = -slope (negative because PSD decreases with frequency)
        beta = -slope
        
        # H = (β + 1) / 2
        H = (beta + 1) / 2
        
        # Ensure H is within reasonable bounds
        H = np.clip(H, 0.1, 0.9)
        
        # Quality assessment
        quality = {
            'r_squared': r_value**2,
            'p_value': p_value,
            'std_error': std_err,
            'frequency_points': len(freqs_sel),
            'frequency_range': [freqs_sel.min(), freqs_sel.max()],
            'slope': slope,
            'beta': beta
        }
        
        return H, quality
    
    def _select_best_method(self, hurst_spectral, spectral_quality, 
                           hurst_local_whittle, local_whittle_available):
        """
        Intelligent method selection based on quality metrics.
        """
        # Quality thresholds
        R2_THRESHOLD = 0.3
        P_VALUE_THRESHOLD = 0.05
        
        # Check if spectral method is reliable
        spectral_reliable = (
            spectral_quality['r_squared'] > R2_THRESHOLD and
            spectral_quality['p_value'] < P_VALUE_THRESHOLD and
            0.1 <= hurst_spectral <= 0.9
        )
        
        # Check if Local Whittle is available and reasonable
        local_whittle_reasonable = (
            local_whittle_available and
            0.1 <= hurst_local_whittle <= 0.9
        )
        
        # Decision logic
        if spectral_reliable:
            method = "Spectral Approach (Adaptive)"
            reason = f"High quality spectral fit (R²={spectral_quality['r_squared']:.3f})"
        elif local_whittle_reasonable:
            method = "Local Whittle (Research Paper)"
            reason = "Spectral method unreliable, Local Whittle reasonable"
        else:
            # Both methods have issues, use spectral with warning
            method = "Spectral Approach (Adaptive) - Fallback"
            reason = f"Both methods problematic, using spectral (R²={spectral_quality['r_squared']:.3f})"
        
        # Select the appropriate Hurst value
        if method.startswith("Spectral"):
            hurst = hurst_spectral
        else:
            hurst = hurst_local_whittle
        
        return hurst, method, reason
    
    def _get_spectral_data_adaptive(self, data, bandwidth_info):
        """Get spectral data using adaptive bandwidth."""
        n = len(data)
        freqs, psd = signal.welch(data, nperseg=bandwidth_info['nperseg'], scaling='density')
        min_freq, max_freq = bandwidth_info['min_freq'], bandwidth_info['max_freq']
        mask = (freqs >= min_freq) & (freqs <= max_freq) & (psd > 0)
        freqs_sel = freqs[mask]
        psd_sel = psd[mask]
        
        # Estimate scale parameter
        scale = np.mean(psd_sel)
        return freqs_sel, psd_sel, scale

    def _fgn_spectrum(self, freqs, hurst, scale=1.0):
        """Compute fGn power spectrum."""
        # fGn spectrum: S(f) = scale * |2*sin(π*f)|^(2H-2)
        return scale * np.abs(2 * np.sin(np.pi * freqs)) ** (2 * hurst - 2)

    def _local_whittle_approach(self, data):
        """
        Local Whittle approach based on research paper Algorithm 15.
        """
        n = len(data)

        # Step 1: Compute FFT of the time sequence (Algorithm 15, Line 3)
        Y = np.fft.fft(data)
        
        # Step 2: Calculate n = [N/2] (Algorithm 15, Line 4)
        n_freq = n // 2
        
        # Step 3: Initialize frequency and periodogram vectors (Algorithm 15, Lines 5-6)
        T = np.zeros(n_freq)  # for the frequencies
        S = np.zeros(n_freq)  # for the periodogram
        
        # Step 4: Calculate frequencies and periodogram (Algorithm 15, Lines 7-10)
        for idx in range(n_freq):
            # T_idx = idx/N (Algorithm 15, Line 8)
            T[idx] = idx / n
            
            # S_idx = |Y_{idx+1}|^2 (Algorithm 15, Line 9)
            S[idx] = np.abs(Y[idx + 1]) ** 2
        
        # Step 5: Filter out zero frequencies and use appropriate frequency range for Local Whittle
        min_freq = 0.01  # Minimum frequency ratio
        max_freq = 0.1   # Maximum frequency ratio
        
        valid_mask = (T >= min_freq) & (T <= max_freq) & (S > 0)
        T = T[valid_mask]
        S = S[valid_mask]
        
        if len(T) < 3:
            raise ValueError("Insufficient frequency points for Local Whittle estimation")
        
        # Step 6: Use Local Whittle solver (Algorithm 15, Line 11)
        hurst = self._local_whittle_solver(T, S)
        
        return hurst
    
    def _local_whittle_solver(self, T, S):
        """
        Local Whittle solver based on Algorithm 15.
        """
        def objective_function(H):
            # Local Whittle maximizes the log-likelihood, so we minimize the negative
            return -self._compute_local_whittle_likelihood(T, S, H)
        
        # Initial guess: H = 0.5 (random walk)
        x0 = [0.5]
        
        # Optimize using L-BFGS-B with bounds
        result = optimize.minimize(
            objective_function,
            x0,
            bounds=[(0.001, 0.999)],
            method="L-BFGS-B",
            options={'ftol': 1e-8}
        )
        
        if result.success:
            return result.x[0]
        else:
            # Fallback to grid search if optimization fails
            return self._grid_search_local_whittle(T, S)
    
    def _compute_local_whittle_likelihood(self, T, S, H):
        """
        Compute Local Whittle objective function ψ(H) based on Algorithm 16.
        """
        n = len(T)
        
        # Algorithm 16, Line 3: ψ(H) = ln((1/n) * Σ_{i=1}^{n} T_i^(2H-1) * S_i) - ((2H-1)/n) * Σ_{i=1}^{n} ln T_i
        
        # First term: ln((1/n) * Σ_{i=1}^{n} T_i^(2H-1) * S_i)
        first_term = np.sum(T ** (2 * H - 1) * S) / n
        first_term = np.log(first_term)
        
        # Second term: ((2H-1)/n) * Σ_{i=1}^{n} ln T_i
        second_term = (2 * H - 1) * np.sum(np.log(T)) / n
        
        # Return ψ(H) = first_term - second_term
        return first_term - second_term
    
    def _grid_search_local_whittle(self, T, S):
        """
        Fallback grid search for Local Whittle estimation.
        """
        H_values = np.linspace(0.001, 0.999, 100)
        likelihood_values = []
        
        for H in H_values:
            try:
                likelihood = self._compute_local_whittle_likelihood(T, S, H)
                likelihood_values.append(likelihood)
            except:
                likelihood_values.append(-np.inf)
        
        # Find H that maximizes likelihood (since we're returning positive values)
        best_idx = np.argmax(likelihood_values)
        return H_values[best_idx]
    
    def _get_local_whittle_data(self, data):
        """Get Local Whittle data for the chosen method."""
        n = len(data)
        Y = np.fft.fft(data)
        n_freq = n // 2
        T = np.array([idx / n for idx in range(n_freq)])
        S = np.array([np.abs(Y[idx + 1]) ** 2 for idx in range(n_freq)])
        
        min_freq, max_freq = 0.01, 0.1
        valid_mask = (T >= min_freq) & (T <= max_freq) & (S > 0)
        T = T[valid_mask]
        S = S[valid_mask]
        
        # Estimate scale parameter
        scale = np.mean(S)
        return T, S, scale

    def plot_scaling(self, save_path=None):
        """Plot the scaling relationship and PSD."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Log-log scaling relationship
        ax1.scatter(
            self.results["log_model"],
            self.results["log_periodogram"],
            alpha=0.6,
            label="Data points",
        )

        # Fit line
        x_range = np.linspace(
            self.results["log_model"].min(),
            self.results["log_model"].max(),
            100,
        )
        y_fit = (
            self.results["slope"] * x_range + self.results["intercept"]
        )
        ax1.plot(x_range, y_fit, "r--", label=f"Fit (R² = {self.results['r_squared']:.3f})")

        ax1.set_xlabel("Log Model Spectrum")
        ax1.set_ylabel("Log Periodogram")
        ax1.set_title("Scaling Relationship")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Power Spectral Density
        ax2.loglog(
            self.results["frequency"],
            self.results["periodogram"],
            "b-",
            alpha=0.7,
            label="Periodogram",
        )

        # Model spectrum
        model_freq = np.logspace(
            np.log10(self.results["frequency"].min()),
            np.log10(self.results["frequency"].max()),
            100,
        )
        model_psd = self._fgn_spectrum(
            model_freq, self.results["hurst_parameter"], self.results["scale_parameter"]
        )
        ax2.loglog(model_freq, model_psd, "r--", label="fGn Model")

        ax2.set_xlabel("Frequency")
        ax2.set_ylabel("Power Spectral Density")
        ax2.set_title(f"Power Spectral Density (H = {self.results['hurst_parameter']:.3f})")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()
