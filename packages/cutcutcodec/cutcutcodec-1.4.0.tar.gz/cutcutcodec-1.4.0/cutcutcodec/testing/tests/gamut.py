#!/usr/bin/env python3

"""Some tests on primaries gamut function."""

# import colour  # this module change the numpy behavour and break doctests
# import numpy as np

# from cutcutcodec.core.colorspace.cst import PRIMARIES
# from cutcutcodec.core.colorspace.func import rgb2xyz_matrix_from_chroma


# COLOUR_SCIENCE_PRIMARIES = {
#     "bt2020": colour.models.RGB_COLOURSPACE_BT2020,
#     "bt470bg": colour.models.RGB_COLOURSPACE_BT470_625,
#     "bt470m": colour.models.RGB_COLOURSPACE_BT470_525,
#     "bt709": colour.models.RGB_COLOURSPACE_BT709,
#     "film": colour.models.RGB_COLOURSPACE_H273_GENERIC_FILM,
#     "jedec-p22, ebu3213": colour.models.RGB_COLOURSPACE_EBU_3213_E,
#     "smpte170m": colour.models.RGB_COLOURSPACE_SMPTE_240M,
#     # "smpte428, smpte428_1": None,
#     # "smpte431": None,
#     "smpte432": colour.models.RGB_COLOURSPACE_P3_D65,
# }


# def _test_primaries(code: str):
#     """Ensure it matches with colour science."""
#     red, green, blue, white = PRIMARIES[code]
#     red_cs, green_cs, blue_cs = COLOUR_SCIENCE_PRIMARIES[code].primaries
#     white_cs = COLOUR_SCIENCE_PRIMARIES[code].whitepoint
#     np.testing.assert_allclose(
#         np.array([red, green, blue, white]).astype(np.float64),
#         np.array([red_cs, green_cs, blue_cs, white_cs]),
#         atol=1e-3,
#     )
#     matrix_exact = rgb2xyz_matrix_from_chroma(red, green, blue, white)
#     matrix_num = np.array(matrix_exact).astype(np.float64)
#     matrix_cs = COLOUR_SCIENCE_PRIMARIES[code].matrix_RGB_to_XYZ
#     np.testing.assert_allclose(matrix_num, matrix_cs, atol=1e-2)


# def test_primaries_bt2020():
#     """Ensure the transfer function."""
#     _test_primaries("bt2020")


# def test_primaries_bt470bg():
#     """Ensure the transfer function."""
#     _test_primaries("bt470bg")


# def test_primaries_bt470m():
#     """Ensure the transfer function."""
#     _test_primaries("bt470m")


# def test_primaries_bt709():
#     """Ensure the transfer function."""
#     _test_primaries("bt709")


# def test_primaries_film():
#     """Ensure the transfer function."""
#     _test_primaries("film")


# def test_primaries_jedec():
#     """Ensure the transfer function."""
#     _test_primaries("jedec-p22, ebu3213")


# def test_primaries_smpte170m():
#     """Ensure the transfer function."""
#     _test_primaries("smpte170m")


# def test_primaries_smpte432():
#     """Ensure the transfer function."""
#     _test_primaries("smpte432")
