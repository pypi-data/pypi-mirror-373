#!/usr/bin/env python3

"""Split a stream in several slices."""

from fractions import Fraction
import numbers
import typing

import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideoWrapper
from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.filter.cut import FilterCut


class FilterVideoCut(FilterCut, Filter):
    """Splits the video stream at the given positions.

    Examples
    --------
    >>> from cutcutcodec.core.filter.video.cut import FilterVideoCut
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (stream_a,) = GeneratorVideoNoise(0).out_streams
    >>> (stream_b,) = GeneratorVideoNoise(0).out_streams
    >>> a_0, b_0, a_1, b_1, a_2, b_2 = FilterVideoCut([stream_a, stream_b], 10, 20).out_streams
    >>>
    >>> a_0.beginning, a_0.duration
    (Fraction(0, 1), Fraction(10, 1))
    >>> a_2.beginning, a_2.duration
    (Fraction(20, 1), inf)
    >>> b_1.beginning, b_1.duration
    (Fraction(10, 1), Fraction(10, 1))
    >>> b_2.beginning, b_2.duration
    (Fraction(20, 1), inf)
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream], *limits: numbers.Real):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        limits : numbers.Real
            Transmitted to ``cutcutcodec.core.filter.cut.FilterCut.init``.
        """
        super().__init__(in_streams, in_streams)
        self._limits, out_streams = self.init(in_streams, _StreamVideoCut, *limits)
        super().__init__(in_streams, out_streams)

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"limits"}, set(state)
        limits = map(Fraction, state["limits"])
        FilterVideoCut.__init__(self, in_streams, *limits)


class _StreamVideoCut(StreamVideoWrapper):
    """Select a slice of a video stream."""

    def __init__(
        self,
        node: FilterVideoCut,
        index: numbers.Integral,
        l_min: numbers.Real,
        l_max: numbers.Real,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.classes.node.Node
            The parent node.
        filter : cutcutcodec.core.filter.video.cut.FilterVideoCut
            Transmitted to ``cutcutcodec.core.classes.stream_video.StreamVideoWrapper``.
        index : numbers.Integral
            Transmitted to ``cutcutcodec.core.classes.stream_video.StreamVideoWrapper``.
        l_min : numbers.Real
            The low absolute limit.
        l_max : numbers.Real
            The high absolute limit.
        """
        assert isinstance(node, FilterVideoCut), node.__class__.__name__
        assert isinstance(l_min, numbers.Real), l_min.__class__.__name__
        assert isinstance(l_max, numbers.Real), l_max.__class__.__name__
        super().__init__(node, index)
        self.l_min, self.l_max = l_min, l_max

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        if timestamp >= self.l_max or timestamp < self.l_min:
            raise OutOfTimeRange(
                f"the stream has been truncated under "
                f"{self.beginning} and over {self.beginning+self.duration} seconds, "
                f"evaluation at {timestamp} seconds"
            )
        return self.stream._snapshot(timestamp, mask)  # pylint: disable=W0212

    @property
    def beginning(self) -> Fraction:
        return max(min(self.l_min, self.l_max), self.stream.beginning)

    @property
    def duration(self) -> Fraction | float:
        end = min(max(self.l_min, self.l_max), self.stream.beginning+self.stream.duration)
        return end - self.beginning
