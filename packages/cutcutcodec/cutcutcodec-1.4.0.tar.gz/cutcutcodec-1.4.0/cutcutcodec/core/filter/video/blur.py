#!/usr/bin/env python3

"""Allow to blur a video stream."""

from fractions import Fraction
import numbers
import typing

import cv2
import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideoWrapper


class FilterVideoBlur(Filter):
    """Blur a video stream.

    Attributes
    ----------
    radius : Fraction
        The relative kernel radius (readonly).

    Examples
    --------
    >>> from cutcutcodec.core.filter.video.blur import FilterVideoBlur
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> (s_blur_video,) = FilterVideoBlur([s_base_video], 0.5).out_streams
    >>>
    >>> s_base_video.snapshot(0, (100, 100)).std() > s_blur_video.snapshot(0, (100, 100)).std()
    tensor(True)
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream], radius: numbers.Real):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        radius : numbers.Real
            The relative kernel radius ]0, 1], the smallest image shape is [-1, 1].
        """
        assert isinstance(radius, numbers.Real), radius.__class__.__name__
        assert 0 < radius <= 1, radius
        self._radius = Fraction(radius)
        super().__init__(in_streams, in_streams)
        super().__init__(
            in_streams, [_StreamVideoBlur(self, index) for index in range(len(in_streams))]
        )

    def _getstate(self) -> dict:
        return {"radius": str(self._radius)}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"radius"}, set(state)
        FilterVideoBlur.__init__(self, in_streams, Fraction(state["radius"]))

    @property
    def radius(self) -> Fraction:
        """Return relative kernel radius."""
        return self._radius


class _StreamVideoBlur(StreamVideoWrapper):
    """Apply gaussian blur to a video stream."""

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        frame = self.stream._snapshot(timestamp, mask)  # pylint: disable=W0212
        frame_input = frame.movedim(2, 0)[:, None, :, :]  # (batch, 1, h, w)
        diameter = 2 * round(self.node.radius * float(min(mask.shape))) + 1  # odd number
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (diameter, diameter))
        kernel = torch.asarray(kernel).to(dtype=frame.dtype, device=frame.device)[None, None, :, :]
        kernel /= kernel.sum()  # [batch, 1, 2*r+1, 2*r+1]
        frame_output = torch.conv2d(frame_input, kernel, padding="same")
        frame = frame_output[:, 0, :, :].movedim(0, 2)
        return frame
