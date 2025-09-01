#!/usr/bin/env python3

"""Check that the arrays comming from C are well referenced."""

import gc
import tracemalloc

from sympy.abc import x
from sympy.core.containers import Tuple
import numpy as np
import pytest

from cutcutcodec.core.compilation.sympy_to_torch.lambdify import _lambdify_c
from cutcutcodec.core.compilation.sympy_to_torch.preprocess import preprocess
from cutcutcodec.core.compilation.sympy_to_torch.printer import _printer
from cutcutcodec.core.generation.video.fractal.fractal import mandelbrot


@pytest.mark.slow
def test_leak_fractal_mandelbrot():
    """Ensure there is not memory leak in mandelbrot generation."""
    imag, real = np.meshgrid(
        np.linspace(-1.12, 1.12, 354, dtype=np.float64),
        np.linspace(-2.0, 0.47, 354, dtype=np.float64),
        indexing="ij",
    )  # 1 Mo for out
    cpx = real + 1j*imag
    tracemalloc.start()
    gc.collect()
    snapshot1 = tracemalloc.take_snapshot()
    for _ in range(1000):  # total leak 1 Go
        mandelbrot(cpx, 64)
    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top_stat = snapshot2.compare_to(snapshot1, "lineno")[0]
    assert top_stat.size_diff < 500_000_000, f"mandelbrot memory leak of {top_stat.size_diff} bytes"


@pytest.mark.slow
def test_leak_fractal_mandelbrot_inplace():
    """Ensure there is not memory leak in mandelbrot generation."""
    imag, real = np.meshgrid(
        np.linspace(-1.12, 1.12, 354, dtype=np.float64),
        np.linspace(-2.0, 0.47, 354, dtype=np.float64),
        indexing="ij",
    )  # 1 Mo for out
    cpx = real + 1j*imag
    tracemalloc.start()
    gc.collect()
    snapshot1 = tracemalloc.take_snapshot()
    for _ in range(1000):  # total leak 1 Go
        mandelbrot(cpx, 64, out=np.zeros(cpx.shape, dtype=np.float32))  # set 0 to allocate
    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top_stat = snapshot2.compare_to(snapshot1, "lineno")[0]
    assert top_stat.size_diff < 500_000_000, f"mandelbrot memory leak of {top_stat.size_diff} bytes"


def test_leak_inplace_array_printer():
    """Ensure there is not memory leak when the returned array is an input array."""
    tree = preprocess(x + 1, set(), set(), set())
    func = _lambdify_c(_printer(tree["dyn_tree"], tree["dyn_alloc"], {x}))
    tracemalloc.start()
    gc.collect()
    snapshot1 = tracemalloc.take_snapshot()
    for _ in range(1000):  # total leak 1 Go
        func(np.zeros(250_000, dtype=np.float32))  # 1 Mo
    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top_stat = snapshot2.compare_to(snapshot1, "lineno")[0]
    assert top_stat.size_diff < 500_000_000, \
        f"c printer inplace memory leak of {top_stat.size_diff} bytes"


def test_leak_new_array_printer():
    """Ensure there is not memory leak when the returned array is allocated inside the C func."""
    tree = preprocess(x*(x + 1), set(), set(), set())
    func = _lambdify_c(_printer(tree["dyn_tree"], tree["dyn_alloc"], {x}))
    tracemalloc.start()
    gc.collect()
    snapshot1 = tracemalloc.take_snapshot()
    for _ in range(1000):  # total leak 1 Go
        func(np.zeros(250_000, dtype=np.float32))  # 1 Mo
    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top_stat = snapshot2.compare_to(snapshot1, "lineno")[0]
    assert top_stat.size_diff < 500_000_000, \
        f"c printer new memory leak of {top_stat.size_diff} bytes"


def test_leak_tuple_pack_printer():
    """Ensure there is not memory leak when the returned arrays are packed in a tuple."""
    tree = preprocess(Tuple(x, x + 1), set(), set(), set())
    func = _lambdify_c(_printer(tree["dyn_tree"], tree["dyn_alloc"], {x}))
    tracemalloc.start()
    gc.collect()
    snapshot1 = tracemalloc.take_snapshot()
    for _ in range(1000):  # total leak 1 or 2 Go
        func(np.zeros(250_000, dtype=np.float32))  # 1 Mo
    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top_stat = snapshot2.compare_to(snapshot1, "lineno")[0]
    assert top_stat.size_diff < 500_000_000, \
        f"c printer inplace memory leak of {top_stat.size_diff} bytes"


def test_segfault_fractal_mandelbrot():
    """Ensure the result of mandelbrot is not dereferenced."""
    imag, real = np.meshgrid(
        np.linspace(-1.12, 1.12, 3540, dtype=np.float64),
        np.linspace(-2.0, 0.47, 3540, dtype=np.float64),
        indexing="ij",
    )  # 100 Mo for out
    cpx = real + 1j*imag
    iterations = mandelbrot(cpx, 64)
    gc.collect()
    iterations.copy()  # acces underground data
    iterations = mandelbrot(cpx, 64, out=np.empty(cpx.shape, dtype=np.float32))
    gc.collect()
    iterations.copy()  # acces underground data


def test_segfault_inplace_array_printer():
    """Ensure the result of c printer inplace array is not dereferenced."""
    tree = preprocess(x + 1, set(), set(), set())
    func = _lambdify_c(_printer(tree["dyn_tree"], tree["dyn_alloc"], {x}))
    out = func(np.zeros(25_000_000, dtype=np.float32))  # 100 Mo
    gc.collect()
    out.copy()  # acces underground data


def test_segfault_new_array_printer():
    """Ensure the result of c printer new array is not dereferenced."""
    tree = preprocess(x * (x+1), set(), set(), set())
    func = _lambdify_c(_printer(tree["dyn_tree"], tree["dyn_alloc"], {x}))
    out = func(np.zeros(25_000_000, dtype=np.float32))  # 100 Mo
    gc.collect()
    out.copy()  # acces underground data


def test_segfault_tuple_pack_printer():
    """Ensure the result of c printer packed tuple is not dereferenced."""
    tree = preprocess(Tuple(x, x + 1), set(), set(), set())
    func = _lambdify_c(_printer(tree["dyn_tree"], tree["dyn_alloc"], {x}))
    out = func(np.zeros(250_000, dtype=np.float32))  # 2 Mo
    gc.collect()
    arr1, arr2 = out
    del out
    gc.collect()
    arr1.copy()
    arr2.copy()
