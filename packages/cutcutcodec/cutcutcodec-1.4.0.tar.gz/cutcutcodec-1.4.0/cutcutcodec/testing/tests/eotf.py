#!/usr/bin/env python3

"""Some tests on eotf function."""

# import colour  # this module change the numpy behavour and break doctests
import torch

from cutcutcodec.core.colorspace.cst import TRC
from cutcutcodec.core.compilation.sympy_to_torch.lambdify import Lambdify


# COLOUR_SCIENCE_TRC = {
#     "arib-std-b67": lambda x: colour.models.oetf_ARIBSTDB67(12.0*x),
#     "bt709": colour.models.oetf_BT709,
#     "gamma22": lambda x: colour.gamma_function(x, 1/2.2),
#     "gamma28": lambda x: colour.gamma_function(x, 1/2.8),
#     "iec61966-2-1, iec61966_2_1": colour.models.oetf_H273_IEC61966_2,
#     "linear": colour.linear_function,
#     "log100, log": colour.models.oetf_H273_Log,
#     "log316, log_sqrt": colour.models.oetf_H273_LogSqrt,
#     "smpte2084": lambda x: colour.models.eotf_inverse_ST2084(x, L_p=1.0),
#     "smpte240m": colour.models.oetf_SMPTE240M,
#     "smpte428, smpte428_1": colour.models.eotf_inverse_H273_ST428_1,
# }


def _test_gamma(code: str):
    """Test if the transfer function is bijective and match colour-science."""
    # preparation
    (func_symb, inv_symb) = TRC[code]
    # func_cs = COLOUR_SCIENCE_TRC[code]
    func_comp, inv_comp = Lambdify(func_symb), Lambdify(inv_symb)
    l_num = torch.linspace(-1.0, 2.0, 1_000_000, dtype=torch.float64)

    # compute functions and bijection
    v_num = func_comp(l_num)
    # v_num_cs = torch.from_numpy(func_cs(l_num.numpy(force=True)))
    l_num_bis = inv_comp(v_num)

    # # draw
    # import matplotlib.pyplot as plt
    # plt.xlabel("linear rgb")
    # plt.ylabel("gamma corrected r'g'b'")
    # plt.title(code)
    # plt.plot(l_num, v_num, label="cutcutcodec")
    # # plt.plot(l_num, v_num_cs, label="colour-science")
    # plt.plot(v_num, l_num_bis, label="bijection")
    # plt.legend()
    # plt.show()

    # verifications
    torch.testing.assert_close(l_num, l_num_bis)  # test bijective
    # # pieces are roughly linked in color-science
    # assert torch.allclose(v_num, v_num_cs, atol=1e-3)
    # assert v_num.min() >= -1e-7
    # assert v_num.max() <= 1.0 + 1e-7


def test_trc_arib():
    """Ensure the transfer function."""
    _test_gamma("arib-std-b67")


def test_trc_bt709():
    """Ensure the transfer function."""
    _test_gamma("bt709")


def test_trc_gamma22():
    """Ensure the transfer function."""
    _test_gamma("gamma22")


def test_trc_gamma26():
    """Ensure the transfer function."""
    _test_gamma("gamma26")


def test_trc_gamma28():
    """Ensure the transfer function."""
    _test_gamma("gamma28")


def test_trc_iec61966():
    """Ensure the transfer function."""
    _test_gamma("iec61966-2-1, iec61966_2_1")


def test_trc_ipt():
    """Ensure the transfer function."""
    _test_gamma("ipt")


def test_trc_linear():
    """Ensure the transfer function."""
    _test_gamma("linear")


def test_trc_log100():
    """Ensure the transfer function."""
    _test_gamma("log100, log")


def test_trc_log316():
    """Ensure the transfer function."""
    _test_gamma("log316, log_sqrt")


def test_trc_smpte2084():
    """Ensure the transfer function."""
    _test_gamma("smpte2084")


def test_trc_smpte240m():
    """Ensure the transfer function."""
    _test_gamma("smpte240m")


def test_trc_smpte428():
    """Ensure the transfer function."""
    _test_gamma("smpte428, smpte428_1")
