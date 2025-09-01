#!/usr/bin/env python3

"""Apply any user defined filter to video frames."""

from fractions import Fraction
import typing

import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideoWrapper


class FilterVideoCustom(Filter):
    '''Apply any user defined filter to video frames.

    Examples
    --------
    >>> from fractions import Fraction
    >>> import torch
    >>> from cutcutcodec.core.filter.video.custom import FilterVideoCustom
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> def func(frame: torch.Tensor, timestamp: Fraction) -> torch.Tensor:
    ...     """Create a black border during the first 10 seconds."""
    ...     if timestamp <= 10:
    ...         frame[:2, :] = frame[-2:, :] = frame[:, :2] = frame[:, -2:] = 0
    ...     return frame
    ...
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> (s_custom_video,) = FilterVideoCustom([s_base_video], func).out_streams
    >>>
    >>> s_custom_video.snapshot(0, (9, 9))[:, :, 0]
    tensor([[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.3209, 0.7038, 0.6147, 0.6749, 0.5931, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.6637, 0.7421, 0.7787, 0.8397, 0.5273, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0467, 0.0464, 0.3364, 0.7802, 0.2447, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.4455, 0.7455, 0.3952, 0.1906, 0.1819, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.9956, 0.1559, 0.8482, 0.7545, 0.7674, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])
    >>>
    '''

    def __init__(
        self,
        in_streams: typing.Iterable[Stream],
        func: typing.Callable[[torch.Tensor, Fraction], torch.Tensor],
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        func : callable
            A user-defined function that takes in input the video frame,
            and the frame time as a rational number
            and returns the new frame.
        """
        assert callable(func), func.__class__.__name__
        self.func = func
        super().__init__(in_streams, in_streams)
        super().__init__(
            in_streams, [_StreamVideoCustom(self, index) for index in range(len(in_streams))]
        )

    def _getstate(self) -> dict:
        return {"func": str(self.func)}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"func"}, set(state)
        FilterVideoCustom.__init__(self, in_streams, state["func"])


class _StreamVideoCustom(StreamVideoWrapper):
    """Apply gaussian blur to a video stream."""

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        frame = self.stream._snapshot(timestamp, mask)  # pylint: disable=W0212
        height, width = frame.shape[:2]
        frame = self.node.func(frame, timestamp)
        if not isinstance(frame, torch.Tensor):
            raise TypeError(f"the function {self.node.func} has not returned a video frame {frame}")
        if frame.shape[:2] != (height, width):
            raise TypeError(f"the {self.node.func} function must not modify frame shape")
        return frame
