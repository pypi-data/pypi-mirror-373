#!/usr/bin/env python3

"""Estimate missing information."""

import numbers

from cutcutcodec.core.io.cst import IMAGE_SUFFIXES


def guess_space(
    height: numbers.Integral, width: numbers.Integral, suffix: str = ""
) -> tuple[str, str]:
    """Guess a gamut and gamma based on the image shape.

    It comes from https://wiki.x266.mov/docs/colorimetry/primaries#2-unspecified.

    Parameters
    ----------
    height, width : int
        The image shape
    suffix : str
        The extension name of the file, ex ".mp4".

    Returns
    -------
    primaries : str
        A guessed primary color space gamut.
    transfer : str
        A guessed primary transfer function gamma.
    """
    assert isinstance(height, numbers.Integral), height.__class__.__name__
    assert isinstance(width, numbers.Integral), width.__class__.__name__
    assert isinstance(suffix, str), suffix.__class__.__name__

    if suffix.lower() in IMAGE_SUFFIXES:
        return "srgb", "srgb"
    if width >= 1280 or height > 576:
        return "bt709", "bt709"
    if height == 576:
        # from ITU-T H.273 (V4), gamma 2.8 is for Rec. ITU-R BT.470-6 System B, G
        return "bt470bg", "gamma28"
    if height in {480, 488}:
        return "smpte170m", "smpte170m"
    return "bt709", "bt709"
