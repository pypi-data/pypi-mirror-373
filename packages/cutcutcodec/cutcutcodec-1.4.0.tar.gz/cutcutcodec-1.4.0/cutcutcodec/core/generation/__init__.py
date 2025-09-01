#!/usr/bin/env python3

"""Create streams."""

from .audio import GeneratorAudioEquation, GeneratorAudioNoise
from .video import GeneratorVideoMandelbrot, GeneratorVideoEquation, GeneratorVideoNoise


__all__ = [
    "GeneratorAudioEquation", "GeneratorAudioNoise",
    "GeneratorVideoEquation", "GeneratorVideoMandelbrot", "GeneratorVideoNoise",
]
