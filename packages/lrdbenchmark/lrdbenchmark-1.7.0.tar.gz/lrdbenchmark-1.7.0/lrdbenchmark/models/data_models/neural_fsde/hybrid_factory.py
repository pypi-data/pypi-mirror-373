"""
Hybrid Factory for Neural fSDE Models

This module provides a factory pattern for creating neural fSDE models
with automatic framework selection based on availability and requirements.
"""

from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import warnings

from .base_neural_fsde import BaseNeuralFSDE
from .fractional_brownian_motion import FractionalBrownianMotionGenerator

# Try to import JAX and PyTorch implementations
try:
    from .jax_fsde_net import JAXfSDENet, JAXLatentFractionalNet, JAX_AVAILABLE
except ImportError:
    JAX_AVAILABLE = False

try:
    from .torch_fsde_net import TorchfSDENet, TorchLatentFractionalNet, TORCH_AVAILABLE
except ImportError:
    TORCH_AVAILABLE = False


class NeuralFSDEFactory:
    """
    Factory for creating neural fSDE models with automatic framework selection.

    This factory automatically chooses the best available framework:
    - JAX: High performance, GPU acceleration
    - PyTorch: Compatibility, debugging, CPU/GPU support
    - Fallback: Error if neither is available
    """

    def __init__(self, preferred_framework: str = "auto"):
        """
        Initialize the factory.

        Parameters
        ----------
        preferred_framework : str, default='auto'
            Preferred framework: 'jax', 'torch', or 'auto'
        """
        self.preferred_framework = preferred_framework
        self.available_frameworks = self._get_available_frameworks()

        if not self.available_frameworks:
            raise RuntimeError("Neither JAX nor PyTorch is available")

    def _get_available_frameworks(self) -> List[str]:
        """Get list of available frameworks."""
        frameworks = []
        if JAX_AVAILABLE:
            frameworks.append("jax")
        if TORCH_AVAILABLE:
            frameworks.append("torch")
        return frameworks

    def get_framework_info(self) -> Dict[str, Any]:
        """Get information about available frameworks."""
        info = {
            "available_frameworks": self.available_frameworks,
            "preferred_framework": self.preferred_framework,
            "framework_details": {},
        }

        if "jax" in self.available_frameworks:
            info["framework_details"]["jax"] = {
                "status": "available",
                "description": "High-performance JAX implementation with GPU acceleration",
                "advantages": [
                    "JIT compilation",
                    "GPU acceleration",
                    "Functional programming",
                ],
                "best_for": [
                    "Large-scale computation",
                    "GPU environments",
                    "Production use",
                ],
            }

        if "torch" in self.available_frameworks:
            info["framework_details"]["torch"] = {
                "status": "available",
                "description": "PyTorch implementation for compatibility and debugging",
                "advantages": ["Mature ecosystem", "Easy debugging", "CPU/GPU support"],
                "best_for": ["Development", "Debugging", "CPU environments"],
            }

        # Auto-select best framework
        if self.preferred_framework == "auto":
            if "jax" in self.available_frameworks:
                info["recommended_framework"] = "jax"
            else:
                info["recommended_framework"] = "torch"
        else:
            info["recommended_framework"] = self.preferred_framework

        return info

    def create_fsde_net(
        self,
        state_dim: int,
        hidden_dim: int,
        num_layers: int = 3,
        hurst_parameter: float = 0.7,
        framework: str = "auto",
        **kwargs,
    ) -> BaseNeuralFSDE:
        """
        Create a neural fSDE network.

        Parameters
        ----------
        state_dim : int
            State space dimension
        hidden_dim : int
            Hidden layer dimension
        num_layers : int, default=3
            Number of hidden layers
        hurst_parameter : float, default=0.7
            Initial Hurst parameter
        framework : str, default='auto'
            Framework to use: 'jax', 'torch', or 'auto'
        **kwargs
            Additional keyword arguments

        Returns
        -------
        BaseNeuralFSDE
            Neural fSDE model instance
        """
        # Determine framework to use
        selected_framework = self._select_framework(framework)

        # Create model based on selected framework
        if selected_framework == "jax":
            return JAXfSDENet(
                state_dim=state_dim,
                hidden_dim=hidden_dim,
                num_layers=num_layers,
                hurst_parameter=hurst_parameter,
                **kwargs,
            )
        elif selected_framework == "torch":
            return TorchfSDENet(
                state_dim=state_dim,
                hidden_dim=hidden_dim,
                num_layers=num_layers,
                hurst_parameter=hurst_parameter,
                **kwargs,
            )
        else:
            raise ValueError(f"Unknown framework: {selected_framework}")

    def create_latent_fsde_net(
        self,
        obs_dim: int,
        latent_dim: int,
        hidden_dim: int,
        num_layers: int = 3,
        hurst_parameter: float = 0.7,
        framework: str = "auto",
        **kwargs,
    ) -> BaseNeuralFSDE:
        """
        Create a latent fractional SDE network.

        Parameters
        ----------
        obs_dim : int
            Observation space dimension
        latent_dim : int
            Latent space dimension
        hidden_dim : int
            Hidden layer dimension
        num_layers : int, default=3
            Number of hidden layers
        hurst_parameter : float, default=0.7
            Initial Hurst parameter
        framework : str, default='auto'
            Framework to use: 'jax', 'torch', or 'auto'
        **kwargs
            Additional keyword arguments

        Returns
        -------
        BaseNeuralFSDE
            Latent fractional SDE model instance
        """
        # Determine framework to use
        selected_framework = self._select_framework(framework)

        # Create model based on selected framework
        if selected_framework == "jax":
            return JAXLatentFractionalNet(
                obs_dim=obs_dim,
                latent_dim=latent_dim,
                hidden_dim=hidden_dim,
                num_layers=num_layers,
                hurst_parameter=hurst_parameter,
                **kwargs,
            )
        elif selected_framework == "torch":
            return TorchLatentFractionalNet(
                obs_dim=obs_dim,
                latent_dim=latent_dim,
                hidden_dim=hidden_dim,
                num_layers=num_layers,
                hurst_parameter=hurst_parameter,
                **kwargs,
            )
        else:
            raise ValueError(f"Unknown framework: {selected_framework}")

    def _select_framework(self, framework: str) -> str:
        """
        Select the appropriate framework based on availability and preferences.

        Parameters
        ----------
        framework : str
            Requested framework

        Returns
        -------
        str
            Selected framework
        """
        if framework == "auto":
            # Auto-select based on preferences and availability
            if self.preferred_framework == "jax" and "jax" in self.available_frameworks:
                return "jax"
            elif (
                self.preferred_framework == "torch"
                and "torch" in self.available_frameworks
            ):
                return "torch"
            else:
                # Default to best available
                if "jax" in self.available_frameworks:
                    return "jax"
                else:
                    return "torch"
        else:
            # Specific framework requested
            if framework not in self.available_frameworks:
                available = ", ".join(self.available_frameworks)
                warnings.warn(
                    f"Requested framework '{framework}' not available. "
                    f"Available: {available}. Falling back to best available."
                )
                return self._select_framework("auto")
            return framework

    def benchmark_frameworks(
        self,
        state_dim: int = 1,
        hidden_dim: int = 32,
        n_samples: int = 1000,
        n_runs: int = 5,
    ) -> Dict[str, Any]:
        """
        Benchmark available frameworks for performance comparison.

        Parameters
        ----------
        state_dim : int, default=1
            State space dimension
        hidden_dim : int, default=32
            Hidden layer dimension
        n_samples : int, default=1000
            Number of samples for simulation
        n_runs : int, default=5
            Number of benchmark runs

        Returns
        -------
        Dict[str, Any]
            Benchmark results
        """
        import time
        import numpy as np

        results = {"frameworks": {}, "recommendations": []}

        # Benchmark each available framework
        for framework in self.available_frameworks:
            try:
                # Create model
                if framework == "jax":
                    model = JAXfSDENet(state_dim, hidden_dim)
                else:
                    model = TorchfSDENet(state_dim, hidden_dim)

                # Benchmark simulation
                times = []
                for _ in range(n_runs):
                    start_time = time.time()
                    _ = model.simulate(n_samples)
                    end_time = time.time()
                    times.append(end_time - start_time)

                # Calculate statistics
                mean_time = np.mean(times)
                std_time = np.std(times)

                results["frameworks"][framework] = {
                    "simulation_time": {
                        "mean": mean_time,
                        "std": std_time,
                        "runs": times,
                    },
                    "samples_per_second": n_samples / mean_time,
                    "status": "success",
                }

            except Exception as e:
                results["frameworks"][framework] = {"status": "error", "error": str(e)}

        # Generate recommendations
        successful_frameworks = [
            f
            for f, result in results["frameworks"].items()
            if result["status"] == "success"
        ]

        if successful_frameworks:
            # Find fastest framework
            fastest = min(
                successful_frameworks,
                key=lambda f: results["frameworks"][f]["simulation_time"]["mean"],
            )

            results["recommendations"].append(f"Fastest framework: {fastest}")

            # Performance comparison
            for framework in successful_frameworks:
                if framework != fastest:
                    fastest_time = results["frameworks"][fastest]["simulation_time"][
                        "mean"
                    ]
                    framework_time = results["frameworks"][framework][
                        "simulation_time"
                    ]["mean"]
                    speedup = fastest_time / framework_time
                    results["recommendations"].append(
                        f"{fastest} is {speedup:.2f}x faster than {framework}"
                    )

        return results

    def create_ensemble(
        self,
        state_dim: int,
        hidden_dim: int,
        num_layers: int = 3,
        hurst_parameter: float = 0.7,
        **kwargs,
    ) -> Dict[str, BaseNeuralFSDE]:
        """
        Create an ensemble of models across all available frameworks.

        Parameters
        ----------
        state_dim : int
            State space dimension
        hidden_dim : int
            Hidden layer dimension
        num_layers : int, default=3
            Number of hidden layers
        hurst_parameter : float, default=0.7
            Initial Hurst parameter
        **kwargs
            Additional keyword arguments

        Returns
        -------
        Dict[str, BaseNeuralFSDE]
            Dictionary of models indexed by framework
        """
        ensemble = {}

        for framework in self.available_frameworks:
            try:
                if framework == "jax":
                    model = JAXfSDENet(
                        state_dim=state_dim,
                        hidden_dim=hidden_dim,
                        num_layers=num_layers,
                        hurst_parameter=hurst_parameter,
                        **kwargs,
                    )
                else:
                    model = TorchfSDENet(
                        state_dim=state_dim,
                        hidden_dim=hidden_dim,
                        num_layers=num_layers,
                        hurst_parameter=hurst_parameter,
                        **kwargs,
                    )

                ensemble[framework] = model

            except Exception as e:
                warnings.warn(f"Failed to create {framework} model: {e}")

        return ensemble


