#!/usr/bin/env python3

"""Regroup all standard color space constants.

The ffmpeg constants are defined on the
`ffmpeg colorspace website <https://trac.ffmpeg.org/wiki/colorspace>`_,
or are described somewhere in ``ffmpeg -h full``.

The tristimulus and transfer functions are taken from the
`International Telecomunication Union Recomandation ITU-T H.273 (V4)`
and the `Commission Internationale de l'Eclairage`.
"""

import sympy

SYMBS = {
    "y'pbpr": sympy.symbols("y' p_b p_r", real=True),
    "r'g'b'": sympy.symbols("r' g' b'", real=True),
    "rgb": sympy.symbols("r g b", real=True),
    "xyz": sympy.symbols("x y z", real=True),
}

FFMPEG_COLORSPACE = {  # define transitions between y'pbpr and r'g'b'
    0: "rgb",
    1: "bt709",
    2: None,  # unknown, unspecified
    4: "fcc",
    5: "bt470bg",
    6: "smpte170m",
    7: "smpte240m",
    8: "ycgco, ycocg",
    9: "bt2020nc, bt2020_ncl",
    10: "bt2020c, bt2020_cl",
    11: "smpte2085",
    12: "chroma-derived-nc",
    13: "chroma-derived-c",
    14: "ictcp",
    15: "ipt-c2",
    16: "ycgco-re",
    17: "ycgco-ro",
}

FFMPEG_PRIMARIES = {
    1: "bt709",
    2: None,  # unknown, unspecified
    4: "bt470m",
    5: "bt470bg",
    6: "smpte170m",
    7: "smpte240m",
    8: "film",
    9: "bt2020",
    10: "smpte428, smpte428_1",
    11: "smpte431",
    12: "smpte432",
    22: "jedec-p22, ebu3213",
}

FFMPEG_PRIMARIES_TO_COLORSPACE = {
    # ffmpeg do the difference even if a mathematical relation link them
    1: 1,  # bt709 -> bt709,
    2: 2,  # unknown -> unknown
    4: 5,  # bt470m -> bt470bg (approx, both tv analog)
    5: 5,  # bt470bg -> bt470bg
    6: 6,  # smpte170m -> smpte170m
    7: 7,  # smpte240m -> smpte240m
    8: 7,  # film -> smpte240m (approx)
    9: 9,  # bt2020 -> bt2020nc (same matrix because same primaries)
    11: 14,  # smpte431 -> ictcp (approx, DCI P3 primaries, often used with ICtCp)
    12: 14,  # smpte432 -> ictcp (modern convention)
    22: 6,  # ebu3213 -> smpte170m (approx, used in sd broadcast)
}

FFMPEG_RANGE = {  # it matches the enum av.video.reformatter.ColorRange
    0: None,  # unknown, unspecified
    1: "tv",  # tv = mpeg = limited
    2: "pc",  # pc = jpeg = full
}

FFMPEG_TRC = {
    1: "bt709",
    2: None,  # unknown, unspecified
    4: "gamma22",
    5: "gamma28",
    6: "smpte170m",
    7: "smpte240m",
    8: "linear",
    9: "log100, log",
    10: "log316, log_sqrt",
    11: "iec61966-2-4, iec61966_2_4",
    12: "bt1361e, bt1361",
    13: "iec61966-2-1, iec61966_2_1",
    14: "bt2020-10, bt2020_10bit",
    15: "bt2020-12, bt2020_12bit",
    16: "smpte2084",
    17: "smpte428, smpte428_1",
    18: "arib-std-b67",
}

