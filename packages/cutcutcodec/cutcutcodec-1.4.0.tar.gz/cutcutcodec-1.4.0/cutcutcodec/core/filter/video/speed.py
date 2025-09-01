#!/usr/bin/env python3

"""Allow to temporarily change the speed of a video sequence."""

from fractions import Fraction
import numbers
import typing

import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideoWrapper


class FilterVideoSpeed(Filter):
    """Change the beginning time of a stream.

    Attributes
    ----------
    speed : Fraction
        The speed factor (readonly).

    Examples
    --------
    >>> from cutcutcodec.core.filter.video.speed import FilterVideoSpeed
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> (s_speed_video,) = FilterVideoSpeed([s_base_video], 2).out_streams
    >>>
    >>> (s_base_video.snapshot(0, (1, 1)) == s_speed_video.snapshot(0, (1, 1))).all()
    tensor(True)
    >>> (s_base_video.snapshot(2, (1, 1)) == s_speed_video.snapshot(1, (1, 1))).all()
    tensor(True)
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream], speed: numbers.Real):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        speed : numbers.Real
            The acceleration factor in ]0, oo[, 1 means the speed is unchanged.
        """
        assert isinstance(speed, numbers.Real), speed.__class__.__name__
        assert speed > 0, speed
        self._speed = Fraction(speed)
        super().__init__(in_streams, in_streams)
        super().__init__(
            in_streams, [_StreamVideoSpeed(self, index) for index in range(len(in_streams))]
        )

    def _getstate(self) -> dict:
        return {"speed": str(self._speed)}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"speed"}, set(state)
        FilterVideoSpeed.__init__(self, in_streams, Fraction(state["speed"]))

    @property
    def speed(self) -> Fraction:
        """Return the speed factor."""
        return self._speed


class _StreamVideoSpeed(StreamVideoWrapper):
    """Change the speed of a video stream."""

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        beginning = self.stream.beginning
        frame = self.stream._snapshot(  # pylint: disable=W0212
            beginning + (timestamp - beginning) * self.node.speed, mask
        )
        frame.time = timestamp
        return frame

    @property
    def duration(self) -> Fraction | float:
        return self.stream.duration / self.node.speed
