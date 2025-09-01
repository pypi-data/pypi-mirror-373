#!/usr/bin/env python3

"""Allow to combine probabilistic laws."""

import math
import numbers

from sympy.core.basic import Basic
import torch

from cutcutcodec.core.compilation.parse import parse_to_sympy
from cutcutcodec.core.compilation.sympy_to_torch import Lambdify


def compute_cumhist(
    expr: Basic | numbers.Real | str, n_per_bars: numbers.Integral = 3
) -> torch.Tensor:
    """Calculate the cumulative histogram of a law combination of reduced uniform probability.

    Parameters
    ----------
    expr : str or sympy.Basic
        The combination expression of uniform laws.
        The ``free_symbols`` variables correspond
        to the draws of these independent reduced uniform distributions.
    n_per_bars : int
        The average number of samples by bars if there is enouth memory.

    Returns
    -------
    min : float
        The minimum value of the output of the expression `expr`.
    max : float
        The maximum value of the output of the expression `expr`.
    cumhist : torch.Tensor
        The float 32 cumulative histogram (1d vector) constitued of 256 bins.
        the min and max of the histograms match with the min and max of the expr.

    Notes
    -----
    This function can use some Gio of RAM.

    Examples
    --------
    >>> from cutcutcodec.core.edit.factor.proba import compute_cumhist
    >>> min_, max_, cum = compute_cumhist("1 + x1 + x2")
    >>> round(min_), round(max_)
    (1, 3)
    >>> cum.round(decimals=3)
    tensor([0.0000, 0.0000, 0.0000, 0.0010, 0.0010, 0.0010, 0.0020, 0.0020, 0.0030,
            0.0030, 0.0040, 0.0040, 0.0050, 0.0060, 0.0070, 0.0080, 0.0090, 0.0100,
            0.0110, 0.0120, 0.0140, 0.0150, 0.0160, 0.0180, 0.0190, 0.0210, 0.0220,
            0.0240, 0.0260, 0.0280, 0.0290, 0.0310, 0.0330, 0.0350, 0.0380, 0.0400,
            0.0420, 0.0440, 0.0470, 0.0490, 0.0510, 0.0540, 0.0570, 0.0590, 0.0620,
            0.0650, 0.0680, 0.0700, 0.0730, 0.0760, 0.0800, 0.0830, 0.0860, 0.0890,
            0.0930, 0.0960, 0.0990, 0.1030, 0.1060, 0.1100, 0.1140, 0.1180, 0.1210,
            0.1250, 0.1290, 0.1330, 0.1370, 0.1410, 0.1460, 0.1500, 0.1540, 0.1580,
            0.1630, 0.1670, 0.1720, 0.1770, 0.1810, 0.1860, 0.1910, 0.1960, 0.2010,
            0.2060, 0.2110, 0.2160, 0.2210, 0.2260, 0.2310, 0.2370, 0.2420, 0.2480,
            0.2530, 0.2590, 0.2640, 0.2700, 0.2760, 0.2820, 0.2880, 0.2930, 0.2990,
            0.3060, 0.3120, 0.3180, 0.3240, 0.3300, 0.3370, 0.3430, 0.3500, 0.3560,
            0.3630, 0.3700, 0.3760, 0.3830, 0.3900, 0.3970, 0.4040, 0.4110, 0.4180,
            0.4250, 0.4330, 0.4400, 0.4470, 0.4550, 0.4620, 0.4700, 0.4770, 0.4850,
            0.4930, 0.5000, 0.5070, 0.5150, 0.5230, 0.5300, 0.5380, 0.5450, 0.5530,
            0.5600, 0.5670, 0.5750, 0.5820, 0.5890, 0.5960, 0.6030, 0.6100, 0.6170,
            0.6240, 0.6300, 0.6370, 0.6440, 0.6500, 0.6570, 0.6630, 0.6700, 0.6760,
            0.6820, 0.6880, 0.6940, 0.7010, 0.7070, 0.7120, 0.7180, 0.7240, 0.7300,
            0.7360, 0.7410, 0.7470, 0.7520, 0.7580, 0.7630, 0.7690, 0.7740, 0.7790,
            0.7840, 0.7890, 0.7940, 0.7990, 0.8040, 0.8090, 0.8140, 0.8190, 0.8230,
            0.8280, 0.8330, 0.8370, 0.8420, 0.8460, 0.8500, 0.8540, 0.8590, 0.8630,
            0.8670, 0.8710, 0.8750, 0.8790, 0.8820, 0.8860, 0.8900, 0.8940, 0.8970,
            0.9010, 0.9040, 0.9070, 0.9110, 0.9140, 0.9170, 0.9200, 0.9240, 0.9270,
            0.9300, 0.9320, 0.9350, 0.9380, 0.9410, 0.9430, 0.9460, 0.9490, 0.9510,
            0.9530, 0.9560, 0.9580, 0.9600, 0.9620, 0.9650, 0.9670, 0.9690, 0.9710,
            0.9720, 0.9740, 0.9760, 0.9780, 0.9790, 0.9810, 0.9820, 0.9840, 0.9850,
            0.9860, 0.9880, 0.9890, 0.9900, 0.9910, 0.9920, 0.9930, 0.9940, 0.9950,
            0.9960, 0.9960, 0.9970, 0.9970, 0.9980, 0.9980, 0.9990, 0.9990, 0.9990,
            1.0000, 1.0000, 1.0000, 1.0000])
    >>>
    """
    assert isinstance(expr, (Basic, numbers.Real, str)), expr
    assert isinstance(n_per_bars, numbers.Integral), numbers.__class__.__name__
    assert n_per_bars > 0, n_per_bars

    expr = parse_to_sympy(expr)
    symbs = sorted(map(str, expr.free_symbols))
    assert symbs, "constant expressions are not yet supported"
    func = Lambdify(expr, compile=False)

    n_per_bars = min(n_per_bars, 268435456**(1/len(symbs))/256)  # nbr = (256*n_per_bars)**n_symbs
    start = 0.001953125 / n_per_bars  # (1 / (2*n_per_bars)) / 256
    nbr = max(2, 2**round(math.log(n_per_bars*256, 2)))  # limited the bias if limited memory
    lins = torch.linspace(start, 1.0-start, nbr)
    lins = [lins] * len(symbs)
    for i in range(len(symbs)-1):
        lins = [lin.unsqueeze(i+1) for lin in lins]
    lins = [lin.transpose(0, i) for i, lin in enumerate(lins)]

    hist = func(**dict(zip(symbs, lins))).flatten()
    min_, max_ = torch.aminmax(hist)
    min_, max_ = min_.item(), max_.item()
    nbr = hist.shape[0]
    hist, _ = torch.histogram(hist, bins=256)
    hist = torch.cumsum(hist, dim=0, out=hist)
    hist /= nbr  # [0, 1]
    return min_, max_, hist


