#!/usr/bin/env python3

"""Perform tests on the ``cutcutcodec.core.generation.audio.equation.GeneratorAudioEquation``."""

import math

import pytest
import sympy

from cutcutcodec.core.generation.audio.equation import GeneratorAudioEquation


def test_clip_nan():
    """Ensures that the values remain in the correct range."""
    for stream, val in (
        (GeneratorAudioEquation(-2).out_streams[0], -1),
        (GeneratorAudioEquation(2).out_streams[0], 1),
        (GeneratorAudioEquation("-2").out_streams[0], -1),
        (GeneratorAudioEquation("2").out_streams[0], 1),
        (GeneratorAudioEquation(math.inf).out_streams[0], 1),
        (GeneratorAudioEquation(-math.inf).out_streams[0], -1),
        (GeneratorAudioEquation(math.nan).out_streams[0], 0),
        (GeneratorAudioEquation("oo").out_streams[0], 1),
        (GeneratorAudioEquation("-oo").out_streams[0], -1),
        (GeneratorAudioEquation("nan").out_streams[0], 0),
    ):
        assert stream.snapshot(0, 1, 1).item() == val


def test_complex_real_part():
    """Check that the Euclidean norm is used for a complex expression."""
    (stream,) = GeneratorAudioEquation("(3/8+4/8*I)").out_streams
    assert stream.snapshot(0, 1, 1).item() == 0.375  # /8 for double base 2


def test_contant():
    """Make sure the numbers are cast in array."""
    (stream,) = GeneratorAudioEquation(0).out_streams
    assert stream.snapshot(0, 1, 2).shape == (1, 2)
    (stream,) = GeneratorAudioEquation(0, "t").out_streams  # mix cst and array
    assert stream.snapshot(0, 1, 3).shape == (2, 3)


def test_divide_by_zero():
    """Make sure not failed when divide by 0."""
    (stream,) = GeneratorAudioEquation("1/t").out_streams
    stream.snapshot(0, 1, 1)


def test_input_type():
    """Check that the entries can be of sympy, str and number type."""
    signals = [sympy.sympify("0"), 1 + sympy.Symbol("t", real=True, positive=True)]
    (stream_from_expr,) = GeneratorAudioEquation(*signals).out_streams
    (stream_from_str,) = GeneratorAudioEquation("0", "1+t").out_streams
    (stream_from_num,) = GeneratorAudioEquation(0, signals[1]).out_streams

    assert stream_from_expr.node.signals == signals
    assert stream_from_str.node.signals == signals
    assert stream_from_num.node.signals == signals


def test_input_vars():
    """Make sure that only the symbol t is allowed."""
    exprs_ok = ["t", "E", "pi", "oo", "nan"]
    exprs_fail = list("abcdefghijklmnopqrsuvwxyzABCDFGHKLMPRUVWXYZ")

    for expr in exprs_ok:
        GeneratorAudioEquation(expr).out_streams[0].snapshot(0, 1, 1)
    for expr in exprs_fail:
        with pytest.raises(AssertionError):
            GeneratorAudioEquation(expr).out_streams[0].snapshot(0, 1, 1)
