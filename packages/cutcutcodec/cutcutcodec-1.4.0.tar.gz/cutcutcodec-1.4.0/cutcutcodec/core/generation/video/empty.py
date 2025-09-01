#!/usr/bin/env python3

"""Dedicated to tests, it is an empty video stream containing no frames."""

from fractions import Fraction
import typing

import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.container import ContainerInput
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.exceptions import OutOfTimeRange


class GeneratorVideoEmpty(ContainerInput):
    """Contains an empty video stream.

    Examples
    --------
    >>> from cutcutcodec.core.exceptions import OutOfTimeRange
    >>> from cutcutcodec.core.generation.video.empty import GeneratorVideoEmpty
    >>> (stream,) = GeneratorVideoEmpty().out_streams
    >>> try:
    ...     stream.snapshot(0, (1, 1))
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    this stream does not contain any frames
    >>>
    """

    def __init__(self):
        out_streams = [_StreamVideoEmpty(self)]
        super().__init__(out_streams)

    def _getstate(self) -> dict:
        return {}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}, state
        GeneratorVideoEmpty.__init__(self)


class _StreamVideoEmpty(StreamVideo):
    """A video stream containing no frames."""

    colorspace = Colorspace.from_default_working()

    def __init__(self, node: GeneratorVideoEmpty):
        assert isinstance(node, GeneratorVideoEmpty), node.__class__.__name__
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        raise OutOfTimeRange("this stream does not contain any frames")

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> Fraction | float:
        return Fraction(0)
