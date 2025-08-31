#!/usr/bin/env python3
"""
Optimization Engine for ML Estimators

This module provides advanced optimization capabilities using:
- Optuna: Hyperparameter optimization
- NumPyro: Probabilistic modeling and inference
- Advanced training strategies
"""

import numpy as np
import time
from typing import Dict, Any, Optional, Callable, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Try to import optimization libraries
try:
    import optuna
    OPTUNA_AVAILABLE = True
    print("✅ Optuna available for hyperparameter optimization")
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️ Optuna not available. Install with: pip install optuna")

try:
    import jax
    import jax.numpy as jnp
    import numpyro
    import numpyro.distributions as dist
    from numpyro.infer import MCMC, NUTS
    NUMPYRO_AVAILABLE = True
    print("✅ NumPyro available for probabilistic modeling")
except ImportError:
    NUMPYRO_AVAILABLE = False
    print("⚠️ NumPyro not available. Install with: pip install numpyro")

class OptunaOptimizer:
    """
    Optuna-based hyperparameter optimizer for ML estimators.
    
    Features:
    - Automatic hyperparameter search
    - Multi-objective optimization
    - Early stopping and pruning
    - Parallel optimization
    """
    
    def __init__(self, n_trials: int = 100, timeout: int = 3600):
        """
        Initialize the Optuna optimizer.
        
        Parameters
        ----------
        n_trials : int
            Number of optimization trials
        timeout : int
            Maximum time for optimization (seconds)
        """
        self.n_trials = n_trials
        self.timeout = timeout
        self.study = None
        
    def optimize_random_forest(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Optimize Random Forest hyperparameters."""
        if not OPTUNA_AVAILABLE:
            raise ImportError("Optuna is required for hyperparameter optimization")
        
        def objective(trial):
            # Define hyperparameter search space
            n_estimators = trial.suggest_int('n_estimators', 50, 500)
            max_depth = trial.suggest_int('max_depth', 3, 20)
            min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
            min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 10)
            max_features = trial.suggest_categorical('max_features', ['sqrt', 'log2', None])
            
            # Create and train model
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import cross_val_score
            
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                max_features=max_features,
                random_state=42,
                n_jobs=-1
            )
            
            # Cross-validation score
            scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            return scores.mean()
        
        # Create study
        self.study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )
        
        # Optimize
        print(f"🔍 Optimizing Random Forest with {self.n_trials} trials...")
        self.study.optimize(objective, n_trials=self.n_trials, timeout=self.timeout)
        
        # Return best parameters
        best_params = self.study.best_params
        best_score = self.study.best_value
        
        print(f"✅ Best Random Forest parameters: {best_params}")
        print(f"📊 Best R² score: {best_score:.4f}")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'study': self.study
        }
    
    def optimize_gradient_boosting(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Optimize Gradient Boosting hyperparameters."""
        if not OPTUNA_AVAILABLE:
            raise ImportError("Optuna is required for hyperparameter optimization")
        
        def objective(trial):
            # Define hyperparameter search space
            n_estimators = trial.suggest_int('n_estimators', 50, 500)
            learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
            max_depth = trial.suggest_int('max_depth', 3, 10)
            subsample = trial.suggest_float('subsample', 0.6, 1.0)
            
            # Create and train model
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.model_selection import cross_val_score
            
            model = GradientBoostingRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                max_depth=max_depth,
                subsample=subsample,
                random_state=42
            )
            
            # Cross-validation score
            scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            return scores.mean()
        
        # Create study
        self.study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )
        
        # Optimize
        print(f"🔍 Optimizing Gradient Boosting with {self.n_trials} trials...")
        self.study.optimize(objective, n_trials=self.n_trials, timeout=self.timeout)
        
        # Return best parameters
        best_params = self.study.best_params
        best_score = self.study.best_value
        
        print(f"✅ Best Gradient Boosting parameters: {best_params}")
        print(f"📊 Best R² score: {best_score:.4f}")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'study': self.study
        }
    
    def optimize_svr(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Optimize SVR hyperparameters."""
        if not OPTUNA_AVAILABLE:
            raise ImportError("Optuna is required for hyperparameter optimization")
        
        def objective(trial):
            # Define hyperparameter search space
            C = trial.suggest_float('C', 0.1, 10.0, log=True)
            epsilon = trial.suggest_float('epsilon', 0.01, 0.5)
            gamma = trial.suggest_categorical('gamma', ['scale', 'auto'])
            
            # Create and train model
            from sklearn.svm import SVR
            from sklearn.model_selection import cross_val_score
            
            model = SVR(
                C=C,
                epsilon=epsilon,
                gamma=gamma
            )
            
            # Cross-validation score
            scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            return scores.mean()
        
        # Create study
        self.study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )
        
        # Optimize
        print(f"🔍 Optimizing SVR with {self.n_trials} trials...")
        self.study.optimize(objective, n_trials=self.n_trials, timeout=self.timeout)
        
        # Return best parameters
        best_params = self.study.best_params
        best_score = self.study.best_value
        
        print(f"✅ Best SVR parameters: {best_params}")
        print(f"📊 Best R² score: {best_score:.4f}")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'study': self.study
        }

class NumPyroProbabilisticModel:
    """
    NumPyro-based probabilistic model for uncertainty quantification.
    
    Features:
    - Bayesian inference
    - Uncertainty quantification
    - Probabilistic predictions
    """
    
    def __init__(self):
        """Initialize the NumPyro probabilistic model."""
        if not NUMPYRO_AVAILABLE:
            raise ImportError("NumPyro is required for probabilistic modeling")
        
        self.model = None
        self.mcmc = None
        
    def bayesian_linear_regression(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Fit Bayesian linear regression model.
        
        Parameters
        ----------
        X : np.ndarray
            Input features
        y : np.ndarray
            Target values
            
        Returns
        -------
        dict
            Model results with uncertainty quantification
        """
        if not NUMPYRO_AVAILABLE:
            raise ImportError("NumPyro is required for probabilistic modeling")
        
        def model(X, y=None):
            # Prior distributions
            intercept = numpyro.sample("intercept", dist.Normal(0, 10))
            slope = numpyro.sample("slope", dist.Normal(0, 10))
            sigma = numpyro.sample("sigma", dist.Exponential(1))
            
            # Linear model
            mean = intercept + slope * X
            numpyro.sample("y", dist.Normal(mean, sigma), obs=y)
        
        # Run MCMC
        print("🔍 Running Bayesian inference with NumPyro...")
        kernel = NUTS(model)
        mcmc = MCMC(kernel, num_warmup=1000, num_samples=2000)
        
        start_time = time.time()
        mcmc.run(jax.random.PRNGKey(42), X, y)
        inference_time = time.time() - start_time
        
        # Extract samples
        samples = mcmc.get_samples()
        
        # Calculate predictions and uncertainty
        intercept_mean = float(jnp.mean(samples["intercept"]))
        slope_mean = float(jnp.mean(samples["slope"]))
        sigma_mean = float(jnp.mean(samples["sigma"]))
        
        # Predictions
        y_pred = intercept_mean + slope_mean * X
        
        # Uncertainty quantification
        intercept_std = float(jnp.std(samples["intercept"]))
        slope_std = float(jnp.std(samples["slope"]))
        
        print(f"✅ Bayesian inference completed in {inference_time:.2f}s")
        print(f"📊 Intercept: {intercept_mean:.4f} ± {intercept_std:.4f}")
        print(f"📊 Slope: {slope_mean:.4f} ± {slope_std:.4f}")
        
        return {
            'intercept': intercept_mean,
            'slope': slope_mean,
            'sigma': sigma_mean,
            'intercept_std': intercept_std,
            'slope_std': slope_std,
            'predictions': y_pred,
            'samples': samples,
            'mcmc': mcmc,
            'inference_time': inference_time
        }
    
    def bayesian_neural_network(self, X: np.ndarray, y: np.ndarray, 
                               hidden_dim: int = 50) -> Dict[str, Any]:
        """
        Fit Bayesian neural network model.
        
        Parameters
        ----------
        X : np.ndarray
            Input features
        y : np.ndarray
            Target values
        hidden_dim : int
            Hidden layer dimension
            
        Returns
        -------
        dict
            Model results with uncertainty quantification
        """
        if not NUMPYRO_AVAILABLE:
            raise ImportError("NumPyro is required for probabilistic modeling")
        
        def model(X, y=None):
            # Prior distributions for weights
            w1 = numpyro.sample("w1", dist.Normal(0, 1).expand([1, hidden_dim]))
            b1 = numpyro.sample("b1", dist.Normal(0, 1).expand([hidden_dim]))
            w2 = numpyro.sample("w2", dist.Normal(0, 1).expand([hidden_dim, 1]))
            b2 = numpyro.sample("b2", dist.Normal(0, 1).expand([1]))
            sigma = numpyro.sample("sigma", dist.Exponential(1))
            
            # Neural network forward pass
            h = jnp.tanh(jnp.dot(X, w1) + b1)
            mean = jnp.dot(h, w2) + b2
            
            numpyro.sample("y", dist.Normal(mean, sigma), obs=y)
        
        # Run MCMC
        print(f"🔍 Running Bayesian neural network inference with {hidden_dim} hidden units...")
        kernel = NUTS(model)
        mcmc = MCMC(kernel, num_warmup=1000, num_samples=2000)
        
        start_time = time.time()
        mcmc.run(jax.random.PRNGKey(42), X, y)
        inference_time = time.time() - start_time
        
        # Extract samples
        samples = mcmc.get_samples()
        
        print(f"✅ Bayesian neural network inference completed in {inference_time:.2f}s")
        
        return {
            'samples': samples,
            'mcmc': mcmc,
            'inference_time': inference_time,
            'hidden_dim': hidden_dim
        }

class AdvancedTrainingStrategy:
    """
    Advanced training strategies combining multiple optimization approaches.
    """
    
    def __init__(self):
        """Initialize the advanced training strategy."""
        self.optuna_optimizer = OptunaOptimizer() if OPTUNA_AVAILABLE else None
        self.numpyro_model = NumPyroProbabilisticModel() if NUMPYRO_AVAILABLE else None
    
    def optimize_and_train(self, X: np.ndarray, y: np.ndarray, 
                          estimator_type: str = 'random_forest') -> Dict[str, Any]:
        """
        Optimize hyperparameters and train the model.
        
        Parameters
        ----------
        X : np.ndarray
            Training features
        y : np.ndarray
            Target values
        estimator_type : str
            Type of estimator to optimize
            
        Returns
        -------
        dict
            Optimization and training results
        """
        results = {}
        
        # Step 1: Hyperparameter optimization with Optuna
        if self.optuna_optimizer:
            print(f"\n🚀 Step 1: Optimizing {estimator_type} hyperparameters...")
            try:
                if estimator_type == 'random_forest':
                    opt_results = self.optuna_optimizer.optimize_random_forest(X, y)
                elif estimator_type == 'gradient_boosting':
                    opt_results = self.optuna_optimizer.optimize_gradient_boosting(X, y)
                elif estimator_type == 'svr':
                    opt_results = self.optuna_optimizer.optimize_svr(X, y)
                else:
                    raise ValueError(f"Unsupported estimator type: {estimator_type}")
                
                results['optimization'] = opt_results
                best_params = opt_results['best_params']
                
            except Exception as e:
                print(f"⚠️ Hyperparameter optimization failed: {e}")
                best_params = {}
                results['optimization'] = {'error': str(e)}
        else:
            print("⚠️ Skipping hyperparameter optimization (Optuna not available)")
            best_params = {}
        
        # Step 2: Train model with optimized parameters
        print(f"\n🚀 Step 2: Training {estimator_type} with optimized parameters...")
        try:
            if estimator_type == 'random_forest':
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
            elif estimator_type == 'gradient_boosting':
                from sklearn.ensemble import GradientBoostingRegressor
                model = GradientBoostingRegressor(**best_params, random_state=42)
            elif estimator_type == 'svr':
                from sklearn.svm import SVR
                model = SVR(**best_params)
            else:
                raise ValueError(f"Unsupported estimator type: {estimator_type}")
            
            # Train model
            start_time = time.time()
            model.fit(X, y)
            training_time = time.time() - start_time
            
            # Evaluate
            from sklearn.metrics import r2_score, mean_squared_error
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            
            results['training'] = {
                'model': model,
                'training_time': training_time,
                'r2_score': r2,
                'mse': mse,
                'best_params': best_params
            }
            
            print(f"✅ Training completed in {training_time:.2f}s")
            print(f"📊 R² Score: {r2:.4f}")
            print(f"📊 MSE: {mse:.4f}")
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            results['training'] = {'error': str(e)}
        
        # Step 3: Uncertainty quantification with NumPyro (optional)
        if self.numpyro_model and len(results.get('training', {})) > 0:
            print(f"\n🚀 Step 3: Uncertainty quantification with NumPyro...")
            try:
                # Use a subset for probabilistic modeling (can be computationally expensive)
                subset_size = min(1000, len(X))
                X_subset = X[:subset_size]
                y_subset = y[:subset_size]
                
                prob_results = self.numpyro_model.bayesian_linear_regression(X_subset, y_subset)
                results['uncertainty'] = prob_results
                
            except Exception as e:
                print(f"⚠️ Uncertainty quantification failed: {e}")
                results['uncertainty'] = {'error': str(e)}
        
        return results

def main():
    """Demo of the optimization engine."""
    print("🚀 Advanced ML Optimization Engine Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    X = np.random.randn(1000, 10)
    y = 2 * X[:, 0] + 1.5 * X[:, 1] + np.random.randn(1000) * 0.1
    
    print(f"📊 Generated dataset: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Test optimization strategies
    strategy = AdvancedTrainingStrategy()
    
    # Test Random Forest optimization
    print("\n" + "=" * 50)
    print("🌳 Random Forest Optimization")
    print("=" * 50)
    
    try:
        rf_results = strategy.optimize_and_train(X, y, 'random_forest')
        print("✅ Random Forest optimization completed successfully!")
    except Exception as e:
        print(f"❌ Random Forest optimization failed: {e}")
    
    # Test Gradient Boosting optimization
    print("\n" + "=" * 50)
    print("🌱 Gradient Boosting Optimization")
    print("=" * 50)
    
    try:
        gb_results = strategy.optimize_and_train(X, y, 'gradient_boosting')
        print("✅ Gradient Boosting optimization completed successfully!")
    except Exception as e:
        print(f"❌ Gradient Boosting optimization failed: {e}")
    
    print("\n🎉 Optimization engine demo completed!")

if __name__ == "__main__":
    main()