# to compute it, based on table
# https://www.cie.co.at/datatable/cie-1964-colour-matching-functions-10-degree-observer
ILLUMINANT_1931 = {  # values of illuminant whitepoint in CIE xy 1931
    "a": ("0.44758", "0.40745"),  # indendence lamp, `CIE 15:2004 T.3`
    "b": ("0.34842",  "0.35161"),  # direct sunlight, <https://fr.wikipedia.org/wiki/Illuminant>
    "c": ("0.31006", "0.31616"),  # Simulated daylight, `CIE 15:2004 T.3`
    "d50": ("0.34567", "0.35851"),  # icc profile, `CIE 15:2004 T.3`
    "d55": ("0.33243", "0.34744"),  # <CIE 15:2004 T.3, https://docs.acescentral.com/tb/white-point>
    "d60": ("0.32169", "0.3378"),  # <https://docs.acescentral.com/tb/white-point>
    "d65": ("0.31272", "0.32903"),  # Daylight on overcast days, `CIE 15:2004 T.3`
    "d75": ("0.29903", "0.31488"),  # `CIE 15:2004 T.3`
    "e": ("1/3", "1/3"),  # by definition
}
ILLUMINANT_1964 = {  # values of illuminant whitepoint in CIE xy 1964
    "a": ("0.45117", "0.50495"),  # indendence lamp, `CIE 15:2004 T.3`
    "d65": ("0.31381", "0.33098"),  # Daylight on overcast days, `CIE 15:2004 T.3`
    "c": ("0.31039", "0.31905"),  # Simulated daylight, `CIE 15:2004 T.3`
    "d50": ("0.34773", "0.35952"),  # icc profile, `CIE 15:2004 T.3`
    "d55": ("0.33412", "0.34877"),  # `CIE 15:2004 T.3`
    "d75": ("0.29968", "0.3174"),  # `CIE 15:2004 T.3`
    "e": ("1/3", "1/3"),  # by definition ("0.33333", "0.33333")
}
ILLUMINANT = {  # values of illuminant whitepoint
    "dci": (
        "0.314", "0.351"  # <https://www.color.org/chardata/rgb/DCIP3.xalter>
    ),  # d-Cinema, `SMPTE RP 431-2:2011 Table C.2`
    "aces": ("0.32168", "0.33767"),  # <https://j.mp/TB-2018-001>
    **ILLUMINANT_1931,
}

PRIMARIES = {  # red, green, blue, white primaries in CIE XY 1931
    # <https://en.wikipedia.org/wiki/Adobe_RGB_color_space>
    # and <https://www.benq.com/en-us/knowledge-center/knowledge/color-gamut-monitor.html>
    "aces_ap0": (  # <https://en.wikipedia.org/wiki/Academy_Color_Encoding_System>
        ("0.7347", "0.2653"), ("0.0", "1.0"), ("0.0001", "-0.0770"), ILLUMINANT["aces"]
    ),
    "aces_ap1": (  # `https://en.wikipedia.org/wiki/Academy_Color_Encoding_System`
        ("0.713", "0.293"), ("0.165", "0.83"), ("0.128", "0.044"), ILLUMINANT["aces"]
    ),
    "adobe": (  # CIE 1931
        ("0.64", "0.33"), ("0.21", "0.71"), ("0.15", "0.06"), ILLUMINANT["d65"]
    ),
    "bt2020": (
        ("0.708", "0.292"), ("0.170", "0.797"), ("0.131", "0.046"), ILLUMINANT["d65"]
    ),
    "bt470bg": (
        ("0.64", "0.33"), ("0.29", "0.6"), ("0.15", "0.06"), ILLUMINANT["d65"]
    ),  # bt601-625
    "bt470m": (
        ("0.67", "0.33"), ("0.21", "0.71"), ("0.14", "0.08"), ILLUMINANT["c"]
    ),
    "bt709": (  # ITU-R BT.709-6 (06/2015) <https://www.itu.int/rec/R-REC-BT.709>
        ("0.64", "0.33"), ("0.3", "0.6"), ("0.15", "0.06"), ILLUMINANT["d65"]
    ),
    "film": (
        ("0.681", "0.319"), ("0.243", "0.692"), ("0.145", "0.049"), ILLUMINANT["c"]
    ),
    "jedec-p22, ebu3213": (
        # ("0.630", "0.340"), ("0.295", "0.605"), ("0.155", "0.077"), ILLUMINANT["d65"]  # in ITU-22
        ("0.64", "0.33"), ("0.29", "0.6"), ("0.15", "0.06"), ILLUMINANT["d65"]  # in colour-science
    ),
    "smpte170m": (
        ("0.63", "0.34"), ("0.31", "0.595"), ("0.155", "0.07"), ILLUMINANT["d65"]
    ),  # bt601-525 and smpte rp145 `https://www.color.org/specification/ICC.1-2022-05.pdf`
    "smpte428, smpte428_1": (
        ("1", "0"), ("0", "1"), ("0", "0"), ILLUMINANT["e"]
    ),
    "smpte431": (
        ("0.68", "0.32"), ("0.265", "0.69"), ("0.15", "0.06"), ILLUMINANT["dci"]
    ),
    "smpte432": (
        ("0.68", "0.32"), ("0.265", "0.69"), ("0.15", "0.06"), ILLUMINANT["d65"]
    ),
}
PRIMARIES |= {
    "bt601": PRIMARIES["bt470bg"],  # UIT-R BT.601-7 (03/2011) https://www.itu.int/rec/R-REC-BT.601
    "dcip3": PRIMARIES["smpte431"],  # SMPTE-EG-0432-1:2010, Color Processing for D-Cinema
    "displayp3": PRIMARIES["smpte432"],
    "ntsc": PRIMARIES["smpte170m"],
    "pal": PRIMARIES["bt470bg"],
    "smpte240m": PRIMARIES["smpte170m"],
    "srgb": PRIMARIES["bt709"],  # alias given by ITU
}

