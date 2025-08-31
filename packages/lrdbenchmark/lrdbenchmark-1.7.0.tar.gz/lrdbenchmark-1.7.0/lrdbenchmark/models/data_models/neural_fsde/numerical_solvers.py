"""
Numerical Solvers for Stochastic Differential Equations

This module provides multiple numerical schemes for solving SDEs:
- Euler-Maruyama: Simple, stable, O(Δt) convergence
- Milstein: Higher order, O(Δt^(2H)) for fBm, more accurate
- Heun: Predictor-corrector, better stability
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Any, Optional, Union
import warnings

# Try to import JAX for high-performance solving
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, grad

    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    jax = None
    jnp = None


class SDESolver:
    """
    Base class for SDE numerical solvers.

    This class provides a unified interface for different numerical
    schemes for solving stochastic differential equations.
    """

    def __init__(self, method: str = "auto"):
        """
        Initialize the SDE solver.

        Parameters
        ----------
        method : str, default='auto'
            Solver method: 'euler', 'milstein', 'heun', or 'auto'
        """
        self.method = method
        self.available_methods = ["euler", "milstein", "heun"]

        if method == "auto":
            self.method = "milstein"  # Best default for fSDEs

    def solve(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: np.ndarray,
        t_span: np.ndarray,
        hurst: float = 0.5,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve the SDE using the specified method.

        Parameters
        ----------
        drift_func : Callable
            Drift function f(x, t)
        diffusion_func : Callable
            Diffusion function g(x, t)
        x0 : np.ndarray
            Initial condition
        t_span : np.ndarray
            Time points for solution
        hurst : float, default=0.5
            Hurst parameter for fractional processes
        **kwargs
            Additional keyword arguments

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Solution trajectory and time points
        """
        if self.method == "euler":
            return self._euler_maruyama(
                drift_func, diffusion_func, x0, t_span, hurst, **kwargs
            )
        elif self.method == "milstein":
            return self._milstein(
                drift_func, diffusion_func, x0, t_span, hurst, **kwargs
            )
        elif self.method == "heun":
            return self._heun(drift_func, diffusion_func, x0, t_span, hurst, **kwargs)
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def _euler_maruyama(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: np.ndarray,
        t_span: np.ndarray,
        hurst: float = 0.5,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Euler-Maruyama scheme for SDEs.

        X_{n+1} = X_n + f(X_n, t_n) Δt + g(X_n, t_n) ΔB^H_n

        Parameters
        ----------
        drift_func : Callable
            Drift function f(x, t)
        diffusion_func : Callable
            Diffusion function g(x, t)
        x0 : np.ndarray
            Initial condition
        t_span : np.ndarray
            Time points
        hurst : float
            Hurst parameter
        **kwargs
            Additional arguments

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Solution and time points
        """
        n_steps = len(t_span)
        dt = t_span[1] - t_span[0]  # Assume uniform time steps

        # Initialize solution
        x = np.zeros((n_steps, len(x0)))
        x[0] = x0

        # Generate fractional Brownian motion increments
        from .fractional_brownian_motion import generate_fbm_increments

        fbm_increments = generate_fbm_increments(n_steps, hurst, dt)

        # Solve using Euler-Maruyama
        for i in range(1, n_steps):
            t_prev = t_span[i - 1]
            x_prev = x[i - 1]

            # Compute drift and diffusion
            drift = drift_func(x_prev, t_prev)
            diffusion = diffusion_func(x_prev, t_prev)

            # Euler-Maruyama step
            x[i] = x_prev + drift * dt + diffusion * fbm_increments[i - 1]

        return x, t_span

    def _milstein(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: np.ndarray,
        t_span: np.ndarray,
        hurst: float = 0.5,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Milstein scheme for SDEs (higher order convergence).

        For fBm with Hurst parameter H:
        X_{n+1} = X_n + f(X_n, t_n) Δt + g(X_n, t_n) ΔB^H_n +
                   0.5 * g(X_n, t_n) * g'(X_n, t_n) * [(ΔB^H_n)² - Δt^(2H)]

        Parameters
        ----------
        drift_func : Callable
            Drift function f(x, t)
        diffusion_func : Callable
            Diffusion function g(x, t)
        x0 : np.ndarray
            Initial condition
        t_span : np.ndarray
            Time points
        hurst : float
            Hurst parameter
        **kwargs
            Additional arguments

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Solution and time points
        """
        n_steps = len(t_span)
        dt = t_span[1] - t_span[0]

        # Initialize solution
        x = np.zeros((n_steps, len(x0)))
        x[0] = x0

        # Generate fractional Brownian motion increments
        from .fractional_brownian_motion import generate_fbm_increments

        fbm_increments = generate_fbm_increments(n_steps, hurst, dt)

        # Check if we can compute diffusion derivative
        try:
            # Try to compute derivative numerically
            diffusion_deriv = self._compute_diffusion_derivative(
                diffusion_func, x0, t_span[0]
            )
            use_milstein = True
        except:
            warnings.warn(
                "Cannot compute diffusion derivative, falling back to Euler-Maruyama"
            )
            use_milstein = False

        # Solve using Milstein scheme
        for i in range(1, n_steps):
            t_prev = t_span[i - 1]
            x_prev = x[i - 1]

            # Compute drift and diffusion
            drift = drift_func(x_prev, t_prev)
            diffusion = diffusion_func(x_prev, t_prev)

            if use_milstein:
                # Compute diffusion derivative
                diffusion_deriv = self._compute_diffusion_derivative(
                    diffusion_func, x_prev, t_prev
                )

                # Milstein correction term
                fbm_increment = fbm_increments[i - 1]
                milstein_correction = (
                    0.5
                    * diffusion
                    * diffusion_deriv
                    * (fbm_increment**2 - dt ** (2 * hurst))
                )

                x[i] = (
                    x_prev
                    + drift * dt
                    + diffusion * fbm_increment
                    + milstein_correction
                )
            else:
                # Fallback to Euler-Maruyama
                x[i] = x_prev + drift * dt + diffusion * fbm_increments[i - 1]

        return x, t_span

    def _heun(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: np.ndarray,
        t_span: np.ndarray,
        hurst: float = 0.5,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Heun scheme for SDEs (predictor-corrector method).

        Predictor: X_pred = X_n + f(X_n, t_n) Δt + g(X_n, t_n) ΔB^H_n
        Corrector: X_{n+1} = X_n + 0.5 * [f(X_n, t_n) + f(X_pred, t_{n+1})] Δt +
                              0.5 * [g(X_n, t_n) + g(X_pred, t_{n+1})] ΔB^H_n

        Parameters
        ----------
        drift_func : Callable
            Drift function f(x, t)
        diffusion_func : Callable
            Diffusion function g(x, t)
        x0 : np.ndarray
            Initial condition
        t_span : np.ndarray
            Time points
        hurst : float
            Hurst parameter
        **kwargs
            Additional arguments

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Solution and time points
        """
        n_steps = len(t_span)
        dt = t_span[1] - t_span[0]

        # Initialize solution
        x = np.zeros((n_steps, len(x0)))
        x[0] = x0

        # Generate fractional Brownian motion increments
        from .fractional_brownian_motion import generate_fbm_increments

        fbm_increments = generate_fbm_increments(n_steps, hurst, dt)

        # Solve using Heun scheme
        for i in range(1, n_steps):
            t_prev = t_span[i - 1]
            t_curr = t_span[i]
            x_prev = x[i - 1]

            # Predictor step
            drift_prev = drift_func(x_prev, t_prev)
            diffusion_prev = diffusion_func(x_prev, t_prev)
            fbm_increment = fbm_increments[i - 1]

            x_pred = x_prev + drift_prev * dt + diffusion_prev * fbm_increment

            # Corrector step
            drift_curr = drift_func(x_pred, t_curr)
            diffusion_curr = diffusion_func(x_pred, t_curr)

            x[i] = (
                x_prev
                + 0.5 * (drift_prev + drift_curr) * dt
                + 0.5 * (diffusion_prev + diffusion_curr) * fbm_increment
            )

        return x, t_span

    def _compute_diffusion_derivative(
        self, diffusion_func: Callable, x: np.ndarray, t: float, eps: float = 1e-6
    ) -> np.ndarray:
        """
        Compute derivative of diffusion function numerically.

        Parameters
        ----------
        diffusion_func : Callable
            Diffusion function g(x, t)
        x : np.ndarray
            State vector
        t : float
            Time
        eps : float
            Small perturbation for numerical derivative

        Returns
        -------
        np.ndarray
            Derivative of diffusion function
        """
        # For scalar diffusion, compute scalar derivative
        if np.isscalar(diffusion_func(x, t)):
            g_plus = diffusion_func(x + eps, t)
            g_minus = diffusion_func(x - eps, t)
            return (g_plus - g_minus) / (2 * eps)
        else:
            # For vector diffusion, compute Jacobian
            n = len(x)
            jacobian = np.zeros((n, n))

            for i in range(n):
                x_plus = x.copy()
                x_plus[i] += eps
                x_minus = x.copy()
                x_minus[i] -= eps

                g_plus = diffusion_func(x_plus, t)
                g_minus = diffusion_func(x_minus, t)

                jacobian[:, i] = (g_plus - g_minus) / (2 * eps)

            return jacobian


class JAXSDESolver(SDESolver):
    """
    JAX-optimized SDE solver for high-performance computation.

    This solver leverages JAX's JIT compilation and GPU acceleration
    for efficient SDE solving.
    """

    def __init__(self, method: str = "auto"):
        """Initialize JAX SDE solver."""
        if not JAX_AVAILABLE:
            raise RuntimeError("JAX not available")

        super().__init__(method)

        # JIT-compile the solver functions
        self._jit_solve = jit(self._solve_jax)

    def solve(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: np.ndarray,
        t_span: np.ndarray,
        hurst: float = 0.5,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve SDE using JAX-optimized methods.

        Parameters
        ----------
        drift_func : Callable
            Drift function (should be JAX-compatible)
        diffusion_func : Callable
            Diffusion function (should be JAX-compatible)
        x0 : np.ndarray
            Initial condition
        t_span : np.ndarray
            Time points
        hurst : float
            Hurst parameter
        **kwargs
            Additional arguments

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Solution and time points
        """
        # Convert to JAX arrays
        x0_jax = jnp.array(x0)
        t_span_jax = jnp.array(t_span)

        # Solve using JAX
        solution = self._jit_solve(
            drift_func, diffusion_func, x0_jax, t_span_jax, hurst
        )

        # Convert back to numpy
        return np.array(solution), t_span

    def _solve_jax(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: jnp.ndarray,
        t_span: jnp.ndarray,
        hurst: float,
    ) -> jnp.ndarray:
        """JAX implementation of SDE solving."""
        if self.method == "euler":
            return self._euler_maruyama_jax(
                drift_func, diffusion_func, x0, t_span, hurst
            )
        elif self.method == "milstein":
            return self._milstein_jax(drift_func, diffusion_func, x0, t_span, hurst)
        elif self.method == "heun":
            return self._heun_jax(drift_func, diffusion_func, x0, t_span, hurst)
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def _euler_maruyama_jax(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: jnp.ndarray,
        t_span: jnp.ndarray,
        hurst: float,
    ) -> jnp.ndarray:
        """JAX-optimized Euler-Maruyama scheme."""
        n_steps = len(t_span)
        dt = t_span[1] - t_span[0]

        # Initialize solution
        x = jnp.zeros((n_steps, len(x0)))
        x = x.at[0].set(x0)

        # Generate fBm increments (using JAX)
        fbm_increments = self._generate_fbm_increments_jax(n_steps, hurst, dt)

        # Define single step function
        def step(x_prev, i):
            t_prev = t_span[i - 1]
            drift = drift_func(x_prev, t_prev)
            diffusion = diffusion_func(x_prev, t_prev)
            fbm_increment = fbm_increments[i - 1]

            x_next = x_prev + drift * dt + diffusion * fbm_increment
            return x_next, x_next

        # Solve using scan for efficiency
        _, x_solution = jax.lax.scan(step, x0, jnp.arange(1, n_steps))

        # Combine initial condition with solution
        x = x.at[1:].set(x_solution)

        return x

    def _milstein_jax(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: jnp.ndarray,
        t_span: jnp.ndarray,
        hurst: float,
    ) -> jnp.ndarray:
        """JAX-optimized Milstein scheme."""
        n_steps = len(t_span)
        dt = t_span[1] - t_span[0]

        # Initialize solution
        x = jnp.zeros((n_steps, len(x0)))
        x = x.at[0].set(x0)

        # Generate fBm increments
        fbm_increments = self._generate_fbm_increments_jax(n_steps, hurst, dt)

        # Define single step function with Milstein correction
        def step(x_prev, i):
            t_prev = t_span[i - 1]
            drift = drift_func(x_prev, t_prev)
            diffusion = diffusion_func(x_prev, t_prev)
            fbm_increment = fbm_increments[i - 1]

            # Milstein correction (simplified for scalar case)
            if jnp.isscalar(diffusion):
                milstein_correction = (
                    0.5 * diffusion * diffusion * (fbm_increment**2 - dt ** (2 * hurst))
                )
            else:
                # For vector case, use simplified correction
                milstein_correction = (
                    0.5 * jnp.sum(diffusion**2) * (fbm_increment**2 - dt ** (2 * hurst))
                )

            x_next = (
                x_prev + drift * dt + diffusion * fbm_increment + milstein_correction
            )
            return x_next, x_next

        # Solve using scan
        _, x_solution = jax.lax.scan(step, x0, jnp.arange(1, n_steps))

        # Combine initial condition with solution
        x = x.at[1:].set(x_solution)

        return x

    def _heun_jax(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: jnp.ndarray,
        t_span: jnp.ndarray,
        hurst: float,
    ) -> jnp.ndarray:
        """JAX-optimized Heun scheme."""
        n_steps = len(t_span)
        dt = t_span[1] - t_span[0]

        # Initialize solution
        x = jnp.zeros((n_steps, len(x0)))
        x = x.at[0].set(x0)

        # Generate fBm increments
        fbm_increments = self._generate_fbm_increments_jax(n_steps, hurst, dt)

        # Define single step function
        def step(x_prev, i):
            t_prev = t_span[i - 1]
            t_curr = t_span[i]

            # Predictor step
            drift_prev = drift_func(x_prev, t_prev)
            diffusion_prev = diffusion_func(x_prev, t_prev)
            fbm_increment = fbm_increments[i - 1]

            x_pred = x_prev + drift_prev * dt + diffusion_prev * fbm_increment

            # Corrector step
            drift_curr = drift_func(x_pred, t_curr)
            diffusion_curr = diffusion_func(x_pred, t_curr)

            x_next = (
                x_prev
                + 0.5 * (drift_prev + drift_curr) * dt
                + 0.5 * (diffusion_prev + diffusion_curr) * fbm_increment
            )

            return x_next, x_next

        # Solve using scan
        _, x_solution = jax.lax.scan(step, x0, jnp.arange(1, n_steps))

        # Combine initial condition with solution
        x = x.at[1:].set(x_solution)

        return x

    def _generate_fbm_increments_jax(
        self, n_steps: int, hurst: float, dt: float
    ) -> jnp.ndarray:
        """Generate fBm increments using JAX."""
        # Use the JAX method from our fBm generator
        from .fractional_brownian_motion import FractionalBrownianMotionGenerator

        generator = FractionalBrownianMotionGenerator(method="jax")
        increments = generator.generate_increments(n_steps, hurst, dt)

        return jnp.array(increments)


class AdaptiveSDESolver:
    """
    Adaptive SDE solver with automatic method selection.

    This solver automatically chooses the best method based on
    problem characteristics and accuracy requirements.
    """

    def __init__(self, tolerance: float = 1e-6):
        """
        Initialize adaptive solver.

        Parameters
        ----------
        tolerance : float
            Error tolerance for adaptive stepping
        """
        self.tolerance = tolerance
        self.solvers = {
            "euler": SDESolver("euler"),
            "milstein": SDESolver("milstein"),
            "heun": SDESolver("heun"),
        }

        if JAX_AVAILABLE:
            self.solvers["jax"] = JAXSDESolver("milstein")

    def solve(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: np.ndarray,
        t_span: np.ndarray,
        hurst: float = 0.5,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve SDE with adaptive method selection.

        Parameters
        ----------
        drift_func : Callable
            Drift function
        diffusion_func : Callable
            Diffusion function
        x0 : np.ndarray
            Initial condition
        t_span : np.ndarray
            Time points
        hurst : float
            Hurst parameter
        **kwargs
            Additional arguments

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Solution and time points
        """
        # Auto-select method based on problem characteristics
        method = self._auto_select_method(drift_func, diffusion_func, x0, t_span, hurst)

        # Solve using selected method
        solver = self.solvers[method]
        return solver.solve(drift_func, diffusion_func, x0, t_span, hurst, **kwargs)

    def _auto_select_method(
        self,
        drift_func: Callable,
        diffusion_func: Callable,
        x0: np.ndarray,
        t_span: np.ndarray,
        hurst: float,
    ) -> str:
        """
        Automatically select the best solver method.

        Selection criteria:
        - JAX: Available and large problem size
        - Milstein: High accuracy requirements, moderate size
        - Heun: Stability concerns
        - Euler: Simple, small problems
        """
        n_steps = len(t_span)
        dt = t_span[1] - t_span[0] if len(t_span) > 1 else 1.0

        # Check if JAX is available and problem is large
        if "jax" in self.solvers and n_steps > 1000:
            return "jax"

        # Check accuracy requirements
        if dt < 0.01 and hurst > 0.5:  # High accuracy, long memory
            return "milstein"

        # Check stability concerns
        if dt > 0.1:  # Large time steps
            return "heun"

        # Default to Euler for simple cases
        return "euler"

    def get_solver_info(self) -> Dict[str, Any]:
        """Get information about available solvers."""
        info = {
            "available_solvers": list(self.solvers.keys()),
            "recommended_solver": "auto",
            "performance_notes": {
                "euler": "Simple, stable, O(Δt) convergence",
                "milstein": "Higher order, O(Δt^(2H)) for fBm",
                "heun": "Predictor-corrector, better stability",
                "jax": "GPU-accelerated, fastest for large problems",
            },
        }

        if "jax" in self.solvers:
            info["recommended_solver"] = "jax"
        else:
            info["recommended_solver"] = "milstein"

        return info


# Convenience functions
def solve_sde(
    drift_func: Callable,
    diffusion_func: Callable,
    x0: np.ndarray,
    t_span: np.ndarray,
    hurst: float = 0.5,
    method: str = "auto",
    **kwargs,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function for solving SDEs.

    Parameters
    ----------
    drift_func : Callable
        Drift function f(x, t)
    diffusion_func : Callable
        Diffusion function g(x, t)
    x0 : np.ndarray
        Initial condition
    t_span : np.ndarray
        Time points
    hurst : float
        Hurst parameter
    method : str
        Solver method
    **kwargs
        Additional arguments

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Solution and time points
    """
    if method == "auto":
        solver = AdaptiveSDESolver()
    else:
        solver = SDESolver(method)

    return solver.solve(drift_func, diffusion_func, x0, t_span, hurst, **kwargs)
