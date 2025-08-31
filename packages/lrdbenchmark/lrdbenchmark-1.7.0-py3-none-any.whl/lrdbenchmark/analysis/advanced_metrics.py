#!/usr/bin/env python3
"""
Advanced Metrics Module for LRDBench

This module provides advanced computational profiling and estimation evaluation
metrics including convergence rates and mean signed error calculations.
"""

import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from scipy import stats
from scipy.optimize import curve_fit
import warnings


class ConvergenceAnalyzer:
    """
    Analyzer for convergence rates and stability of estimators.
    
    This class provides methods to analyze how quickly estimators converge
    to stable estimates and how reliable their convergence is.
    """
    
    def __init__(self, convergence_threshold: float = 1e-6, max_iterations: int = 100):
        """
        Initialize the convergence analyzer.
        
        Parameters
        ----------
        convergence_threshold : float
            Threshold for considering convergence achieved
        max_iterations : int
            Maximum number of iterations to test
        """
        self.convergence_threshold = convergence_threshold
        self.max_iterations = max_iterations
    
    def analyze_convergence_rate(
        self, 
        estimator, 
        data: np.ndarray, 
        true_value: Optional[float] = None,
        data_subsets: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Analyze convergence rate of an estimator.
        
        Parameters
        ----------
        estimator : BaseEstimator
            Estimator instance to analyze
        data : np.ndarray
            Full dataset for analysis
        true_value : float, optional
            True parameter value for error calculation
        data_subsets : List[int], optional
            List of subset sizes to test. If None, uses geometric progression.
            
        Returns
        -------
        dict
            Convergence analysis results
        """
        if data_subsets is None:
            # Use geometric progression for subset sizes
            n = len(data)
            data_subsets = []
            # Start with larger minimum size to avoid spectral estimator issues
            current_size = max(100, n // 10)  # Start with at least 100 points or 10% of data
            while current_size <= n:
                data_subsets.append(current_size)
                current_size = int(current_size * 1.3)  # Slower progression
            data_subsets.append(n)  # Include full dataset
        
        estimates = []
        errors = []
        subset_sizes = []
        convergence_flags = []
        
        for subset_size in data_subsets:
            if subset_size > len(data):
                continue
                
            # Use first subset_size points
            subset_data = data[:subset_size]
            
            try:
                # Estimate parameter
                result = estimator.estimate(subset_data)
                estimate = result.get('hurst_parameter', None)
                
                if estimate is not None:
                    estimates.append(estimate)
                    subset_sizes.append(subset_size)
                    
                    # Calculate error if true value is provided
                    if true_value is not None:
                        error = abs(estimate - true_value)
                        errors.append(error)
                    else:
                        errors.append(None)
                    
                    # Check convergence
                    if len(estimates) > 1:
                        convergence = abs(estimates[-1] - estimates[-2]) < self.convergence_threshold
                        convergence_flags.append(convergence)
                    else:
                        convergence_flags.append(False)
                        
            except Exception as e:
                warnings.warn(f"Failed to estimate for subset size {subset_size}: {e}")
                continue
        
        if len(estimates) < 2:
            return {
                'convergence_rate': None,
                'convergence_achieved': False,
                'final_estimate': estimates[0] if estimates else None,
                'convergence_iteration': None,
                'stability_metric': None,
                'subset_sizes': subset_sizes,
                'estimates': estimates,
                'errors': errors
            }
        
        # Calculate convergence rate
        convergence_rate = self._calculate_convergence_rate(estimates, subset_sizes)
        
        # Find convergence point
        convergence_iteration = None
        for i, converged in enumerate(convergence_flags):
            if converged:
                convergence_iteration = i + 1
                break
        
        # Calculate stability metric
        stability_metric = self._calculate_stability_metric(estimates)
        
        return {
            'convergence_rate': convergence_rate,
            'convergence_achieved': convergence_iteration is not None,
            'convergence_iteration': convergence_iteration,
            'final_estimate': estimates[-1],
            'stability_metric': stability_metric,
            'subset_sizes': subset_sizes,
            'estimates': estimates,
            'errors': errors,
            'convergence_flags': convergence_flags
        }
    
    def _calculate_convergence_rate(self, estimates: List[float], subset_sizes: List[int]) -> float:
        """
        Calculate the rate of convergence.
        
        Parameters
        ----------
        estimates : List[float]
            List of estimates
        subset_sizes : List[int]
            List of corresponding subset sizes
            
        Returns
        -------
        float
            Convergence rate (negative value indicates convergence)
        """
        if len(estimates) < 3:
            return None
        
        # Use log-log regression to estimate convergence rate
        # log(error) = a * log(n) + b
        errors = np.abs(np.diff(estimates))
        n_values = np.array(subset_sizes[1:])
        
        # Remove zero errors to avoid log(0)
        valid_indices = errors > 0
        if np.sum(valid_indices) < 2:
            return None
        
        log_errors = np.log(errors[valid_indices])
        log_n = np.log(n_values[valid_indices])
        
        try:
            # Fit linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_n, log_errors)
            return slope
        except:
            return None
    
    def _calculate_stability_metric(self, estimates: List[float]) -> float:
        """
        Calculate stability metric based on variance of estimates.
        
        Parameters
        ----------
        estimates : List[float]
            List of estimates
            
        Returns
        -------
        float
            Stability metric (lower is more stable)
        """
        if len(estimates) < 2:
            return None
        
        # Use coefficient of variation as stability metric
        estimates_array = np.array(estimates)
        mean_estimate = np.mean(estimates_array)
        std_estimate = np.std(estimates_array)
        
        if mean_estimate == 0:
            return None
        
        return std_estimate / abs(mean_estimate)


class MeanSignedErrorAnalyzer:
    """
    Analyzer for mean signed error and bias assessment.
    
    This class provides methods to calculate mean signed error and
    assess systematic bias in estimators.
    """
    
    def __init__(self):
        """Initialize the mean signed error analyzer."""
        pass
    
    def calculate_mean_signed_error(
        self, 
        estimates: List[float], 
        true_values: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate mean signed error and related metrics.
        
        Parameters
        ----------
        estimates : List[float]
            List of estimated values
        true_values : List[float]
            List of true values
            
        Returns
        -------
        dict
            Mean signed error analysis results
        """
        if len(estimates) != len(true_values):
            raise ValueError("Estimates and true values must have the same length")
        
        estimates_array = np.array(estimates)
        true_values_array = np.array(true_values)
        
        # Calculate signed errors
        signed_errors = estimates_array - true_values_array
        
        # Calculate metrics
        mean_signed_error = np.mean(signed_errors)
        mean_absolute_error = np.mean(np.abs(signed_errors))
        root_mean_squared_error = np.sqrt(np.mean(signed_errors**2))
        
        # Calculate bias metrics
        bias_percentage = (mean_signed_error / np.mean(np.abs(true_values_array))) * 100
        
        # Test for significant bias
        t_stat, p_value = stats.ttest_1samp(signed_errors, 0)
        
        # Calculate confidence interval for bias
        std_error = np.std(signed_errors, ddof=1) / np.sqrt(len(signed_errors))
        confidence_interval = stats.t.interval(
            0.95, 
            len(signed_errors) - 1, 
            loc=mean_signed_error, 
            scale=std_error
        )
        
        return {
            'mean_signed_error': mean_signed_error,
            'mean_absolute_error': mean_absolute_error,
            'root_mean_squared_error': root_mean_squared_error,
            'bias_percentage': bias_percentage,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant_bias': p_value < 0.05,
            'confidence_interval_95': confidence_interval,
            'std_error': std_error,
            'signed_errors': signed_errors.tolist(),
            'estimates': estimates,
            'true_values': true_values
        }
    
    def analyze_bias_pattern(
        self, 
        estimates: List[float], 
        true_values: List[float],
        additional_variables: Optional[Dict[str, List[float]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze bias patterns and relationships with other variables.
        
        Parameters
        ----------
        estimates : List[float]
            List of estimated values
        true_values : List[float]
            List of true values
        additional_variables : Dict[str, List[float]], optional
            Additional variables to analyze bias relationships with
            
        Returns
        -------
        dict
            Bias pattern analysis results
        """
        mse_results = self.calculate_mean_signed_error(estimates, true_values)
        signed_errors = mse_results['signed_errors']
        
        bias_patterns = {
            'overestimation_frequency': np.sum(np.array(signed_errors) > 0) / len(signed_errors),
            'underestimation_frequency': np.sum(np.array(signed_errors) < 0) / len(signed_errors),
            'zero_error_frequency': np.sum(np.array(signed_errors) == 0) / len(signed_errors),
            'error_range': (np.min(signed_errors), np.max(signed_errors)),
            'error_skewness': stats.skew(signed_errors) if len(signed_errors) > 2 else 0.0,
            'error_kurtosis': stats.kurtosis(signed_errors) if len(signed_errors) > 3 else 0.0
        }
        
        # Analyze relationships with additional variables
        variable_correlations = {}
        if additional_variables:
            for var_name, var_values in additional_variables.items():
                if len(var_values) == len(signed_errors):
                    try:
                        # Check for constant input
                        if np.std(var_values) == 0:
                            variable_correlations[var_name] = {
                                'correlation': None,
                                'p_value': None,
                                'significant': False
                            }
                        else:
                            correlation, p_value = stats.pearsonr(signed_errors, var_values)
                            variable_correlations[var_name] = {
                                'correlation': correlation,
                                'p_value': p_value,
                                'significant': p_value < 0.05
                            }
                    except:
                        variable_correlations[var_name] = {
                            'correlation': None,
                            'p_value': None,
                            'significant': False
                        }
        
        return {
            **mse_results,
            'bias_patterns': bias_patterns,
            'variable_correlations': variable_correlations
        }


class AdvancedPerformanceProfiler:
    """
    Comprehensive performance profiler with convergence and bias analysis.
    
    This class combines convergence analysis and mean signed error analysis
    to provide comprehensive performance profiling for estimators.
    """
    
    def __init__(self, convergence_threshold: float = 1e-6, max_iterations: int = 100):
        """
        Initialize the advanced performance profiler.
        
        Parameters
        ----------
        convergence_threshold : float
            Threshold for convergence detection
        max_iterations : int
            Maximum iterations for convergence analysis
        """
        self.convergence_analyzer = ConvergenceAnalyzer(convergence_threshold, max_iterations)
        self.mse_analyzer = MeanSignedErrorAnalyzer()
    
    def profile_estimator_performance(
        self,
        estimator,
        data: np.ndarray,
        true_value: Optional[float] = None,
        n_monte_carlo: int = 100,
        data_subsets: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive performance profiling of an estimator.
        
        Parameters
        ----------
        estimator : BaseEstimator
            Estimator to profile
        data : np.ndarray
            Dataset for analysis
        true_value : float, optional
            True parameter value
        n_monte_carlo : int
            Number of Monte Carlo simulations for bias analysis
        data_subsets : List[int], optional
            Subset sizes for convergence analysis
            
        Returns
        -------
        dict
            Comprehensive performance profile
        """
        # Basic performance metrics
        start_time = time.time()
        try:
            result = estimator.estimate(data)
            execution_time = time.time() - start_time
            success = True
            error_message = None
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            error_message = str(e)
            result = None
        
        # Convergence analysis
        convergence_results = None
        if success and true_value is not None:
            convergence_results = self.convergence_analyzer.analyze_convergence_rate(
                estimator, data, true_value, data_subsets
            )
        
        # Monte Carlo bias analysis
        bias_results = None
        if success and true_value is not None and n_monte_carlo > 0:
            bias_results = self._monte_carlo_bias_analysis(
                estimator, data, true_value, n_monte_carlo
            )
        
        return {
            'basic_performance': {
                'success': success,
                'execution_time': execution_time,
                'error_message': error_message,
                'result': result
            },
            'convergence_analysis': convergence_results,
            'bias_analysis': bias_results,
            'comprehensive_score': self._calculate_comprehensive_score(
                success, execution_time, convergence_results, bias_results
            )
        }
    
    def _monte_carlo_bias_analysis(
        self,
        estimator,
        data: np.ndarray,
        true_value: float,
        n_simulations: int
    ) -> Dict[str, Any]:
        """
        Perform Monte Carlo bias analysis.
        
        Parameters
        ----------
        estimator : BaseEstimator
            Estimator to analyze
        data : np.ndarray
            Original dataset
        true_value : float
            True parameter value
        n_simulations : int
            Number of Monte Carlo simulations
            
        Returns
        -------
        dict
            Monte Carlo bias analysis results
        """
        estimates = []
        execution_times = []
        
        for i in range(n_simulations):
            # Add small random noise to create variations
            noise_level = 0.01 * np.std(data)
            noisy_data = data + np.random.normal(0, noise_level, len(data))
            
            start_time = time.time()
            try:
                result = estimator.estimate(noisy_data)
                estimate = result.get('hurst_parameter', None)
                if estimate is not None:
                    estimates.append(estimate)
                    execution_times.append(time.time() - start_time)
            except:
                continue
        
        if len(estimates) == 0:
            return None
        
        # Create true values list (all same value)
        true_values = [true_value] * len(estimates)
        
        # Calculate bias metrics
        bias_results = self.mse_analyzer.analyze_bias_pattern(
            estimates, true_values, 
            additional_variables={'execution_time': execution_times}
        )
        
        return bias_results
    
    def _calculate_comprehensive_score(
        self,
        success: bool,
        execution_time: float,
        convergence_results: Optional[Dict[str, Any]],
        bias_results: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate comprehensive performance score.
        
        Parameters
        ----------
        success : bool
            Whether estimation was successful
        execution_time : float
            Execution time
        convergence_results : dict, optional
            Convergence analysis results
        bias_results : dict, optional
            Bias analysis results
            
        Returns
        -------
        float
            Comprehensive performance score (0-1, higher is better)
        """
        if not success:
            return 0.0
        
        score = 1.0
        
        # Execution time penalty (normalize to reasonable range)
        if execution_time > 1.0:  # Penalize if takes more than 1 second
            score *= max(0.1, 1.0 / execution_time)
        
        # Convergence bonus
        if convergence_results and convergence_results.get('convergence_achieved'):
            score *= 1.2  # 20% bonus for convergence
        
        # Bias penalty
        if bias_results:
            mse = bias_results.get('mean_signed_error', 0)
            if abs(mse) > 0.1:  # Penalize significant bias
                score *= max(0.5, 1.0 - abs(mse))
        
        return min(1.0, max(0.0, score))


def calculate_convergence_rate(estimates: List[float], subset_sizes: List[int]) -> float:
    """
    Calculate convergence rate from estimates and subset sizes.
    
    Parameters
    ----------
    estimates : List[float]
        List of estimates
    subset_sizes : List[int]
        List of corresponding subset sizes
        
    Returns
    -------
    float
        Convergence rate
    """
    analyzer = ConvergenceAnalyzer()
    return analyzer._calculate_convergence_rate(estimates, subset_sizes)


def calculate_mean_signed_error(estimates: List[float], true_values: List[float]) -> Dict[str, Any]:
    """
    Calculate mean signed error and related metrics.
    
    Parameters
    ----------
    estimates : List[float]
        List of estimated values
    true_values : List[float]
        List of true values
        
    Returns
    -------
    dict
        Mean signed error analysis results
    """
    analyzer = MeanSignedErrorAnalyzer()
    return analyzer.calculate_mean_signed_error(estimates, true_values)


def profile_estimator_performance(
    estimator,
    data: np.ndarray,
    true_value: Optional[float] = None,
    n_monte_carlo: int = 100
) -> Dict[str, Any]:
    """
    Profile estimator performance with advanced metrics.
    
    Parameters
    ----------
    estimator : BaseEstimator
        Estimator to profile
    data : np.ndarray
        Dataset for analysis
    true_value : float, optional
        True parameter value
    n_monte_carlo : int
        Number of Monte Carlo simulations
        
    Returns
    -------
    dict
        Performance profile with convergence and bias analysis
    """
    profiler = AdvancedPerformanceProfiler()
    return profiler.profile_estimator_performance(
        estimator, data, true_value, n_monte_carlo
    )
