#!/usr/bin/env python3

"""Video editing software."""

from cutcutcodec.core.analysis.video import (get_duration_video, get_nb_frames, get_pix_fmt,
                                             get_rate_video, get_resolution, get_timestamps_video,
                                             compare, lpips, psnr, ssim, uvq, vmaf)
from cutcutcodec.core import classes
from cutcutcodec.core import filter  # pylint: disable=W0622
from cutcutcodec.core import generation
from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.colorspace.func import convert
from cutcutcodec.core.compilation import Lambdify
from cutcutcodec.core.io import read, write


__author__ = "Robin RICHARD (robinechuca)"
__version__ = "1.4.0"  # pep 440
__all__ = [
    "get_duration_video", "get_nb_frames", "get_pix_fmt", "get_rate_video", "get_resolution",
    "get_timestamps_video",
    "compare", "lpips", "psnr", "ssim", "uvq", "vmaf",
    "Colorspace", "convert",
    "Lambdify",
    "read", "write",
    "classes", "filter", "generation",
]
