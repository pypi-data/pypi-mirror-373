#!/usr/bin/env python3

"""Allow to temporarily translate a video sequence."""

from fractions import Fraction
import numbers
import typing

import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideoWrapper


class FilterVideoDelay(Filter):
    """Change the beginning time of a stream.

    Attributes
    ----------
    delay : Fraction
        The delay append to the original beginning time of the stream (readonly).
        a positive value indicates that the output flow is later than the input flow.

    Examples
    --------
    >>> from cutcutcodec.core.filter.video.delay import FilterVideoDelay
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> (s_trans_video,) = FilterVideoDelay([s_base_video], 10).out_streams
    >>>
    >>> (s_base_video.snapshot(0, (1, 1)) == s_trans_video.snapshot(10, (1, 1))).all()
    tensor(True)
    >>> (s_base_video.snapshot(10, (1, 1)) == s_trans_video.snapshot(10, (1, 1))).all()
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
            The temporal translation value to apply at the output video stream.
        """
        assert isinstance(delay, numbers.Real), delay.__class__.__name__

        self._delay = Fraction(delay)
        super().__init__(in_streams, in_streams)
        super().__init__(
            in_streams, [_StreamVideoTranslate(self, index) for index in range(len(in_streams))]
        )

    def _getstate(self) -> dict:
        return {"delay": str(self.delay)}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"delay"}, set(state)
        FilterVideoDelay.__init__(self, in_streams, Fraction(state["delay"]))

    @property
    def delay(self) -> Fraction:
        """Return the delay append to the original beginning time of the stream."""
        return self._delay


class _StreamVideoTranslate(StreamVideoWrapper):
    """Translate a video stream from a certain delay."""

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        frame = self.stream._snapshot(timestamp - self.node.delay, mask)  # pylint: disable=W0212
        frame.time = timestamp
        return frame

    @property
    def beginning(self) -> Fraction:
        return self.stream.beginning + self.node.delay