V, L = sympy.symbols("V L", real=True)

# Values comes from International Telecomunication Union Recomandation ITU-T H.273 (V4).
# When it is noc clear in the report, values comes from:
# https://github.com/sekrit-twc/zimg/blob/master/src/zimg/colorspace/gamma.cpp
# The alpha and beta constants of the power loop are determined so as to have a c1 class function:
# V1 = alpha * L ** p - (alpha - 1) if L >= beta, V2 = q * L overwise
# V1(beta) = V2(beta) and V1'(beta) = V2(beta)
# <=> alpha = beta * (q/p - q) + 1 and (beta * q * (1-p) + p) * beta**(p-1) - q = 0
# Resolusion:
# beta, p, q = sympy.Symbol("beta"), sympy.Float("0.45", 37), sympy.Float("4.5", 37)
# f = (beta * q * (1-p) + p) * beta**(p-1) - q
# beta = sympy.nsolve(f, (1e-6, 0.5), solver='bisect', prec=37)
# alpha = beta * (q/p - q) + 1
ALPHA_REC709 = sympy.Float("1.099296826809442940347282759215782542", 37)
BETA_REC709 = sympy.Float("0.01805396851080780733586959258468773494", 37)
ALPHA_SMPTE240M = sympy.Float("1.111572195921731219670994036609727092", 37)
BETA_SMPTE240M = sympy.Float("0.02282158552944502220543059839744417796", 37)
ALPHA_IEC61966 = sympy.Float("1.055010718947586597210097331142909940", 37)
BETA_IEC61966 = sympy.Float("0.003041282560127520854162833433376268246", 37)
A_ARIB = sympy.Float("0.1788327726569497656275213115686889965", 37)  # 1-b=4*a
B_ARIB = sympy.Float("0.2846689093722009374899147537252440140", 37)  # a*ln(1-b)+c=1/2
C_ARIB = sympy.Float("0.5599107277627164298015656640000824769", 37)  # a*ln(12-b)+c=1

