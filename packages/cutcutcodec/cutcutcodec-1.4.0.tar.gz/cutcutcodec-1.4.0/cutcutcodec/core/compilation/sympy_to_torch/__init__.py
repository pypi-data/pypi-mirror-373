#!/usr/bin/env python3

"""The folowing optimisations are performed.

* Compute in place as possible.
* Compatible with gpu input tensor.
* Conserve the type: float32, float64 or complex.
* Factorisation of redondant patern for minimizing operations.
* Cached the constants paterns.
* Prealocate the internal tensors taken in account the broadcasting of shapes.
"""

from cutcutcodec.core.compilation.sympy_to_torch.lambdify import Lambdify

__all__ = ["Lambdify"]
