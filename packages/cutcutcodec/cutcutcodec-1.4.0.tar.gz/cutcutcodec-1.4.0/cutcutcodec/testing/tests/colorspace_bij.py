#!/usr/bin/env python3

"""Test if all colorspace conversion are bijectives."""

import torch

from cutcutcodec.core.classes.colorspace import Colorspace

RGB = torch.meshgrid(
    torch.linspace(0.1, 0.9, 256, dtype=torch.float64),
    torch.linspace(0.1, 0.9, 256, dtype=torch.float64),
    torch.linspace(0.1, 0.9, 256, dtype=torch.float64),
    indexing="ij"
)


def main_test(src: Colorspace, dst: Colorspace):
    """Test if the numerical conversion from src to dst is bijective."""
    assert src.space == "y'pbpr", src
    assert dst.space == "y'pbpr", dst
    y_src, u_src, v_src = (
        Colorspace("r'g'b'", src.primaries, src.transfer)
        .to_function(src)(r=RGB[0], g=RGB[1], b=RGB[2])
    )
    forward = src.to_function(dst)
    backward = dst.to_function(src)
    y_dst, u_dst, v_dst = forward(y=y_src, u=u_src, v=v_src)
    y_src_, u_src_, v_src_ = backward(y=y_dst, u=u_dst, v=v_dst)
    torch.testing.assert_close(y_src, y_src_)
    torch.testing.assert_close(u_src, u_src_)
    torch.testing.assert_close(v_src, v_src_)


def test_rec601_to_srgb():
    """Conversion rec601 to srgb."""
    main_test(Colorspace("y'pbpr", "smpte170m", "gamma22"), Colorspace("y'pbpr", "srgb", "srgb"))


def test_rec601_to_rec709():
    """Conversion rec601 to rec709."""
    main_test(Colorspace("y'pbpr", "smpte170m", "gamma22"), Colorspace("y'pbpr", "bt709", "bt709"))


def test_rec601_to_rec2020():
    """Conversion rec601 to rec2020."""
    main_test(
        Colorspace("y'pbpr", "smpte170m", "gamma22"), Colorspace("y'pbpr", "bt2020", "smpte2084")
    )


def test_srgb_to_rec601():
    """Conversion srgb to rec601."""
    main_test(Colorspace("y'pbpr", "srgb", "srgb"), Colorspace("y'pbpr", "smpte170m", "gamma22"))


def test_srgb_to_rec709():
    """Conversion srgb to rec709."""
    main_test(Colorspace("y'pbpr", "srgb", "srgb"), Colorspace("y'pbpr", "bt709", "bt709"))


def test_srgb_to_rec2020():
    """Conversion srgb to rec2020."""
    main_test(Colorspace("y'pbpr", "srgb", "srgb"), Colorspace("y'pbpr", "bt2020", "smpte2084"))


def test_rec709_to_rec601():
    """Conversion rec709 to rec601."""
    main_test(Colorspace("y'pbpr", "bt709", "bt709"), Colorspace("y'pbpr", "srgb", "srgb"))


def test_rec709_to_srgb():
    """Conversion rec709 to srgb."""
    main_test(Colorspace("y'pbpr", "bt709", "bt709"), Colorspace("y'pbpr", "srgb", "srgb"))


def test_rec709_to_rec2020():
    """Conversion rec709 to rec2020."""
    main_test(Colorspace("y'pbpr", "bt709", "bt709"), Colorspace("y'pbpr", "bt2020", "smpte2084"))


def test_rec2020_to_rec601():
    """Conversion rec2020 to rec601."""
    main_test(Colorspace("y'pbpr", "bt2020", "smpte2084"), Colorspace("y'pbpr", "srgb", "srgb"))


def test_rec2020_to_srgb():
    """Conversion rec2020 to srgb."""
    main_test(Colorspace("y'pbpr", "bt2020", "smpte2084"), Colorspace("y'pbpr", "srgb", "srgb"))


def test_rec2020_to_rec709():
    """Conversion rec2020 to rec709."""
    main_test(Colorspace("y'pbpr", "bt2020", "smpte2084"), Colorspace("y'pbpr", "bt709", "bt709"))