# It is the default luminance defined in ffmpeg's zscale filter.
# https://github.com/sekrit-twc/zimg/blob/master/src/zimg/colorspace/colorspace.cpp#L97
# in `Rec. ITU-R BT.2100-1 (06/2017) note 5e`, PEAK_LUMINANCE = 1000.0
PEAK_LUMINANCE = sympy.Float("100.0", 37)  # default value in ffmpeg zscale
# https://github.com/sekrit-twc/zimg/blob/master/src/zimg/colorspace/gamma.cpp#L365
ARIB_PEAK_LUMINANCE = sympy.Float("1000.0", 37)
ST2084_PEAK_LUMINANCE = sympy.Float("10000.0", 37)  # unit cd/m**2
ARIB_SCALE = PEAK_LUMINANCE / ARIB_PEAK_LUMINANCE
ST2084_SCALE = PEAK_LUMINANCE / ST2084_PEAK_LUMINANCE


# In limited range, values V can values can go beyond the range [0, 1].
# In the other direction, values from the workspace L can also fall outside the [0, 1] range.
# Rather than clamp, these EOTFs are extended on R.
# This simplifies calculations and avoids some saturation.
TRC = {  # l to l' and l' to l
    # in the ITU-T H.273 (V4), nominal range is defined in [0, 12],
    # this version is rescaled in range [0, 1]. Match with colour.models.oetf_ARIBSTDB67(12*L)
    "arib-std-b67": (
        sympy.Piecewise(
            (L, L <= 0),  # C0 prolongation because C1 impossible
            (
                sympy.sqrt(sympy.Float("3.0", 37) * L * ARIB_SCALE),
                L <= sympy.Rational("1/12").n(37) / ARIB_SCALE,
            ),
            (A_ARIB * sympy.log(sympy.Float("12.0", 37) * L * ARIB_SCALE - B_ARIB) + C_ARIB, True),
        ),
        sympy.Piecewise(
            (V, V <= 0),
            (V * V * sympy.Rational("1/3").n(37) / ARIB_SCALE, V <= sympy.Float("0.5", 37)),
            (
                sympy.Rational("1/12").n(37) * (sympy.exp((V-C_ARIB)/A_ARIB) + B_ARIB) / ARIB_SCALE,
                True,
            ),
        ),
    ),
    "bt709": (  # ITU-R BT.709-6 (06/2015) <https://www.itu.int/rec/R-REC-BT.709>
        sympy.Piecewise(  # natural C1 prolongation
            (sympy.Float("4.5", 37)*L, L <= BETA_REC709),
            (ALPHA_REC709*L**sympy.Float("0.45", 37)-(ALPHA_REC709-1), True),
        ),
        sympy.Piecewise(
            (V / sympy.Float("4.5", 37), V <= BETA_REC709*sympy.Float("4.5", 37)),
            (((V+(ALPHA_REC709-1))/ALPHA_REC709)**(1/sympy.Float("0.45", 37)), True)
        ),
    ),
    "gamma22": (  # bt470m, approximation of sRGB
        sympy.Piecewise(
            (L, L <= 0),  # C0 prolongation because C1 impossible
            (L**(1/sympy.Float("2.2", 37)), True),
        ),
        sympy.Piecewise(
            (V, V <= 0),
            (V**sympy.Float("2.2", 37), True),
        ),
    ),
    "gamma26": (  # bt470m
        sympy.Piecewise(
            (L, L <= 0),  # C0 prolongation because C1 impossible
            (L**(1/sympy.Float("2.6", 37)), True),
        ),
        sympy.Piecewise(
            (V, V <= 0),
            (V**sympy.Float("2.6", 37), True),
        ),
    ),
    "gamma28": (  # bt470bg
        sympy.Piecewise(
            (L, L <= 0),  # C0 prolongation because C1 impossible
            (L**(1/sympy.Float("2.8", 37)), True),
        ),
        sympy.Piecewise(
            (V, V <= 0),
            (V**sympy.Float("2.8", 37), True),
        ),
    ),
    "iec61966-2-1, iec61966_2_1": (  # sRGB
        sympy.Piecewise(  # natural C1 prolongation
            (sympy.Float("12.92", 37)*L, L <= BETA_IEC61966),
            (ALPHA_IEC61966*L**(1/sympy.Float("2.4", 37))-(ALPHA_IEC61966-1), True),
        ),
        sympy.Piecewise(
            (V * (1/sympy.Float("12.92", 37)), V <= BETA_IEC61966*sympy.Float("12.92", 37)),
            (((V+(ALPHA_IEC61966-1))/ALPHA_IEC61966)**sympy.Float("2.4", 37), True),
        ),
    ),
    "ipt": (  # `RIT Digital Institutional Repository` <https://scholarworks.rit.edu/theses/2858/>
        sympy.Piecewise(
            (L, L <= 0),  # C0 prolongation because C1 impossible
            (L**sympy.Float("0.43", 37), True),
        ),
        sympy.Piecewise(
            (V, V <= 0),
            (V**(1/sympy.Float("0.43", 37)), True),
        ),
    ),
    "linear": (L, V),
    # By design, this function is not bijective on [0, 1/100].
    # This function, slightly modified on this interval, makes it bijective.
    # This is a continuity connection of a linear function of arbitrary slope alpha=1/65535,
    # and the original function.
    # The transition point is ``-LambertW(-alpha*log(10)/50)/(2*alpha*log(10))``.
    "log100, log": (
        sympy.Piecewise(  # natural C1 prolongation
            (
                sympy.Float("0.00001525902189669642175936522468909742885", 37) * L,
                L <= sympy.Float("0.01000000702704667750197159799752265256", 37),
            ),
            (1+(sympy.log(L)/sympy.log(10))/2, True),
        ),
        sympy.Piecewise(
            (
                sympy.Float("65535.0", 37) * V,
                V <= sympy.Float("0.0000001525903261928233387040756541927619219", 37),
            ),
            (10**(2*V - 2), True),
        ),
    ),
    # To make this function bijective, we apply the same methodology as for the log100 function.
    # The transition point is ``-2*LambertW(-sqrt(10)*alpha*log(10)/400)/(5*alpha*log(10))``.
    "log316, log_sqrt": (
        sympy.Piecewise(  # natural C1 prolongation
            (
                sympy.Float("0.00001525902189669642175936522468909742885", 37) * L,
                L <= sympy.Float("0.003162278538548654136151340181558209886", 37),
            ),
            (1+sympy.Float("0.4", 37) * (sympy.log(L)/sympy.log(10)), True),
        ),
        sympy.Piecewise(
            (
                sympy.Float("65535.0", 37) * V,
                V <= sympy.Float("0.00000004825327746316707310828321021680338575", 37),
            ),
            (10**(sympy.Float("2.5", 37)*V - sympy.Float("2.5", 37)), True),
        ),
    ),
    # It is also defined with more details in SMPTE ST 2084:2017
    "smpte2084": (  # Rec. ITU-R BT.2100-2 perceptual quantization (PQ) system
        # ((c1 + c2 * L**n) / (1 + c3 * L**n))**m,
        sympy.Piecewise(  # C0 prolongation because C1 impossible
            (L, L <= 0),
            (
                (
                    (
                        sympy.Rational("107/128").n(37)
                        + sympy.Rational("2413/128").n(37)
                        * (L*ST2084_SCALE)**sympy.Rational("1305/8192").n(37)
                    )
                    / (
                        1 + sympy.Rational("2392/128").n(37)
                        * (L*ST2084_SCALE)**sympy.Rational("1305/8192").n(37)
                    )
                )**sympy.Rational("2523/32").n(37),
                True,
            ),
        ),
        # ((-V**(1/m) + c1)/(V**(1/m)*c3 - c2))**(1/n),
        sympy.Piecewise(
            (V, V <= 0),
            (
                (
                    (-V**sympy.Rational("32/2523").n(37) + sympy.Rational("107/128").n(37))
                    / (
                        V**sympy.Rational("32/2523").n(37)*sympy.Rational("2392/128").n(37)
                        - sympy.Rational("2413/128").n(37)
                    )
                )**sympy.Rational("8192/1305").n(37) / ST2084_SCALE,
                True,
            ),
        ),
    ),
    # We have smpte428([0, 1]) = [0, 1-esp[
    "smpte428, smpte428_1": (  # natural C1 prolongation
        sympy.Piecewise(  # C0 prolongation because C1 impossible
            (L, L <= 0),
            (
                (
                    sympy.Float("0.9165552797403093374069123544013748329", 37) * L
                )**sympy.Float("0.3846153846153846153846153846153846154"),
                True,
            ),
        ),
        sympy.Piecewise(  # natural C1 prolongation
            (V, V <= 0),
            (
                sympy.Float("1.0910416666666666666666666666666667", 37) * V**sympy.Float("2.6", 37),
                True,
            ),
        ),
    ),
    "smpte240m": (
        sympy.Piecewise(  # natural C1 prolongation
            (sympy.Float("4.0", 37)*L, L <= BETA_SMPTE240M),
            (ALPHA_SMPTE240M*L**sympy.Float("0.45", 37)-(ALPHA_SMPTE240M-1), True),
        ),
        sympy.Piecewise(
            (sympy.Float("0.25", 37)*V, V <= 4*BETA_SMPTE240M),
            (((V+(ALPHA_SMPTE240M-1))/ALPHA_SMPTE240M)**(1/sympy.Float("0.45", 37)), True),
        ),
    ),
}