# Global factory instance
_factory = None


def get_factory() -> NeuralFSDEFactory:
    """Get the global factory instance."""
    global _factory
    if _factory is None:
        _factory = NeuralFSDEFactory()
    return _factory


def create_fsde_net(*args, **kwargs) -> BaseNeuralFSDE:
    """Convenience function to create fSDE-Net using global factory."""
    return get_factory().create_fsde_net(*args, **kwargs)


def create_latent_fsde_net(*args, **kwargs) -> BaseNeuralFSDE:
    """Convenience function to create Latent fSDE-Net using global factory."""
    return get_factory().create_latent_fsde_net(*args, **kwargs)


def benchmark_frameworks(*args, **kwargs) -> Dict[str, Any]:
    """Convenience function to benchmark frameworks using global factory."""
    return get_factory().benchmark_frameworks(*args, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Test factory creation
    factory = NeuralFSDEFactory()

    print("Available frameworks:", factory.available_frameworks)
    print("Framework info:", factory.get_framework_info())

    # Test model creation
    try:
        model = factory.create_fsde_net(state_dim=1, hidden_dim=32)
        print(f"Created {model.framework} model: {model}")

        # Test simulation
        trajectory = model.simulate(n_samples=100)
        print(f"Generated trajectory shape: {trajectory.shape}")

    except Exception as e:
        print(f"Error creating model: {e}")

    # Test benchmarking
    try:
        results = factory.benchmark_frameworks()
        print("Benchmark results:", results)
    except Exception as e:
        print(f"Error benchmarking: {e}")