def inv_cumhist(min_: numbers.Real, max_: numbers.Real, cumhist: torch.Tensor) -> list:
    """Reverse the histogram of the estimation of the proba repartition function.

    Parameters
    ----------
    min_ : numbers.Real
        The minimum value of the reversed repartition function.
    max_ : numbers.Real
        The minimum value of the reversed repartition function.
    cumhist : torch.Tensor
        The strictely growing repartition function between 0 and 1.
        Only y values are represented like a 1d torch vector.
        The x axis is implicitely a linspace betwen 0 and 1.

    Return
    ------
    invrep : torch.Tensor
        An estimation of the inverse function (1d vector).
        The dimension is choose to be the same as the input histogram len.

    Examples
    --------
    >>> from cutcutcodec.core.edit.factor.proba import compute_cumhist, inv_cumhist
    >>> min_, max_, cum = compute_cumhist("1 + x1 + x2")
    >>> inv_cumhist(min_, max_, cum)
    tensor([0.9985, 1.0814, 1.1181, 1.1462, 1.1699, 1.1908, 1.2096, 1.2270, 1.2432,
            1.2583, 1.2727, 1.2863, 1.2994, 1.3119, 1.3239, 1.3356, 1.3468, 1.3577,
            1.3683, 1.3785, 1.3885, 1.3983, 1.4079, 1.4172, 1.4263, 1.4352, 1.4440,
            1.4526, 1.4610, 1.4693, 1.4775, 1.4855, 1.4933, 1.5011, 1.5087, 1.5163,
            1.5237, 1.5310, 1.5382, 1.5453, 1.5524, 1.5593, 1.5662, 1.5730, 1.5797,
            1.5863, 1.5929, 1.5994, 1.6058, 1.6121, 1.6184, 1.6246, 1.6308, 1.6369,
            1.6429, 1.6489, 1.6549, 1.6608, 1.6666, 1.6724, 1.6781, 1.6838, 1.6894,
            1.6950, 1.7006, 1.7061, 1.7116, 1.7170, 1.7223, 1.7277, 1.7330, 1.7383,
            1.7435, 1.7487, 1.7538, 1.7590, 1.7641, 1.7691, 1.7741, 1.7791, 1.7841,
            1.7890, 1.7939, 1.7988, 1.8036, 1.8084, 1.8132, 1.8180, 1.8227, 1.8274,
            1.8321, 1.8367, 1.8414, 1.8459, 1.8505, 1.8551, 1.8596, 1.8641, 1.8686,
            1.8730, 1.8775, 1.8819, 1.8863, 1.8906, 1.8950, 1.8993, 1.9036, 1.9079,
            1.9122, 1.9164, 1.9206, 1.9248, 1.9290, 1.9332, 1.9374, 1.9415, 1.9456,
            1.9497, 1.9538, 1.9578, 1.9619, 1.9659, 1.9699, 1.9739, 1.9779, 1.9819,
            1.9860, 1.9905, 1.9947, 1.9986, 2.0025, 2.0065, 2.0105, 2.0145, 2.0185,
            2.0225, 2.0266, 2.0306, 2.0347, 2.0388, 2.0429, 2.0470, 2.0512, 2.0554,
            2.0596, 2.0638, 2.0680, 2.0722, 2.0765, 2.0808, 2.0851, 2.0894, 2.0938,
            2.0981, 2.1025, 2.1069, 2.1114, 2.1158, 2.1203, 2.1248, 2.1293, 2.1339,
            2.1384, 2.1430, 2.1477, 2.1523, 2.1570, 2.1617, 2.1664, 2.1712, 2.1760,
            2.1808, 2.1856, 2.1905, 2.1954, 2.2003, 2.2053, 2.2102, 2.2153, 2.2203,
            2.2254, 2.2306, 2.2357, 2.2409, 2.2461, 2.2514, 2.2567, 2.2620, 2.2674,
            2.2728, 2.2783, 2.2838, 2.2894, 2.2950, 2.3006, 2.3063, 2.3120, 2.3178,
            2.3236, 2.3295, 2.3354, 2.3414, 2.3475, 2.3536, 2.3598, 2.3660, 2.3723,
            2.3786, 2.3850, 2.3915, 2.3981, 2.4047, 2.4114, 2.4182, 2.4251, 2.4320,
            2.4390, 2.4462, 2.4534, 2.4607, 2.4681, 2.4757, 2.4833, 2.4911, 2.4989,
            2.5069, 2.5151, 2.5234, 2.5318, 2.5404, 2.5492, 2.5581, 2.5672, 2.5765,
            2.5861, 2.5959, 2.6059, 2.6161, 2.6267, 2.6376, 2.6488, 2.6605, 2.6725,
            2.6850, 2.6981, 2.7117, 2.7261, 2.7412, 2.7574, 2.7748, 2.7936, 2.8145,
            2.8382, 2.8663, 2.9030, 2.9909])
    >>>
    """
    assert isinstance(min_, numbers.Real), min_.__class__.__name__
    assert isinstance(max_, numbers.Real), max_.__class__.__name__
    assert min_ < max_, (min_, max_)
    assert isinstance(cumhist, torch.Tensor), cumhist.__class__.__name__
    assert cumhist.ndim == 1, cumhist.shape

    cum_min, cum_max = torch.aminmax(cumhist)
    cum_min, cum_max = cum_min.item(), cum_max.item()

    prob = torch.linspace(
        0, 1, cumhist.shape[0], dtype=cumhist.dtype, device=cumhist.device
    )  # we can choose any len
    index = cumhist.unsqueeze(0) > prob.unsqueeze(1)
    index = index.to(torch.uint8, copy=False)
    index = torch.argmax(index, dim=1)
    index[0], index[-1] = 1, cumhist.shape[0]-1
    p_max = cumhist[index]
    index -= 1
    p_min = cumhist[index]
    d_p = p_max-p_min
    shift = torch.where(d_p != 0, (prob-p_min)/d_p, .5)
    out = (index + shift) * (max_-min_)/cumhist.shape[0] + min_

    return out