TRC |= {
    "bt2020": TRC["bt709"],  # ITU-R BT.2020-2 (10/2015) <https://www.itu.int/rec/R-REC-BT.2020>
    "bt2020-10, bt2020_10bit": TRC["bt709"],
    "bt2020-12, bt2020_12bit": TRC["bt709"],
    "bt470bg": TRC["gamma28"],
    "bt470m": TRC["gamma22"],
    "bt601": TRC["bt709"],  # UIT-R BT.601-7 (03/2011) <https://www.itu.int/rec/R-REC-BT.601>
    "hlg": TRC["arib-std-b67"],  # <github.com/m13253/colorspace-routines/blob/master/gammas.py>
    "smpte170m": TRC["bt709"],
    "iec61966-2-4, iec61966_2_4": (
        sympy.sign(L) * TRC["bt709"][0].subs(L, sympy.Abs(L)),
        sympy.sign(V) * TRC["bt709"][1].subs(V, sympy.Abs(V)),
    ),
    "bt1361e, bt1361": TRC["bt709"],  # wrong for negative L values
    "srgb": TRC["iec61966-2-1, iec61966_2_1"],  # alias given by ITU
    "smpte431": TRC["gamma26"],  # `SMPTE RP 431-2:2011 Table A.1 sec 7.7`
}


__doc__ += f"""
PRIMARIES
---------
.. csv-table:: The tristimulus primaries colors (gamut), defined in the CIE XY space.
    :header: name, red, green, blue, white
    :widths: auto

    {"\n    ".join(
    f'"{n}", "x={rx}, y={ry}", "x={gx}, y={gy}", "x={bx}, y={by}", "x={wx}, y={wy}"'
    for n, ((rx, ry), (gx, gy), (bx, by), (wx, wy))
    in ((n, PRIMARIES[n]) for n in sorted(PRIMARIES)))}

TRC
---
.. csv-table:: The transfer functions (gamma), Let the luminance be Y or L, the luma Y' or V.
    :header: name, ":math:`V = f(L)`", ":math:`L = f^{{-1}}(V)`"
    :widths: auto

    {"\n    ".join(
        f'"{n}", ":math:`{sympy.latex(l2v)}`", ":math:`{sympy.latex(v2l)}`"'
        for n, (l2v, v2l) in ((n, TRC[n]) for n in sorted(TRC)))}
"""
