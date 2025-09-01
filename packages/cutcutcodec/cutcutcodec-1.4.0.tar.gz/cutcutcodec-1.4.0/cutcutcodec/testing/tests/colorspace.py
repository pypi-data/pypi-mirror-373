#!/usr/bin/env python3

"""Compare Colour-Science and cutcutcodec color chain."""

# import colour  # this module change the numpy behavour and break doctests
# import torch

# from cutcutcodec.core.classes.colorspace import Colorspace


# def test_yuv_to_rgb():
#     """Compare the conversion from y'pbpr to r'g'b'."""
#     # create a fake y'pbpr
#     src_yuv = torch.rand(1080, 1920, 3, dtype=torch.float64)
#     src_yuv[:, :, 0] -= 0.5

#     # conversion with cutcutcodec
#     dst_y, dst_u, dst_v = Colorspace(
#         "y'pbpr", "smpte240m", "smpte240m"
#     ).to_function(Colorspace(
#         "r'g'b'", "smpte240m", "smpte240m"
#     ))(
#         y=src_yuv[..., 0], u=src_yuv[..., 1], v=src_yuv[..., 2]
#     )
#     dst_yuv = torch.cat([dst_y[:, :, None], dst_u[:, :, None], dst_v[:, :, None]], dim=2)

#     # conversion with colour-science
#     dst_yuv_cs = torch.from_numpy(
#         colour.YCbCr_to_RGB(
#             src_yuv.numpy(force=True),
#             colour.WEIGHTS_YCBCR["SMPTE-240M"],
#             in_range=(0.0, 1.0, -0.5, 0.5),
#             out_range=(0.0, 1.0),
#         )
#     )

#     # verification it matches
#     assert torch.allclose(dst_yuv, dst_yuv_cs, rtol=1e-3, atol=1e-3)


# def test_rgb_to_xyz():
#     """Compare the conversion between r'g'b' to xyz."""
#     # create a fake rgb
#     src_rgb = torch.rand(1080, 1920, 3, dtype=torch.float64)

#     # conversion with cutcutcodec
#     dst_r, dst_g, dst_b = Colorspace(
#         "r'g'b'", "smpte240m", "smpte240m"
#     ).to_function("xyz")(
#         r=src_rgb[..., 0], g=src_rgb[..., 1], b=src_rgb[..., 2]
#     )
#     dst_rgb = torch.cat([dst_r[:, :, None], dst_g[:, :, None], dst_b[:, :, None]], dim=2)

#     # conversion with colour-science
#     dst_rgb_cs = torch.from_numpy(
#         colour.RGB_to_XYZ(
#             src_rgb.numpy(force=True),
#             colour.models.RGB_COLOURSPACE_SMPTE_240M,
#             apply_cctf_decoding=True,
#         )
#     )

#     # verification it matches
#     assert torch.allclose(dst_rgb, dst_rgb_cs, rtol=1e-3, atol=1e-3)
