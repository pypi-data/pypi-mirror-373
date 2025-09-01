#!/usr/bin/env python3

"""Mathematical functions to switching from a color space to another."""

import numbers

import networkx
import sympy

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.opti.cache.basic import basic_cache
from .cst import PRIMARIES, SYMBS, TRC, V, L

NBR = numbers.Real | sympy.core.basic.Basic


def _rgb2rpgpbp(componants: sympy.Matrix, transfer_dst: str) -> sympy.Matrix:
    """Convert the colorspace expression from RGB to R'G'B'."""
    trans = TRC[transfer_dst][0]
    componants[0, 0] = trans.xreplace({L: componants[0, 0]})
    componants[1, 0] = trans.xreplace({L: componants[1, 0]})
    componants[2, 0] = trans.xreplace({L: componants[2, 0]})
    return componants


def _rgb2xyz(componants: sympy.Matrix, primaries_src: str) -> sympy.Matrix:
    """Convert the colorspace expression from RGB to XYZ."""
    return rgb2xyz_matrix_from_chroma(*PRIMARIES[primaries_src]) @ componants


def _rpgpbp2rgb(componants: sympy.Matrix, transfer_src: str) -> sympy.Matrix:
    """Convert the colorspace expression from R'G'B' to RGB."""
    trans = TRC[transfer_src][1]
    componants[0, 0] = trans.xreplace({V: componants[0, 0]})
    componants[1, 0] = trans.xreplace({V: componants[1, 0]})
    componants[2, 0] = trans.xreplace({V: componants[2, 0]})
    return componants


def _rpgpbp2yuv(componants: sympy.Matrix, primaries_dst: str) -> sympy.Matrix:
    """Convert the colorspace expression from R'G'B' to Y'PbPr.

    To be consitent with ffmpeg, we should use the constant matrix given by
    Rec. ITU-T T.871 (05/2011).
    It is the same matrix directly in th ffmpeg source code:
    https://github.com/FFmpeg/FFmpeg/blob/master/libswscale/utils.c#L681
    """
    # return sympy.Matrix( # https://fourcc.org/fccyvrgb.php
    #     [[0.299, 0.587, 0.114],
    #      [-0.1687, -0.3313, 0.5],
    #      [0.5, -0.4187, -0.0813]],
    # ) @ componants
    return rgb2yuv_matrix_from_kr_kb(
        *yuv_cst_from_chroma(*PRIMARIES[primaries_dst])  # get kr and kb
    ) @ componants


def _to_sympy(antity: object) -> sympy.Rational:
    """Convert float numbers into rational."""
    match antity:
        case numbers.Real() | str():
            return sympy.Rational(antity)  # sympy.Float(antity, 37)
        case tuple():
            return tuple(_to_sympy(item) for item in antity)
        case list():
            return [_to_sympy(item) for item in antity]
        case _:
            return sympy.sympify(antity)


def _xyz2rgb(componants: sympy.Matrix, primaries_dst: str) -> sympy.Matrix:
    """Convert the colorspace expression from XYZ to RGB."""
    return rgb2xyz_matrix_from_chroma(*PRIMARIES[primaries_dst])**-1 @ componants


def _yuv2rpgpbp(componants: sympy.Matrix, primaries_src: str) -> sympy.Matrix:
    """Convert the colorspace expression from Y'PbPr to R'G'B'.

    See ``_rpgpbp2yuv`` for the ffmpeg consistency.
    """
    # return sympy.Matrix(
    #     [[1.0, 0.0, 1.402],
    #      [1.0, -0.3441, -0.7141],
    #      [1.0, 1.772, 0.0]],
    # )  @ componants
    return rgb2yuv_matrix_from_kr_kb(
        *yuv_cst_from_chroma(*PRIMARIES[primaries_src])  # get kr and kb
    )**-1 @ componants


