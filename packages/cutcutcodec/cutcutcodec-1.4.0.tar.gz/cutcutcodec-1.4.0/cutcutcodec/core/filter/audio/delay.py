#!/usr/bin/env python3

"""Allow to temporarily translate an audio sequence."""

from fractions import Fraction
import numbers
import typing

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudioWrapper


class FilterAudioDelay(Filter):
    """Change the beginning time of a stream.

    Attributes
    ----------
    delay : Fraction
        The delay append to the original beginning time of the stream (readonly).
        a positive value indicates that the output flow is later than the input flow.

    Examples
    --------
    >>> from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>>
    >>> (s_base_audio,) = GeneratorAudioNoise(0).out_streams
    >>> (s_trans_audio,) = FilterAudioDelay([s_base_audio], 10).out_streams
    >>>
    >>> (s_base_audio.snapshot(0) == s_trans_audio.snapshot(10)).all()
    tensor(True)
    >>> (s_base_audio.snapshot(10) == s_trans_audio.snapshot(10)).all()
    tensor(False)
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream], delay: numbers.Real):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        delay : numbers.Real
            The temporal translation value to apply at the output audio stream.
        """
        assert isinstance(delay, numbers.Real), delay.__class__.__name__

        self._delay = Fraction(delay)
        super().__init__(in_streams, in_streams)
        super().__init__(
            in_streams, [_StreamAudioTranslate(self, index) for index in range(len(in_streams))]
        )

    def _getstate(self) -> dict:
        return {"delay": str(self.delay)}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"delay"}, set(state)
        FilterAudioDelay.__init__(self, in_streams, Fraction(state["delay"]))

    @property
    def delay(self) -> Fraction:
        """Return the delay append to the original beginning time of the stream."""
        return self._delay


class _StreamAudioTranslate(StreamAudioWrapper):
    """Translate an audio stream from a certain delay."""

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        frame = self.stream._snapshot(  # pylint: disable=W0212
            timestamp - self.node.delay, rate, samples
        )
        frame = FrameAudio(frame.time + self.node.delay, rate, frame.layout, frame)
        return frame

    @property
    def beginning(self) -> Fraction:
        return self.stream.beginning + self.node.delay
