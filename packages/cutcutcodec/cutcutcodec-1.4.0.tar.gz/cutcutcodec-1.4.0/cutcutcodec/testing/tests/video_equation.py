#!/usr/bin/env python3

"""Perform tests on the ``cutcutcodec.core.generation.video.equation.GeneratorVideoEquation``."""

import pytest
import sympy

from cutcutcodec.core.generation.video.equation import GeneratorVideoEquation


def test_complex_module_part():
    """Check that the real part is used for a complex expression."""
    (stream,) = GeneratorVideoEquation("(3+4*I)/255").out_streams
    assert stream.snapshot(0, (1, 1)).item() == pytest.approx(5/255)


def test_contant():
    """Make sure the numbers are cast in array."""
    (stream,) = GeneratorVideoEquation("0", "1", "t").out_streams
    assert stream.snapshot(0, (5, 4)).shape == (5, 4, 3)
    (stream,) = GeneratorVideoEquation("0", "i").out_streams  # mix cst and array
    assert stream.snapshot(0, (5, 4)).shape == (5, 4, 2)


def test_divide_by_zero():
    """Make sure not failed when divide by 0."""
    (stream,) = GeneratorVideoEquation("1/t").out_streams
    stream.snapshot(0, (1, 1))
    (stream,) = GeneratorVideoEquation("1/sqrt(t)").out_streams
    stream.snapshot(0, (1, 1))
    (stream,) = GeneratorVideoEquation("t**-2").out_streams
    stream.snapshot(0, (1, 1))
    (stream,) = GeneratorVideoEquation("0", "1/j", "1/i").out_streams
    stream.snapshot(0, (3, 3))


def test_input_type():
    """Check that the entries can be of sympy, str and number type."""
    colors = [sympy.sympify("0"), 1 + sympy.Symbol("t", real=True, positive=True)]
    (stream_from_expr,) = GeneratorVideoEquation(*colors).out_streams
    (stream_from_str,) = GeneratorVideoEquation("0", "1+t").out_streams
    (stream_from_num,) = GeneratorVideoEquation(0, colors[1]).out_streams

    assert stream_from_expr.node.colors == colors
    assert stream_from_str.node.colors == colors
    assert stream_from_num.node.colors == colors


def test_input_vars():
    """Make sure that only the symbols t, i and j are allowed."""
    exprs_ok = ["t+i+j", "exp(1)", "E", "pi", "oo", "nan"]
    exprs_fail = list("abcdefghklmnopqrsuvwxyzABCDFGHKLMPRUVWXYZ")

    for expr in exprs_ok:
        GeneratorVideoEquation(expr).out_streams[0].snapshot(0, (1, 1))
    for expr in exprs_fail:
        with pytest.raises(ValueError):
            GeneratorVideoEquation(expr).out_streams[0].snapshot(0, (1, 1))
