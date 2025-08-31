"""
Neural Fractional Stochastic Differential Equations (fSDEs)

This module implements neural network-based fractional stochastic differential equations
based on the work by Hayashi & Nakagawa (2022, 2024).

The system provides a hybrid approach with:
- JAX + Equinox: High-performance GPU-accelerated implementation
- PyTorch: Compatibility and debugging implementation
- Automatic framework selection based on availability

References:
- Hayashi, K., & Nakagawa, K. (2022). fSDE-Net: Generating Time Series Data with Long-term Memory.
- Nakagawa, K., & Hayashi, K. (2024). Lf-Net: Generating Fractional Time-Series with Latent Fractional-Net.

Features:
- Multiple numerical schemes: Euler-Maruyama, Milstein, Heun
- Efficient fBm generation: Cholesky, Circulant, JAX-optimized
- Framework switching capability
- Performance benchmarking
"""

# Base classes
from .base_neural_fsde import BaseNeuralFSDE

# Core components
from .fractional_brownian_motion import (
    FractionalBrownianMotionGenerator,
    generate_fbm_path,
    generate_fbm_increments,
)

from .numerical_solvers import SDESolver, JAXSDESolver, AdaptiveSDESolver, solve_sde

# JAX implementations (high performance)
try:
    from .jax_fsde_net import (
        JAXfSDENet,
        JAXLatentFractionalNet,
        JAXMLP,
        create_jax_fsde_net,
        create_jax_latent_fsde_net,
    )

    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

# PyTorch implementations (compatibility)
try:
    from .torch_fsde_net import (
        TorchfSDENet,
        TorchLatentFractionalNet,
        TorchMLP,
        create_torch_fsde_net,
        create_torch_latent_fsde_net,
    )

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Hybrid factory (automatic framework selection)
from .hybrid_factory import (
    NeuralFSDEFactory,
    get_factory,
    create_fsde_net,
    create_latent_fsde_net,
    benchmark_frameworks,
)

# Convenience imports
__all__ = [
    # Base classes
    "BaseNeuralFSDE",
    # Core components
    "FractionalBrownianMotionGenerator",
    "generate_fbm_path",
    "generate_fbm_increments",
    "SDESolver",
    "JAXSDESolver",
    "AdaptiveSDESolver",
    "solve_sde",
    # Factory and utilities
    "NeuralFSDEFactory",
    "get_factory",
    "create_fsde_net",
    "create_latent_fsde_net",
    "benchmark_frameworks",
]

# Add framework-specific exports if available
if JAX_AVAILABLE:
    __all__.extend(
        [
            "JAXfSDENet",
            "JAXLatentFractionalNet",
            "JAXMLP",
            "create_jax_fsde_net",
            "create_jax_latent_fsde_net",
        ]
    )

if TORCH_AVAILABLE:
    __all__.extend(
        [
            "TorchfSDENet",
            "TorchLatentFractionalNet",
            "TorchMLP",
            "create_torch_fsde_net",
            "create_torch_latent_fsde_net",
        ]
    )

# Version info
__version__ = "1.0.0"
__author__ = "Data Modelling and Generation Project"
__description__ = "Hybrid Neural Fractional Stochastic Differential Equations"


# Quick start example
def quick_start_example():
    """
    Quick start example for using the neural fSDE system.

    This demonstrates the basic usage pattern with automatic
    framework selection.
    """
    try:
        # Create a neural fSDE model (auto-selects best framework)
        model = create_fsde_net(
            state_dim=1, hidden_dim=32, num_layers=3, hurst_parameter=0.7
        )

        print(f"Created {model.framework} model: {model}")

        # Simulate time series
        trajectory = model.simulate(n_samples=1000, dt=0.01)
        print(f"Generated trajectory shape: {trajectory.shape}")

        # Get framework information
        factory = get_factory()
        info = factory.get_framework_info()
        print(f"Available frameworks: {info['available_frameworks']}")
        print(f"Recommended framework: {info['recommended_framework']}")

        return model, trajectory

    except Exception as e:
        print(f"Quick start failed: {e}")
        return None, None


# Check availability on import
def check_availability():
    """Check framework availability and print status."""
    print("Neural fSDE System Status:")
    print(f"  JAX available: {JAX_AVAILABLE}")
    print(f"  PyTorch available: {TORCH_AVAILABLE}")

    if JAX_AVAILABLE or TORCH_AVAILABLE:
        try:
            factory = get_factory()
            info = factory.get_framework_info()
            print(f"  Recommended framework: {info['recommended_framework']}")
            print(f"  Available frameworks: {info['available_frameworks']}")
        except Exception as e:
            print(f"  Factory error: {e}")
    else:
        print("  ⚠️  No frameworks available! Install JAX or PyTorch.")


# Run availability check on import
if __name__ == "__main__":
    check_availability()
    print("\nRunning quick start example...")
    model, trajectory = quick_start_example()
else:
    # Only check on import if verbose mode is enabled
    import os

    if os.environ.get("NEURAL_FSDE_VERBOSE", "0") == "1":
        check_availability()