@basic_cache
def convert(
    src: Colorspace | str, dst: Colorspace | str
) -> tuple[sympy.core.basic.Basic, sympy.core.basic.Basic, sympy.core.basic.Basic]:
    r"""Return the symbolic expression to convert colorspace.

    Parameters
    ----------
    src, dst : Colorspace or str
        The source and destination colorspace.

    Returns
    -------
    componants : tuple[sympy.core.basic.Basic, sympy.core.basic.Basic, sympy.core.basic.Basic]
        The 3 sympy equations that link the input color space components,
        to each of the output components.

    Examples
    --------
    >>> import sympy, torch
    >>> from cutcutcodec.core.colorspace.func import convert
    >>> from cutcutcodec.core.colorspace.cst import SYMBS
    >>> from cutcutcodec.core.compilation.sympy_to_torch.lambdify import Lambdify
    >>> convert("y'pbpr_bt709", "r'g'b'_bt709")[0]
    12901312*p_r/8192847 + y'
    >>> trans_symb = convert("y'pbpr_bt709", "y'pbpr_bt2020")
    >>> trans_symb = trans_symb.subs(zip(SYMBS["y'pbpr"], sympy.symbols("y u v", real=True)))
    >>> trans_func = Lambdify(trans_symb)
    >>> yuv_709 = torch.rand(1_000_000), torch.rand(1_000_000)-0.5, torch.rand(1_000_000)-0.5
    >>> yuv_2020 = trans_func(y=yuv_709[0], u=yuv_709[1], v=yuv_709[2])
    >>>
    """
    src, dst = Colorspace(src), Colorspace(dst)
    colors = {
        "primaries_dst": dst.primaries,
        "primaries_src": src.primaries,
        "transfer_dst": dst.transfer,
        "transfer_src": src.transfer,
    }

    # find transformation chain
    nodes = [
        ("y'pbpr", src.primaries, src.transfer),
        ("r'g'b", src.primaries, src.transfer),
        ("rgb", src.primaries),
        ("xyz",),
        ("rgb", dst.primaries),
        ("r'g'b", dst.primaries, dst.transfer),
        ("y'pbpr", dst.primaries, dst.transfer),
    ]
    chain = networkx.DiGraph()
    chain.add_edges_from([
        (nodes[0], nodes[1], {"conv": _yuv2rpgpbp, "color": "primaries_src"}),  # Y'PbPr -> R'G'B'
        (nodes[1], nodes[2], {"conv": _rpgpbp2rgb, "color": "transfer_src"}),  # R'G'B' -> RGB
        (nodes[2], nodes[3], {"conv": _rgb2xyz, "color": "primaries_src"}),  # RGB -> XYZ
        (nodes[3], nodes[4], {"conv": _xyz2rgb, "color": "primaries_dst"}),  # XYZ -> RGB
        (nodes[4], nodes[5], {"conv": _rgb2rpgpbp, "color": "transfer_dst"}),  # RGB -> R'G'B'
        (nodes[5], nodes[6], {"conv": _rpgpbp2yuv, "color": "primaries_dst"}),  # R'G'B' -> Y'PbPr
    ])
    path = networkx.algorithms.shortest_path(  # simplification
        chain,
        dict(zip(["y'pbpr", "r'g'b'", "rgb", "xyz"], nodes[:4]))[src.space],
        dict(zip(["xyz", "rgb", "r'g'b'", "y'pbpr"], nodes[3:]))[dst.space],
    )

    # compute the full expression
    componants = sympy.Matrix(SYMBS[src.space])  # column vector
    for nodes in zip(path[:-1], path[1:]):
        edge = chain[nodes[0]][nodes[1]]
        assert colors[edge["color"]] is not None, f"the {edge['color']} is missing"
        componants = edge["conv"](componants, colors[edge["color"]])
    return sympy.Tuple(componants[0, 0], componants[1, 0], componants[2, 0])


