import jax.numpy as jnp
from jax import lax

from simple_pytree import Pytree, dataclass

from typing import Callable


@dataclass
class FixedPointState(Pytree):
    """State information

    Attributes:
        iter_num (int): iteration number
        step_norm (jnp.ndarray): norm of step
        root_norm (jnp.ndarray): norm of root
    """

    iter_num: int
    step_norm: jnp.ndarray
    root_norm: jnp.ndarray


@dataclass
class OptStep(Pytree):
    """Current guess of the solution and state information

    Attributes:
        x (jnp.ndarray): current guess of the solution
        state (FixedPointState): state information
    """

    x: jnp.ndarray
    state: FixedPointState


@dataclass
class fxp_root(Pytree, mutable=True):
    """Initialize the solver state.

    Attributes:
        fun (Callable): system of fixed-point equations
        step_tol (float): tolerance level for step norm
        root_tol (float): tolerance level for root norm
        max_iter (int): maximum number of iterations
    """

    fun: Callable

    step_tol: float = 1e-8
    root_tol: float = 1e-6
    max_iter: int = 1000
    accelerator: str | None = None

    def _init_state(self) -> FixedPointState:
        """Initialize the solver state.

        Returns:
            state (FixedPointState)
        """
        return FixedPointState(
            iter_num=0,
            step_norm=jnp.asarray(jnp.inf),
            root_norm=jnp.asarray(jnp.inf),
        )

    def _update_none(self, fxp: Callable, step: OptStep, *args, **kwargs) -> OptStep:
        """Update fixed-point

        Args:
            fxp (Callable): system of fixed-point equations
            step (OptStep): current states

        Returns:
            step_next (OptStep): updated states
        """
        x_next, root = fxp(step.x, *args, **kwargs)

        next_state = FixedPointState(
            iter_num=step.state.iter_num + 1,
            step_norm=jnp.linalg.norm(x_next - step.x),
            root_norm=jnp.linalg.norm(root),
        )
        return OptStep(x=x_next, state=next_state)

    def _update_squarem(self, fxp: Callable, step: OptStep, *args, **kwargs) -> OptStep:
        """Update fixed-point by SQUAREM

        Args:
            fxp (Callable): system of fixed-point equations
            step (OptStep): current states

        Returns:
            step_next (OptStep): updated states
        """

        x1 = fxp(step.x, *args, **kwargs)[0]  # first fixed-point step
        x2 = fxp(x1, *args, **kwargs)[0]  # second fixed-point step

        # Accelerated step
        r = x1 - step.x  # change
        v = x2 - x1 - r  # curvature

        alpha = -jnp.sqrt(jnp.sum(r**2) / jnp.sum(v**2))

        x_next, root = fxp(step.x - 2 * alpha * r + (alpha**2) * v, *args, **kwargs)

        next_state = FixedPointState(
            iter_num=step.state.iter_num + 1,
            step_norm=jnp.linalg.norm(x_next - step.x),
            root_norm=jnp.linalg.norm(root),
        )
        return OptStep(x=x_next, state=next_state)

    def _condition(self, step: OptStep) -> jnp.ndarray:
        """Conditions for continuation of while loop

        Args:
            step (OptStep): current states

        Returns:
            condition (jnp.ndarray): boolean

        """
        # Evaluate stopping criterions
        cond1 = step.state.root_norm > self.root_tol  # stop if root is zero
        cond2 = step.state.step_norm > self.step_tol  # stop if step is zero
        cond3 = (
            step.state.iter_num < self.max_iter
        )  # stop if maximum iteration is reached
        cond4 = jnp.any(jnp.isnan(step.x)) == 0  # stop if any value is NaN

        cond_tol = jnp.logical_and(cond1, cond2)  # step or root is close to zero
        return jnp.all(jnp.logical_and(jnp.logical_and(cond_tol, cond3), cond4))

    def solve(self, guess: jnp.ndarray, *args, **kwargs) -> OptStep:
        """Solve fixed-point equation by fixed point iterations

        Args:
            guess (jnp.ndarray): initial guess

        Returns:
            state (OptStep): dataclass containing the solution to the fixed-point

        """

        if self.accelerator == "SQUAREM":
            # Set up accelerated fixed-point equations (SQUAREM)
            def func(step):
                return self._update_squarem(self.fun, step, *args, **kwargs)
        else:
            # Set up fixed-point equations
            def func(step):
                return self._update_none(self.fun, step, *args, **kwargs)

        # Execute fixed-point iterations
        result = lax.while_loop(
            body_fun=func,
            cond_fun=self._condition,
            init_val=OptStep(x=guess, state=self._init_state()),
        )

        # Print number of iterations and norm of root and step
        print(
            f"FXP output: iterations={result.state.iter_num}, root norm={result.state.root_norm}, step norm={result.state.step_norm}"
        )
        return result
