#!/usr/bin/env python3

"""Create video streams."""

from .equation import GeneratorVideoEquation
from .fractal import GeneratorVideoMandelbrot
from .noise import GeneratorVideoNoise


__all__ = ["GeneratorVideoEquation", "GeneratorVideoMandelbrot", "GeneratorVideoNoise"]