def rgb2xyz_matrix_from_chroma(
    xy_r: tuple[NBR, NBR], xy_g: tuple[NBR, NBR], xy_b: tuple[NBR, NBR], xy_w: tuple[NBR, NBR]
) -> sympy.Matrix:
    r"""Compute the RGB to XYZ matrix from chromaticity coordinates and white point.

    Relationship between tristimulus values in CIE XYZ 1936 colour space and in RGB signal space.

    It is an implementation of the International Telecomunication Union Report ITU-R BT.2380-2.

    Returns the :math:`\mathbf{M}` matrix with :math:`(r, g, b) \in [0, 1]^3` such as:

    .. math::
        :label: rgb2xyz

        \begin{pmatrix} x \\ y \\ z \\ \end{pmatrix}
        = \mathbf{M} \begin{pmatrix} r \\ g \\ b \\ \end{pmatrix}

    Where

    .. math::

        \begin{cases}
            (x'_r, y'_r, z'_r) = \left(\frac{x_r}{y_r}, 1, \frac{1-x_r-y_r}{y_r}\right) \\
            (x'_g, y'_g, z'_g) = \left(\frac{x_g}{y_g}, 1, \frac{1-x_g-y_g}{y_g}\right) \\
            (x'_r, y'_r, z'_r) = \left(\frac{x_r}{y_r}, 1, \frac{1-x_r-y_r}{y_r}\right) \\
            (x'_w, y'_w, z'_w) = \left(\frac{x_w}{y_w}, 1, \frac{1-x_w-y_w}{y_w}\right) \\
            \begin{pmatrix}  s_r \\ s_g \\ s_b \end{pmatrix} = \begin{pmatrix}
                x'_r & x'_g & x'_b \\
                y'_r & y'_g & y'_b \\
                z'_r & z'_g & z'_b \\
            \end{pmatrix}^{-1} \begin{pmatrix} x'_w \\ y'_w \\ z'_w \end{pmatrix} \\
            \mathbf{M} = \begin{pmatrix}
                s_r x'_r & s_g x'_g & s_b x'_b \\
                s_r y'_r & s_g y'_g & s_b y'_b \\
                s_r z'_r & s_g z'_g & s_b z'_b \\
            \end{pmatrix} \\
        \end{cases}

    Parameters
    ----------
    xy_r : tuple
        The red point :math:`(x_r, y_r)` in the xyz space.
    xy_g : tuple
        The green point :math:`(x_g, y_g)` in the xyz space.
    xy_b : tuple
        The blue point :math:`(x_b, y_b)` in the xyz space.
    xy_w : tuple
        The white point :math:`(x_w, y_w)` in the xyz space.

    Returns
    -------
    rgb2xyz : sympy.Matrix
        The 3x3 :math:`\mathbf{M}` matrix, sometimes called ``primaries``,
        which converts points from RGB space to XYZ space :eq:`rgb2xyz`.

    Examples
    --------
    >>> import sympy
    >>> from cutcutcodec.core.colorspace.func import rgb2xyz_matrix_from_chroma
    >>> wrgb = sympy.Matrix([[1, 1, 0, 0],  # red
    ...                      [1, 0, 1, 0],  # green
    ...                      [1, 0, 0, 1]]) # blue
    ...
    >>> # rec.709
    >>> xy_r, xy_g, xy_b, white = (0.640, 0.330), (0.300, 0.600), (0.150, 0.060), (0.3127, 0.3290)
    >>> m_709 = rgb2xyz_matrix_from_chroma(xy_r, xy_g, xy_b, white)
    >>> # rec.2020
    >>> xy_r, xy_g, xy_b, white = (0.708, 0.292), (0.170, 0.797), (0.131, 0.046), (0.3127, 0.3290)
    >>> m_2020 = rgb2xyz_matrix_from_chroma(xy_r, xy_g, xy_b, white)
    >>>
    >>> # convert from rec.709 to rec.2020
    >>> (m_2020**-1 @ m_709 @ wrgb).evalf(n=5)
    Matrix([
    [1.0,   0.6274,  0.32928, 0.043313],
    [1.0, 0.069097,  0.91954, 0.011362],
    [1.0, 0.016391, 0.088013,   0.8956]])
    >>>
    """
    assert isinstance(xy_r, tuple), xy_r.__class__.__name__
    assert isinstance(xy_g, tuple), xy_g.__class__.__name__
    assert isinstance(xy_b, tuple), xy_b.__class__.__name__
    assert isinstance(xy_w, tuple), xy_w.__class__.__name__
    assert len(xy_r) == 2, xy_r
    assert len(xy_g) == 2, xy_g
    assert len(xy_b) == 2, xy_b
    assert len(xy_w) == 2, xy_w
    xy_r, xy_g, xy_b, xy_w = _to_sympy(xy_r), _to_sympy(xy_g), _to_sympy(xy_b), _to_sympy(xy_w)

    def xy_to_xyz(x, y):
        return [x / y, 1, (1 - x - y) / y]

    # columns rbg, rows xyz
    rgb2xyz = sympy.Matrix([xy_to_xyz(*xy_r), xy_to_xyz(*xy_g), xy_to_xyz(*xy_b)]).T
    s_rgb = rgb2xyz**-1 @ sympy.Matrix([xy_to_xyz(*xy_w)]).T  # column vectors
    rgb2xyz = rgb2xyz @ sympy.diag(*s_rgb)  # hack for elementwise product

    return rgb2xyz


