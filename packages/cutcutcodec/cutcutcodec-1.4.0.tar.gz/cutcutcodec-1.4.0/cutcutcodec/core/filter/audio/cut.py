#!/usr/bin/env python3

"""Split a stream in several slices."""

from fractions import Fraction
import numbers
import typing

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudioWrapper
from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.filter.cut import FilterCut


class FilterAudioCut(FilterCut, Filter):
    """Splits the audio stream at the given positions.

    Examples
    --------
    >>> from cutcutcodec.core.filter.audio.cut import FilterAudioCut
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>>
    >>> (stream_a,) = GeneratorAudioNoise(0).out_streams
    >>> (stream_b,) = GeneratorAudioNoise(0).out_streams
    >>> a_0, b_0, a_1, b_1, a_2, b_2 = FilterAudioCut([stream_a, stream_b], 10, 20).out_streams
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
        self._limits, out_streams = self.init(in_streams, _StreamAudioCut, *limits)
        super().__init__(in_streams, out_streams)

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"limits"}, set(state)
        limits = map(Fraction, state["limits"])
        FilterAudioCut.__init__(self, in_streams, *limits)


class _StreamAudioCut(StreamAudioWrapper):
    """Select a slice of an audio stream."""

    def __init__(
        self,
        node: FilterAudioCut,
        index: numbers.Integral,
        l_min: numbers.Real,
        l_max: numbers.Real,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.classes.node.Node
            The parent node.
        filter : cutcutcodec.core.classes.filter.Filter
            Transmitted to ``cutcutcodec.core.classes.stream_audio.StreamAudioWrapper``.
        index : numbers.Integral
            Transmitted to ``cutcutcodec.core.classes.stream_audio.StreamAudioWrapper``.
        l_min : numbers.Real
            The low absolute limit.
        l_max : numbers.Real
            The high absolute limit.
        """
        assert isinstance(node, FilterAudioCut), node.__class__.__name__
        assert isinstance(l_min, numbers.Real), l_min.__class__.__name__
        assert isinstance(l_max, numbers.Real), l_max.__class__.__name__
        super().__init__(node, index)
        self.l_min, self.l_max = l_min, l_max

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        if timestamp + Fraction(samples, rate) > self.l_max or timestamp < self.l_min:
            raise OutOfTimeRange(
                "the stream has been truncated under "
                f"{self.beginning} and over {self.beginning+self.duration} seconds, "
                f"eval from {timestamp} to length {Fraction(samples, rate)}"
            )
        return self.stream._snapshot(timestamp, rate, samples)  # pylint: disable=W0212

    @property
    def beginning(self) -> Fraction:
        return max(min(self.l_min, self.l_max), self.stream.beginning)

    @property
    def duration(self) -> Fraction | float:
        end = min(max(self.l_min, self.l_max), self.stream.beginning+self.stream.duration)
        return end - self.beginning
