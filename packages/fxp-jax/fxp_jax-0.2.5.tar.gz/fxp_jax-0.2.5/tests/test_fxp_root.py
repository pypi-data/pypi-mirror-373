import jax
import jax.numpy as jnp
from jax import random

from fxp_jax import fxp_root

import pytest

# Increase precision to 64 bit
jax.config.update("jax_enable_x64", True)


@pytest.mark.parametrize(
    "N, accelerator",
    [
        (1000, "None"),
        (1000, "SQUAREM"),
    ],
)
def test_fxp_root(N: int, accelerator: str):
    a = random.uniform(random.PRNGKey(111), (N, 1))
    b = random.uniform(random.PRNGKey(112), (1, 1))

    def fun(x: jnp.ndarray) -> tuple[jnp.ndarray, jnp.ndarray]:
        y = a + x @ b
        return y, y - x

    fxp = fxp_root(
        fun,
        accelerator=accelerator,
    )
    result = fxp.solve(jnp.zeros_like(a))

    assert jnp.allclose(result.x, fxp.fun(result.x)[0]), (
        f"Error: {jnp.linalg.norm(fxp.fun(result.x)[1])}"
    )


@pytest.mark.parametrize(
    "N, accelerator",
    [
        (1000, "None"),
        (1000, "SQUAREM"),
    ],
)
def test_fxp_root_args(N: int, accelerator: str):
    a = random.uniform(random.PRNGKey(111), (N, 1))
    b = random.uniform(random.PRNGKey(112), (1, 1))

    def fun_args(x: jnp.ndarray, *args) -> tuple[jnp.ndarray, jnp.ndarray]:
        a, b = args
        y = a + x @ b
        return y, y - x

    fxp_args = fxp_root(
        fun_args,
        accelerator=accelerator,
    )
    result_args = fxp_args.solve(jnp.zeros_like(a), a, b)

    x, z = fxp_args.fun(result_args.x, a, b)

    assert jnp.allclose(result_args.x, x), f"Error: {jnp.linalg.norm(z)}"


@pytest.mark.parametrize(
    "N, accelerator",
    [
        (1000, "None"),
        (1000, "SQUAREM"),
    ],
)
def test_fxp_root_kwargs(N: int, accelerator: str):
    a = random.uniform(random.PRNGKey(111), (N, 1))
    b = random.uniform(random.PRNGKey(112), (1, 1))

    def fun_kwargs(x: jnp.ndarray, **kwargs) -> tuple[jnp.ndarray, jnp.ndarray]:
        a, b = kwargs["a"], kwargs["b"]
        y = a + x @ b
        return y, y - x

    fxp_kwargs = fxp_root(
        fun_kwargs,
        accelerator=accelerator,
    )
    result_kwargs = fxp_kwargs.solve(jnp.zeros_like(a), a=a, b=b)

    x, z = fxp_kwargs.fun(result_kwargs.x, a=a, b=b)

    assert jnp.allclose(result_kwargs.x, x), f"Error: {jnp.linalg.norm(z)}"


@pytest.mark.parametrize(
    "N, accelerator",
    [
        (1000, "None"),
        (1000, "SQUAREM"),
    ],
)
def test_fxp_root_args_kwargs(N: int, accelerator: str):
    a = random.uniform(random.PRNGKey(111), (N, 1))
    b = random.uniform(random.PRNGKey(112), (1, 1))

    def fun_args_kwargs(
        x: jnp.ndarray, *args, **kwargs
    ) -> tuple[jnp.ndarray, jnp.ndarray]:
        a = args[0]
        b = kwargs["b"]
        y = a + x @ b
        return y, y - x

    fxp_args_kwargs = fxp_root(
        fun_args_kwargs,
        accelerator=accelerator,
    )
    result_args_kwargs = fxp_args_kwargs.solve(jnp.zeros_like(a), a, b=b)

    x, z = fxp_args_kwargs.fun(result_args_kwargs.x, a, b=b)

    assert jnp.allclose(result_args_kwargs.x, x), f"Error: {jnp.linalg.norm(z)}"
