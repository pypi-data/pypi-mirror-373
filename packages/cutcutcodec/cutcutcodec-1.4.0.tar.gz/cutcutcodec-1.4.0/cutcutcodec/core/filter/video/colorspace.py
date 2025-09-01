#!/usr/bin/env python3

"""Switches from one color space to another."""

import typing

import sympy

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.stream_video import StreamVideo
from .equation import FilterVideoEquation


class FilterVideoColorspace(FilterVideoEquation):
    """Switches from one color space to another.

    This filter is built automatically through the
    ``cutcutcodec.core.io.read`` and ``cutcutcodec.core.io.write`` functions,
    and should never be instantiated by a user.

    Examples
    --------
    >>> from cutcutcodec.core.classes.colorspace import Colorspace
    >>> from cutcutcodec.core.filter.video.colorspace import FilterVideoColorspace
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>> (stream,) = GeneratorVideoNoise(0).out_streams
    >>> stream.colorspace
    Colorspace('rgb', 'bt709')
    >>> dst = Colorspace("rgb", "bt2020")
    >>> (stream_rgb_bt2020,) = FilterVideoColorspace([stream], dst).out_streams
    >>> stream_rgb_bt2020.colorspace
    Colorspace('rgb', 'bt2020')
    >>> stream_rgb_bt2020.snapshot(0, (13, 9))[..., 0]
    tensor([[0.4824, 0.2114, 0.5962, 0.6170, 0.2989, 0.4423, 0.4960, 0.7960, 0.3711],
            [0.6872, 0.8248, 0.4061, 0.4428, 0.5387, 0.5219, 0.7068, 0.6459, 0.5698],
            [0.8770, 0.3703, 0.2970, 0.7248, 0.4062, 0.7301, 0.4954, 0.3394, 0.8245],
            [0.7000, 0.8139, 0.5692, 0.6791, 0.8107, 0.8861, 0.6236, 0.3917, 0.2450],
            [0.6592, 0.7217, 0.0917, 0.3172, 0.4469, 0.7582, 0.2397, 0.4258, 0.4769],
            [0.7207, 0.1743, 0.4559, 0.5712, 0.3713, 0.4069, 0.3752, 0.1172, 0.3533],
            [0.5858, 0.8497, 0.8888, 0.1853, 0.6720, 0.7482, 0.8111, 0.4787, 0.4374],
            [0.7285, 0.7802, 0.3971, 0.4243, 0.5180, 0.4387, 0.2403, 0.5947, 0.4026],
            [0.1293, 0.3936, 0.8009, 0.8568, 0.4814, 0.7028, 0.3322, 0.3411, 0.8715],
            [0.7737, 0.6067, 0.5999, 0.5105, 0.4649, 0.3613, 0.6834, 0.5160, 0.6292],
            [0.7944, 0.3924, 0.5063, 0.5044, 0.3406, 0.2338, 0.5204, 0.3408, 0.5352],
            [0.5846, 0.6981, 0.2822, 0.3278, 0.6432, 0.6354, 0.4946, 0.6582, 0.1538],
            [0.1537, 0.2207, 0.6140, 0.6910, 0.5170, 0.5020, 0.6288, 0.1427, 0.3845]])
    >>>
    """

    def __init__(
        self,
        in_streams: typing.Iterable[StreamVideo],
        colorspace: typing.Optional[Colorspace | str] = None,
        alpha: bool = False,
    ):
        """Initialise the filter.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to :py:class:`cutcutcodec.core.filter.video.equation.FilterVideoEquation`.
        colorspace : str or Colorspace, optional
            The destination colorspace into which the streams will be converted.
            Source color spaces are read from the .colorspace attribute of source streams.
            By default, the selected space is the working workspace given by
            :py:meth:`cutcutcodec.core.classes.Colorspace.from_default_working`.
        alpha : boolean
            True to append the alpha channel, False overwise.
        """
        assert isinstance(alpha, bool), alpha.__class__.__name__

        # get dst colorspace
        if colorspace is None:
            dst = Colorspace.from_default_working()
        else:
            dst = Colorspace(colorspace)

        # get dst colorspace
        in_streams = list(in_streams)
        if len(src := {s.colorspace for s in in_streams}) != 1:
            raise ValueError(f"ambiguous input colorspace {src}")
        src = src.pop()

        # create streams
        conv = (
            src.to_equation(dst)
            .xreplace(dict(zip(src.symbols, sympy.symbols("r0 g0 b0", real=True))))
        )
        if alpha:
            conv = (*conv, "a0")
        super().__init__(in_streams, *conv)

        # set colorspace value
        for stream in self.out_streams:
            stream.colorspace = dst