def rgb2yuv_matrix_from_kr_kb(k_r: NBR, k_b: NBR) -> sympy.Matrix:
    r"""Compute the RGB to YpPbPr matrix from the kr and kb constants.

    Relationship between gamma corrected R'G'B' colour space and Y'PbPr colour space.

    It is an implementation based on wikipedia.

    Returns the :math:`\mathbf{A}` matrix with :math:`(r', g', b') \in [0, 1]^3`
    and :math:`(y', p_b, p_r) \in [0, 1] \times \left[-\frac{1}{2}, \frac{1}{2}\right]^2` such as:

    .. math::
        :label: rgb2yuv

        \begin{pmatrix} y' \\ p_b \\ p_r \\ \end{pmatrix}
        = \mathbf{A} \begin{pmatrix} r' \\ g' \\ b' \\ \end{pmatrix}

    Where

    .. math::

        \begin{cases}
            k_r + k_g + k_b = 1 \\
            \mathbf{A} = \begin{pmatrix}
                k_r & k_g & k_b \\
                -\frac{k_r}{2-2k_b} & -\frac{k_g}{2-2k_b} & \frac{1}{2} \\
                \frac{1}{2} & -\frac{k_g}{2-2k_r} & -\frac{k_b}{2-2k_r} \\
            \end{pmatrix} \\
        \end{cases}

    Parameters
    ----------
    k_r, k_b
        The 2 scalars :math:`k_r` and :math:`k_b` :eq:`krkb`.
        They may come from :py:func:`cutcutcodec.core.colorspace.func.yuv_cst_from_chroma`.

    Returns
    -------
    rgb2yuv : sympy.Matrix
        The 3x3 :math:`\mathbf{A}` color matrix.

    Examples
    --------
    >>> import sympy
    >>> from cutcutcodec.core.colorspace.func import rgb2yuv_matrix_from_kr_kb
    >>> wrgb = sympy.Matrix([[1, 1, 0, 0],  # red
    ...                      [1, 0, 1, 0],  # green
    ...                      [1, 0, 0, 1]]) # blue
    ...
    >>> kr, kb = sympy.Rational(0.2126), sympy.Rational(0.0722)  # rec.709
    >>> a_709 = rgb2yuv_matrix_from_kr_kb(kr, kb)
    >>> (a_709 @ wrgb).evalf(n=5)
    Matrix([
    [1.0,   0.2126,   0.7152,    0.0722],
    [  0, -0.11457, -0.38543,       0.5],
    [  0,      0.5, -0.45415, -0.045847]])
    >>> kr = kb = sympy.sympify("1/3")  # for demo
    >>> rgb2yuv_matrix_from_kr_kb(kr, kb) @ wrgb
    Matrix([
    [1,  1/3,  1/3,  1/3],
    [0, -1/4, -1/4,  1/2],
    [0,  1/2, -1/4, -1/4]])
    >>>
    """
    assert isinstance(k_b, NBR), k_b.__class__.__name__
    assert isinstance(k_r, NBR), k_r.__class__.__name__

    k_g = 1 - k_r - k_b
    uscale = 1 / (2 - 2 * k_b)
    vscale = 1 / (2 - 2 * k_r)
    return sympy.Matrix([[k_r, k_g, k_b],
                         [-k_r * uscale, -k_g * uscale, sympy.core.numbers.Half()],
                         [sympy.core.numbers.Half(), -k_g * vscale, -k_b * vscale]])


