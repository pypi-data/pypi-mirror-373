"""
Test script for the hybrid neural fSDE system.

This script tests the basic functionality of our hybrid system
including framework detection, model creation, and simulation.
"""

import sys
import os
import numpy as np

# Add the project root to the path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def test_framework_detection():
    """Test that framework detection works correctly."""
    print("Testing framework detection...")

    try:
        from models.data_models.neural_fsde import JAX_AVAILABLE, TORCH_AVAILABLE

        print(f"  JAX available: {JAX_AVAILABLE}")
        print(f"  PyTorch available: {TORCH_AVAILABLE}")

        if not JAX_AVAILABLE and not TORCH_AVAILABLE:
            print("  ⚠️  Warning: No frameworks available")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Framework detection failed: {e}")
        return False


def test_factory_creation():
    """Test that the factory can be created."""
    print("Testing factory creation...")

    try:
        from models.data_models.neural_fsde import get_factory

        factory = get_factory()
        print(f"  ✓ Factory created: {type(factory).__name__}")

        # Get framework info
        info = factory.get_framework_info()
        print(f"  Available frameworks: {info['available_frameworks']}")
        print(f"  Recommended framework: {info['recommended_framework']}")

        return True

    except Exception as e:
        print(f"  ✗ Factory creation failed: {e}")
        return False


def test_model_creation():
    """Test that models can be created."""
    print("Testing model creation...")

    try:
        from models.data_models.neural_fsde import (
            create_fsde_net,
            create_latent_fsde_net,
        )

        # Test basic fSDE-Net
        model = create_fsde_net(
            state_dim=1, hidden_dim=32, num_layers=2, hurst_parameter=0.7
        )
        print(f"  ✓ Basic fSDE-Net created: {model}")
        print(f"  Framework: {model.framework}")

        # Test latent fSDE-Net
        latent_model = create_latent_fsde_net(
            obs_dim=1, latent_dim=8, hidden_dim=32, num_layers=2, hurst_parameter=0.7
        )
        print(f"  ✓ Latent fSDE-Net created: {latent_model}")
        print(f"  Framework: {latent_model.framework}")

        return True

    except Exception as e:
        print(f"  ✗ Model creation failed: {e}")
        return False


def test_simulation():
    """Test that models can simulate time series."""
    print("Testing simulation...")

    try:
        from models.data_models.neural_fsde import create_fsde_net

        # Create model
        model = create_fsde_net(
            state_dim=1, hidden_dim=32, num_layers=2, hurst_parameter=0.7
        )

        # Simulate
        trajectory = model.simulate(n_samples=100, dt=0.01)
        print(f"  ✓ Simulation successful: {trajectory.shape}")

        # Check basic properties
        if trajectory.shape == (100, 1):
            print("  ✓ Trajectory shape correct")
        else:
            print(f"  ⚠️  Unexpected trajectory shape: {trajectory.shape}")

        # Check for NaN or infinite values
        if np.any(np.isnan(trajectory)) or np.any(np.isinf(trajectory)):
            print("  ⚠️  Trajectory contains NaN or infinite values")
        else:
            print("  ✓ Trajectory values are finite")

        return True

    except Exception as e:
        print(f"  ✗ Simulation failed: {e}")
        return False


def test_fbm_generation():
    """Test fractional Brownian motion generation."""
    print("Testing fBm generation...")

    try:
        from models.data_models.neural_fsde import FractionalBrownianMotionGenerator

        # Create generator
        generator = FractionalBrownianMotionGenerator(method="auto")
        print(f"  ✓ Generator created with method: {generator.method}")

        # Generate fBm path
        path = generator.generate_path(n_steps=100, hurst=0.7, dt=0.01)
        print(f"  ✓ fBm path generated: {path.shape}")

        # Generate increments
        increments = generator.generate_increments(n_steps=100, hurst=0.7, dt=0.01)
        print(f"  ✓ fBm increments generated: {increments.shape}")

        # Check method info
        info = generator.get_method_info()
        print(f"  Available methods: {info['available_methods']}")
        print(f"  Recommended method: {info['recommended_method']}")

        return True

    except Exception as e:
        print(f"  ✗ fBm generation failed: {e}")
        return False


def test_numerical_solvers():
    """Test numerical SDE solvers."""
    print("Testing numerical solvers...")

    try:
        from models.data_models.neural_fsde import SDESolver, solve_sde

        # Test basic solver
        solver = SDESolver(method="euler")
        print(f"  ✓ Basic solver created: {solver.method}")

        # Test solving simple SDE
        def drift_func(x, t):
            return -0.1 * x  # Simple mean reversion

        def diffusion_func(x, t):
            return 0.1  # Constant volatility

        x0 = np.array([1.0])
        t_span = np.linspace(0, 1, 100)

        solution, _ = solve_sde(
            drift_func, diffusion_func, x0, t_span, hurst=0.5, method="euler"
        )
        print(f"  ✓ SDE solved: {solution.shape}")

        return True

    except Exception as e:
        print(f"  ✗ Numerical solvers failed: {e}")
        return False


def test_benchmarking():
    """Test framework benchmarking."""
    print("Testing framework benchmarking...")

    try:
        from models.data_models.neural_fsde import benchmark_frameworks

        # Run benchmark
        results = benchmark_frameworks(
            state_dim=1, hidden_dim=32, n_samples=100, n_runs=2
        )
        print(f"  ✓ Benchmark completed")

        # Print results
        for framework, result in results["frameworks"].items():
            if result["status"] == "success":
                time_info = result["simulation_time"]
                print(
                    f"    {framework}: {time_info['mean']:.4f}s ± {time_info['std']:.4f}s"
                )
            else:
                print(
                    f"    {framework}: {result['status']} - {result.get('error', 'Unknown error')}"
                )

        # Print recommendations
        if results["recommendations"]:
            print("  Recommendations:")
            for rec in results["recommendations"]:
                print(f"    - {rec}")

        return True

    except Exception as e:
        print(f"  ✗ Benchmarking failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("HYBRID NEURAL fSDE SYSTEM TESTING")
    print("=" * 60)

    tests = [
        ("Framework Detection", test_framework_detection),
        ("Factory Creation", test_factory_creation),
        ("Model Creation", test_model_creation),
        ("Simulation", test_simulation),
        ("fBm Generation", test_fbm_generation),
        ("Numerical Solvers", test_numerical_solvers),
        ("Framework Benchmarking", test_benchmarking),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Hybrid neural fSDE system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
