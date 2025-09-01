#!/usr/bin/env python3

"""Test all behavours of the th e c mandelbrot function."""

import numpy as np
import pytest

from cutcutcodec.core.generation.video.fractal.fractal import mandelbrot


def test_cpx_plan_dim():
    """Ensure raise an exception if dim != 2."""
    with pytest.raises(ValueError):
        mandelbrot(np.empty((1,), dtype=np.complex128))
    with pytest.raises(ValueError):
        mandelbrot(np.empty((1, 1, 1), dtype=np.complex128))


def test_cpx_plan_dtype():
    """Tests raise an exception if dtype if wrong."""
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.float32))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.float64))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.float128))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.int8))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.int16))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.int32))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.int64))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.uint8))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.uint16))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.uint32))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.uint64))
    mandelbrot(np.zeros((1, 1), dtype=np.complex128))
    mandelbrot(np.zeros((1, 1), dtype=np.complex256))


def test_iterations_bounds():
    """Ensure iterations values are in write range."""
    with pytest.raises(ValueError):
        mandelbrot(np.empty((1, 1), dtype=np.complex128), iterations=0)
    with pytest.raises(OverflowError):
        mandelbrot(np.empty((1, 1), dtype=np.complex128), iterations=1 << 63)


def test_nan():
    """Ensure it skip the nan values."""
    out = np.full((1, 1), 2.0, dtype=np.float32)
    fractal = mandelbrot(np.full((1, 1), np.nan, dtype=np.complex128), out=out)
    assert fractal[0, 0] == 2.0
    fractal = mandelbrot(np.full((1, 1), np.nan, dtype=np.complex256), out=out)
    assert fractal[0, 0] == 2.0


def test_out_dtype():
    """Test it accepts the output array."""
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.complex128), out=np.empty((1, 1), dtype=np.complex128))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.complex128), out=np.empty((1, 1), dtype=np.uint8))
    with pytest.raises(TypeError):
        mandelbrot(np.empty((1, 1), dtype=np.complex128), out=np.empty((1, 1), dtype=np.float64))
    mandelbrot(np.zeros((1, 1), dtype=np.complex128), out=np.empty((1, 1), dtype=np.float32))


def test_out_ndim():
    """Test it accepts the output array."""
    with pytest.raises(ValueError):
        mandelbrot(np.empty((1, 1), dtype=np.complex128), out=np.empty((1,), dtype=np.float32))
    with pytest.raises(ValueError):
        mandelbrot(np.empty((1, 1), dtype=np.complex128), out=np.empty((1, 1, 1), dtype=np.float32))
    mandelbrot(np.zeros((1, 1), dtype=np.complex128), out=np.empty((1, 1), dtype=np.float32))


def test_out_shape():
    """Test it accepts the output array."""
    with pytest.raises(ValueError):
        mandelbrot(np.empty((1, 2), dtype=np.complex128), out=np.empty((1, 3), dtype=np.float32))
    with pytest.raises(ValueError):
        mandelbrot(np.empty((1, 2), dtype=np.complex128), out=np.empty((2, 2), dtype=np.float32))
    mandelbrot(np.zeros((1, 2), dtype=np.complex128), out=np.empty((1, 2), dtype=np.float32))