def yuv_cst_from_chroma(
    xy_r: tuple[NBR, NBR], xy_g: tuple[NBR, NBR], xy_b: tuple[NBR, NBR], xy_w: tuple[NBR, NBR]
) -> tuple[NBR, NBR]:
    r"""Compute the kr and kb constants from chromaticity coordinates and white point.

    It is an implementation of the
    International Telecomunication Union Recomandation ITU-T H.273 (V4).

    .. math::
        :label: krkb

        k_r = \frac{\det\mathbf{R}}{\det\mathbf{D}} \\
        k_b = \frac{\det\mathbf{B}}{\det\mathbf{D}} \\

    Where

    .. math::

        \begin{cases}
            (x'_r, y'_r, z'_r) = \left(\frac{x_r}{y_r}, 1, \frac{1-x_r-y_r}{y_r}\right) \\
            (x'_g, y'_g, z'_g) = \left(\frac{x_g}{y_g}, 1, \frac{1-x_g-y_g}{y_g}\right) \\
            (x'_r, y'_r, z'_r) = \left(\frac{x_r}{y_r}, 1, \frac{1-x_r-y_r}{y_r}\right) \\
            (x'_w, y'_w, z'_w) = \left(\frac{x_w}{y_w}, 1, \frac{1-x_w-y_w}{y_w}\right) \\
            \mathbf{D} = \begin{pmatrix}
                x'_r & y'_r & z'_r \\
                x'_g & y'_g & z'_g \\
                x'_b & y'_b & z'_b \\
            \end{pmatrix} \\
            \mathbf{R} = \begin{pmatrix}
                x'_w & x'_g & x'_b \\
                y'_w & y'_g & y'_b \\
                z'_w & z'_g & z'_b \\
            \end{pmatrix} \\
            \mathbf{B} = \begin{pmatrix}
                x'_w & x'_r & x'_g \\
                y'_w & y'_r & y'_g \\
                z'_w & z'_r & z'_g \\
            \end{pmatrix} \\
        \end{cases}

    Parameters
    ----------
    xy_r : tuple
        The red point :math:`(x_r, y_r)` in the xyz space.
    xy_g : tuple
        The green point :math:`(x_g, y_g)` in the xyz space.
    xy_b : tuple
        The blue point :math:`(x_b, y_b)` in the xyz space.
    xy_w : tuple
        The white point :math:`(x_w, y_w)` in the xyz space.

    Returns
    -------
    k_r, k_b
        The 2 scalars :math:`k_r` and :math:`k_b` :eq:`krkb` used in rgb to yuv conversion.

    Examples
    --------
    >>> from cutcutcodec.core.colorspace.func import yuv_cst_from_chroma
    >>> # rec.709
    >>> xy_r, xy_g, xy_b, white = (0.640, 0.330), (0.300, 0.600), (0.150, 0.060), (0.3127, 0.3290)
    >>> kr, kb = yuv_cst_from_chroma(xy_r, xy_g, xy_b, white)
    >>> round(kr, 5), round(kb, 5)
    (0.21264, 0.07219)
    >>> # rec.2020
    >>> xy_r, xy_g, xy_b, white = (0.708, 0.292), (0.170, 0.797), (0.131, 0.046), (0.3127, 0.3290)
    >>> kr, kb = yuv_cst_from_chroma(xy_r, xy_g, xy_b, white)
    >>> round(kr, 5), round(kb, 5)
    (0.26270, 0.05930)
    >>>
    """
    assert isinstance(xy_r, tuple), xy_r.__class__.__name__
    assert isinstance(xy_g, tuple), xy_g.__class__.__name__
    assert isinstance(xy_b, tuple), xy_b.__class__.__name__
    assert isinstance(xy_w, tuple), xy_w.__class__.__name__
    assert len(xy_r) == 2, xy_r
    assert len(xy_g) == 2, xy_g
    assert len(xy_b) == 2, xy_b
    assert len(xy_w) == 2, xy_w
    xy_r, xy_g, xy_b, xy_w = _to_sympy(xy_r), _to_sympy(xy_g), _to_sympy(xy_b), _to_sympy(xy_w)

    def xy_to_xyz(x, y):
        return [x / y, 1, (1 - x - y) / y]

    # version zscale
    xyz_r = xy_to_xyz(*xy_r)
    xyz_g = xy_to_xyz(*xy_g)
    xyz_b = xy_to_xyz(*xy_b)
    xyz_w = xy_to_xyz(*xy_w)
    denom = sympy.det(sympy.Matrix([xyz_r, xyz_g, xyz_b]))
    k_r = sympy.det(sympy.Matrix([xyz_w, xyz_g, xyz_b])) / denom  # det(A) = det(At)
    k_b = sympy.det(sympy.Matrix([xyz_w, xyz_r, xyz_g])) / denom

    # # version ITU
    # # this version is mathematically equivalent to the formula above
    # xyz_r = [*xy_r, 1 - (xy_r[0] + xy_r[1])]
    # xyz_g = [*xy_g, 1 - (xy_g[0] + xy_g[1])]
    # xyz_b = [*xy_b, 1 - (xy_b[0] + xy_b[1])]
    # xyz_w = [*xy_w, 1 - (xy_w[0] + xy_w[1])]
    # denom = xyz_w[1] * (
    #     xyz_r[0] * (xyz_g[1] * xyz_b[2] - xyz_b[1] * xyz_g[2])
    #     + xyz_g[0] * (xyz_b[1] * xyz_r[2] - xyz_r[1] * xyz_b[2])
    #     + xyz_b[0] * (xyz_r[1] * xyz_g[2] - xyz_g[1] * xyz_r[2])
    # )
    # k_r = xyz_r[1] * (
    #     xyz_w[0] * (xyz_g[1] * xyz_b[2] - xyz_b[1] * xyz_g[2])
    #     + xyz_w[1] * (xyz_b[0] * xyz_g[2] - xyz_g[0] * xyz_b[2])
    #     + xyz_w[2] * (xyz_g[0] * xyz_b[1] - xyz_b[0] * xyz_g[1])
    # ) / denom
    # k_b = xyz_b[1] * (
    #     xyz_w[0] * (xyz_r[1] * xyz_g[2] - xyz_g[1] * xyz_r[2])
    #     + xyz_w[1] * (xyz_g[0] * xyz_r[2] - xyz_r[0] * xyz_g[2])
    #     + xyz_w[2] * (xyz_r[0] * xyz_g[1] - xyz_g[0] * xyz_r[1])
    # ) / denom

    return k_r, k_b
