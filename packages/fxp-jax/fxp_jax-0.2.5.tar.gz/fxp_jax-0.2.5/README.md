[![PyPI version](https://img.shields.io/pypi/v/fxp-jax.svg)](https://pypi.org/project/fxp-jax/)
[![CI](https://github.com/esbenscriver/fxp-jax/actions/workflows/ci.yml/badge.svg)](https://github.com/esbenscriver/fxp-jax/actions/workflows/ci.yml)
[![CD](https://github.com/esbenscriver/fxp-jax/actions/workflows/cd.yml/badge.svg)](https://github.com/esbenscriver/fxp-jax/actions/workflows/cd.yml)
# Fixed-point solver
fxp-jax is a simple implementation of a fixed-point iteration algorithm for root finding in JAX. The implementation allow the user to solve the system of fixed point equations by standard fixed point iterations and the SQUAREM accelerator, see [Du and Varadhan (2020)](https://doi.org/10.18637/jss.v092.i07).

## Installation

```bash
pip install fxp-jax
```

## Usage

```python

import jax
import jax.numpy as jnp
from jax import random

from fxp_jax import fxp_root

jax.config.update("jax_enable_x64", True)

accelerator = "SQUAREM"

N = 100

a = random.uniform(random.PRNGKey(111), (N,1))
b = random.uniform(random.PRNGKey(112), (1,1))

def fun(x: jnp.ndarray) -> tuple[jnp.ndarray, jnp.ndarray]:
    y = a + x @ b
    return y, y - x

fxp = fxp_root(fun, accelerator=accelerator)

result = fxp.solve(jnp.zeros_like(a))

y, z = fxp.fun(result.x)

print('--------------------------------------------------------')
print(f'System of fixed-point equations is solved: {jnp.allclose(result.x, y)}.')
print(f'Roots are zero: {jnp.allclose(z, 0.0)}.')
print('--------------------------------------------------------')
```
