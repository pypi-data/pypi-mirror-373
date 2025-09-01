#!/usr/bin/env python3

"""Pythonic tools."""

import os
import pathlib

import numpy as np


class MetaSingleton(type):
    """For share memory inside the current session.

    Notes
    -----
    The arguments needs to be hashable.

    Examples
    --------
    >>> from cutcutcodec.utils import MetaSingleton
    >>> class A:
    ...     pass
    ...
    >>> class B(metaclass=MetaSingleton):
    ...     pass
    ...
    >>> class C(metaclass=MetaSingleton):
    ...     def __init__(self, *args, **kwargs):
    ...         self.args = args
    ...         self.kwargs = kwargs
    ...
    >>> A() is A()
    False
    >>> B() is B()
    True
    >>> C(0) is C(0)
    True
    >>> C(0) is C(1)
    False
    >>>
    """

    instances: dict = {}

    def __call__(cls, *args, **kwargs):
        """Create a new class only if it is not already instanciated."""
        signature = (cls, args, tuple((k, kwargs[k]) for k in sorted(kwargs)))
        if signature not in MetaSingleton.instances:
            instance = cls.__new__(cls)
            instance.__init__(*args, **kwargs)
            MetaSingleton.instances[signature] = instance
        return MetaSingleton.instances[signature]


def get_compilation_rules() -> dict:
    """Return the extra compilation rules."""
    if os.environ.get("READTHEDOCS") == "True":  # if we are on readthedoc server
        extra_compile_args = [
            "-fopenmp",  # for threads
            "-fopenmp-simd",  # for single instruction multiple data
            "-lc",  # include standard c library
            "-lm",  # for math functions
            "-march=x86-64",  # uses local processor instructions for optimization
            "-mtune=generic",  # can be conflictual with march
            "-O1",  # faster to compile
            "-Wall", "-Wextra",  # activate warnings
            "-std=gnu11",  # use iso c norm (gnu23 not yet supported on readthedoc)
            "-pipe",  # use pipline rather than tempory files
        ]
    else:
        extra_compile_args = [
            "-fopenmp",  # for threads
            "-fopenmp-simd",  # for single instruction multiple data
            "-lc",  # include standard c library
            "-lm",  # for math functions
            "-march=native",  # uses local processor instructions for optimization
            "-mtune=native",  # can be conflictual with march
            "-O2",  # hight optimization, -O3 include -ffast-math
            "-ffast-math",  # not activated in -O2
            "-std=gnu18",  # use iso c norm
            "-flto=auto",  # enable link time optimization
            "-pipe",  # use pipline rather than tempory files
        ]
    # setuptools used sysconfig CC and CFLAGS by default,
    # it used environement var if it is defined.
    # to avoid undefined symbol: GOMP_loop_nonmonotonic_dynamic_start,
    # we have to add -fopenmp -fopenmp-simd before "extra_compile_args".
    os.environ["CC"] = "gcc"  # overwite default compiler
    os.environ["CFLAGS"] = " ".join(extra_compile_args)
    return {
        "define_macros": [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],  # for warning
        "extra_compile_args": extra_compile_args,
        # solvable localy with:
        # import ctypes
        # ctypes.CDLL('libgomp.so.1')
        # or in the shell with:
        # export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libgomp.so.1
        "extra_link_args": [
            "-fopenmp", "-shared", "-lmvec",  # avoid ImportError: ... .so undefined symbol: ...
        ],
        "include_dirs": [
            np.get_include(),  # requires for  #include <numpy/arrayobject.h>
            str(get_project_root().parent),  # requires for #include "cutcutcodec/..."
        ],
    }


def get_project_root() -> pathlib.Path:
    """Return the absolute project root folder.

    Examples
    --------
    >>> from cutcutcodec.utils import get_project_root
    >>> root = get_project_root()
    >>> root.is_dir()
    True
    >>> root.name
    'cutcutcodec'
    >>> sorted(p.name for p in root.iterdir())  # doctest: +ELLIPSIS
    ['__init__.py', '__main__.py', ...]
    >>>
    """
    return pathlib.Path(__file__).resolve().parent
