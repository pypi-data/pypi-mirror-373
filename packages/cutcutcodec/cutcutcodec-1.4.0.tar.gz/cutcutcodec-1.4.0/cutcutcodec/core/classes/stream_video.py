#!/usr/bin/env python3

"""Defines the structure of an abstract video stream."""

from fractions import Fraction
import abc
import math
import numbers

import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.classes.stream import Stream, StreamWrapper


class StreamVideo(Stream):
    """Representation of any video stream.

    Attributes
    ----------
    colorspace : Colorspace
        The color space in which the stream is defined (readonly).
    """

    def __init__(self, node):
        super().__init__(node)
        self._mask = None  # for cache speedup

    def _from_masked_items(self, flat_frame: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Return a new frame with the initialised values at the position given by the mask.

        A copy is made only if needed.
        It is the complementary method of
        ``cutcutcodec.core.classes.stream_video.StreamVideo._to_masked_items``.
        """
        if mask is self._mask:
            return torch.reshape(flat_frame, (*mask.shape, 1))
        frame = torch.empty(*mask.shape, dtype=flat_frame.dtype, device=flat_frame.device)
        frame[mask] = flat_frame
        frame = torch.unsqueeze(frame, 2)
        return frame

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        """Abstract help for ``snapshot``.

        Parameters
        ----------
        timestamp : fractions.Fraction
            The absolute time expressed in seconds
        mask : torch.Tensor[boolean]
            The 2d boolean matrix of the interested pixels.

        Returns
        -------
        torch.Tensor[torch.float32]
            A floting point matrix of pixel between 0 and 1.
        """
        raise NotImplementedError

    def _to_masked_items(self, frame: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Return a contiguous flattened tensor equivalent to `frame[mask]`.

        A copy is made only if needed.
        It is the complementary method of
        ``cutcutcodec.core.classes.stream_video.StreamVideo._from_masked_items``.
        """
        if mask is self._mask:
            return torch.ravel(frame)
        return torch.ravel(torch.masked_select(frame, mask).contiguous())

    @property
    @abc.abstractmethod
    def colorspace(self) -> Colorspace:
        """Return the color space in which the stream is defined."""
        raise NotImplementedError

    def snapshot(
        self,
        timestamp: numbers.Real,
        shape: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
        *, channels=None
    ) -> FrameVideo:
        """Extract the closest frame to the requested date.

        Parameters
        ----------
        timestamp : numbers.Real
            The absolute time expressed in seconds, not relative to the beginning of the video.
            For avoid the inacuracies of round, it is recomended to use fractional number.
        shape : tuple[int, int] or list[int, int]
            The pixel dimensions of the returned frame.
            The convention adopted is the numpy convention (height, width).
        channels : int, optional
            Impose the numbers of channels, apply conversion if nescessary.
            For the interpretation of the layers,
            see ``cutcutcodec.core.classes.frame_video.FrameVideo``.

        Returns
        -------
        frame : cutcutcodec.core.classes.frame_video.FrameVideo
            Video frame with metadata.

        Raises
        ------
        cutcutcodec.core.exception.OutOfTimeRange
            If we try to get a frame out of the definition range.
            The valid range is [self.beginning, self.beginning+self.duration[.
        """
        assert isinstance(timestamp, numbers.Real), timestamp.__class__.__name__
        assert isinstance(shape, (tuple, list)), shape.__class__.__name__
        assert len(shape) == 2, len(shape)
        assert all(isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape
        shape = (int(shape[0]), int(shape[1]))
        if math.isnan(timestamp):  # default transparent video frame
            frame = FrameVideo(0, torch.zeros((*shape, 2)))
        else:
            if self._mask is None or self._mask.shape != shape:
                self._mask = torch.full(shape, True, dtype=bool)
            frame = self._snapshot(Fraction(timestamp), self._mask)
            frame = FrameVideo(timestamp, frame)
        if channels is not None:
            frame = frame.convert(channels)
        return frame

    @property
    def type(self) -> str:
        """Implement ``cutcutcodec.core.classes.stream.Stream.type``."""
        return "video"


class StreamVideoWrapper(StreamWrapper, StreamVideo):
    """Allow to dynamically transfer the methods of an instanced video stream.

    This can be very useful for implementing filters.

    Attribute
    ---------
    stream : cutcutcodec.core.classes.stream_video.StreamVideo
        The video stream containing the properties to be transfered (readonly).
        This stream is one of the input streams of the parent node.
    """

    def __init__(self, node: Filter, index: numbers.Integral):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.classes.filter.Filter
            The parent node, transmitted to ``cutcutcodec.core.classes.stream.Stream``.
        index : number.Integral
            The index of the video stream among all the input streams of the ``node``.
            0 for the first, 1 for the second ...
        """
        assert isinstance(node, Filter), node.__class__.__name__
        assert len(node.in_streams) > index, f"only {len(node.in_streams)} streams, no {index}"
        assert isinstance(node.in_streams[index], StreamVideo), "the stream must be video type"
        super().__init__(node, index)

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        return self.stream._snapshot(timestamp, mask)  # pylint: disable=W0212

    @property
    def colorspace(self) -> Colorspace:
        """Return the color space in which the stream is defined."""
        return self.stream.colorspace
