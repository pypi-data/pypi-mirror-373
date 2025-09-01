#!/usr/bin/env python3

"""Check that the generated function works whell."""

import itertools

from sympy.abc import x, y, z
from sympy.core.mul import Mul
from sympy.functions.elementary.complexes import Abs
from sympy.core.power import Pow
from sympy.functions.elementary.miscellaneous import cbrt, sqrt, Max, Min
from sympy.core.add import Add
from sympy.functions.elementary.trigonometric import cos, exp, sin
import torch

from cutcutcodec.core.compilation.sympy_to_torch import Lambdify


FUNC_R2R = (Abs, cbrt, cos, exp, sin, sqrt)
FUNC_RR2R = (Add, Mul, Pow, Max, Min)


def test_broadcast():
    """Test broadcasting shapes."""
    g_cpu = torch.Generator()
    g_cpu.manual_seed(0)
    args = (
        torch.randn(1, 1, 100, generator=g_cpu),
        torch.randn(1, 100, 1, generator=g_cpu),
        torch.randn(100, 1, 1, generator=g_cpu),
    )
    for func, comp, cst, safe in itertools.product(
        FUNC_RR2R,
        (True, False),
        (set(), {x}, {y}, {z}, {x, y}, {x, z}, {y, z}, {x, y, z}),
        (set(), {x}, {y}, {z}, {x, y}, {x, z}, {y, z}, {x, y, z}),
    ):
        out = Lambdify(
            func(x, func(y, z)), safe=safe, compile=comp, cst_args=cst
        )(*args)
        assert (
            out.shape == torch.broadcast_shapes(*(a.shape for a in args))
        ), (
            f"func {func} comp {comp} cst {cst} safe {safe} "
            f"out_shape {out.shape} in_shapes {(a.shape for a in args)}"
        )


def test_func_r2r_inplace_safe():
    """Check that the values of the input tensor are not modified."""
    g_cpu = torch.Generator()
    g_cpu.manual_seed(0)
    arg = torch.randn(1000, generator=g_cpu)
    arg_clone = arg.clone()
    for func, comp, cst in itertools.product(
        FUNC_R2R,
        (True, False),
        (set(), {x}),
    ):
        Lambdify(func(x), safe={x}, compile=comp, cst_args=cst)(arg)
        assert torch.equal(arg, arg_clone), f"func {func}, comp {comp} cst {cst}"


def test_func_rr2r_inplace_safe():
    """Check that thes values of the input tensor are not modified."""
    g_cpu = torch.Generator()
    g_cpu.manual_seed(0)
    arg_left = torch.randn(1000, generator=g_cpu)
    arg_right = torch.randn(1000, generator=g_cpu)
    arg_left_clone = arg_left.clone()
    arg_right_clone = arg_right.clone()
    for func, comp, cst in itertools.product(
        FUNC_RR2R,
        (True, False),
        (set(), {x}, {y}, {x, y}),
    ):
        Lambdify(
            func(x, y), safe={x, y}, compile=comp, cst_args=cst, shapes={frozenset({x, y})}
        )(arg_left, arg_right)
        assert torch.equal(arg_left, arg_left_clone), f"func {func} comp {comp} cst {cst}"
        assert torch.equal(arg_right, arg_right_clone), f"func {func} comp {comp} cst {cst}"


def test_homogeneous_2r2_dtype():
    """Check that the dtype in conserved in r to r functions."""
    g_cpu = torch.Generator()
    g_cpu.manual_seed(0)
    for dtype in (torch.float32, torch.float64, torch.complex64, torch.complex128):
        arg = torch.randn(1000, generator=g_cpu, dtype=dtype)
        for func, comp, cst in itertools.product(
            FUNC_R2R,
            (True, False),
            (set(), {x}),
        ):
            out = Lambdify(func(x), safe={x}, compile=comp, cst_args=cst)(arg)
            assert out.dtype == dtype, (
                f"func {func}, comp {comp} cst {cst} "
                f"in_dtype {dtype} out_dtype {out.dtype}"
            )


def test_homogeneous_2r2_dtype_empty():
    """Check that the dtype in conserved in r to r functions."""
    g_cpu = torch.Generator()
    g_cpu.manual_seed(0)
    for dtype in (torch.float32, torch.float64, torch.complex64, torch.complex128):
        arg = torch.tensor([], dtype=dtype)
        for func, comp, cst in itertools.product(
            FUNC_R2R,
            (True, False),
            (set(), {x}),
        ):
            out = Lambdify(func(x), safe={x}, compile=comp, cst_args=cst)(arg)
            assert out.dtype == dtype, (
                f"func {func}, comp {comp} cst {cst} "
                f"in_dtype {dtype} out_dtype {out.dtype}"
            )


def test_homogeneous_2r2_shape():
    """Check that the shape is conserved in r to r functions."""
    g_cpu = torch.Generator()
    g_cpu.manual_seed(0)
    for shape in ((0,), (1,), (1, 1), (1, 2, 3, 4)):
        arg = torch.randn(*shape, generator=g_cpu)
        for func, comp, cst in itertools.product(
            FUNC_R2R,
            (True, False),
            (set(), {x}),
        ):
            out = Lambdify(func(x), safe={x}, compile=comp, cst_args=cst)(arg)
            assert out.shape == shape, (
                f"func {func}, comp {comp} cst {cst} "
                f"in_shape {shape} out_shape {out.shape}"
            )
