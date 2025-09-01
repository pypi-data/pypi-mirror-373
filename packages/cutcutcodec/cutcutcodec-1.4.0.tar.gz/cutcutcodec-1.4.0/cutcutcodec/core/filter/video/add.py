#!/usr/bin/env python3

"""Allow to combine overlapping streams."""

from fractions import Fraction
import typing

import numpy as np
import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.filter.mix.video_cast import to_rgb, to_rgb_alpha


class FilterVideoAdd(Filter):
    """Combine the stream in once by additing the overlapping slices.

    Examples
    --------
    >>> from cutcutcodec.core.filter.video.add import FilterVideoAdd
    >>> from cutcutcodec.core.filter.video.delay import FilterVideoDelay
    >>> from cutcutcodec.core.generation.video.equation import GeneratorVideoEquation
    >>>
    >>> (s_video_0,) = GeneratorVideoEquation("(i+1)/2", "1/2").out_streams
    >>> (s_video_1,) = FilterVideoDelay(
    ...     GeneratorVideoEquation("(j+1)/2", "1/2").out_streams, 10
    ... ).out_streams
    >>> (s_add_video,) = FilterVideoAdd([s_video_0, s_video_1]).out_streams
    >>>
    >>> s_video_0.snapshot(10, (2, 2))
    FrameVideo(10, [[[0. , 0.5],
                     [0. , 0.5]],
    <BLANKLINE>
                    [[1. , 0.5],
                     [1. , 0.5]]])
    >>> s_video_1.snapshot(10, (2, 2))
    FrameVideo(10, [[[0. , 0.5],
                     [1. , 0.5]],
    <BLANKLINE>
                    [[0. , 0.5],
                     [1. , 0.5]]])
    >>> s_add_video.snapshot(10, (2, 2))
    FrameVideo(10, [[[0.        , 0.75      ],
                     [0.33333334, 0.75      ]],
    <BLANKLINE>
                    [[0.6666667 , 0.75      ],
                     [1.        , 0.75      ]]])
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream]):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
            About the overlaping portions, if the stream is an audio stream,
            a simple addition is performed but if the stream is a video stream,
            the frames are combined like a superposition of semi-transparent windows.
        """
        super().__init__(in_streams, in_streams)
        if not self.in_streams:
            return
        super().__init__(self.in_streams, [_StreamVideoAdd(self)])

    def _getstate(self) -> dict:
        return {}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterVideoAdd.__init__(self, in_streams)


class _StreamVideoAdd(StreamVideo):
    """Concatenate and mix the video streams."""

    def __init__(self, node: FilterVideoAdd):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.filter.video.add.FilterVideoAdd
            The node containing the StreamVideo to mix.
        """
        assert isinstance(node, FilterVideoAdd), node.__class__.__name__
        assert node.in_streams, "requires at least 1 video stream to add"
        super().__init__(node)

    @staticmethod
    def _add_2_with_1(ref: torch.Tensor, other: torch.Tensor) -> torch.Tensor:
        """Add a gray frame (``other``) to the gray alpha reference frame (``ref``).

        No verifications are performed for performance reason.
        ``other`` remains unchanged but ``ref`` is changed inplace.

        alpha final = 1
        color final = c_r*a_r + c_o*(1-a_r)

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.filter.video.add import _StreamVideoAdd
        >>> ref = torch.empty(3, 3, 2)  # 3x3 gray alpha
        >>> ref[..., 1] = torch.tensor([0.0, 0.5, 1.0])  # set alpha transparent to blind
        >>> ref[..., 1]
        tensor([[0.0000, 0.5000, 1.0000],
                [0.0000, 0.5000, 1.0000],
                [0.0000, 0.5000, 1.0000]])
        >>> ref[..., 0] = torch.tensor([[0.0], [0.5], [1.0]])  # set different gray scale
        >>> ref[..., 0]
        tensor([[0.0000, 0.0000, 0.0000],
                [0.5000, 0.5000, 0.5000],
                [1.0000, 1.0000, 1.0000]])
        >>> other_black = torch.full((3, 3, 1), 0.0)
        >>> other_gray = torch.full((3, 3, 1), 0.5)
        >>> other_white = torch.full((3, 3, 1), 1.0)
        >>>
        >>> _StreamVideoAdd._add_2_with_1(ref.clone(), other_black)[..., 0]
        tensor([[0.0000, 0.0000, 0.0000],
                [0.0000, 0.2500, 0.5000],
                [0.0000, 0.5000, 1.0000]])
        >>> _StreamVideoAdd._add_2_with_1(ref.clone(), other_gray)[..., 0]
        tensor([[0.5000, 0.2500, 0.0000],
                [0.5000, 0.5000, 0.5000],
                [0.5000, 0.7500, 1.0000]])
        >>> _StreamVideoAdd._add_2_with_1(ref.clone(), other_white)[..., 0]
        tensor([[1.0000, 0.5000, 0.0000],
                [1.0000, 0.7500, 0.5000],
                [1.0000, 1.0000, 1.0000]])
        >>>
        """
        a_r = ref[..., 1]  # a_r
        color = ref[..., 0]  # c_r
        c_o = other[..., 0]  # c_o
        color -= c_o  # c_r - c_o
        color *= a_r  # a_r * (c_r-c_o)
        color += c_o  # a_r * (c_r - c_o) + c_o = c_r*a_r + c_o*(1-a_r)
        color = torch.unsqueeze(color, 2)  # shape (height, width, 1)
        return color

    @staticmethod
    def _add_2_with_2(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """Add a gray alpha frame (``other``) to the gray alpha reference frame (``ref``).

        No verifications are performed for performance reason.
        ``other`` remains unchanged but ``ref`` is changed inplace.
        Returns a pointer of ``ref``.

        alpha final = 1 - (1-a_r)*(1-a_o)
        color final = (c_r*a_r + c_o*a_o*(1-a_r)) / (a_r+a_o-a_r*a_o)

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.filter.video.add import _StreamVideoAdd
        >>> ref = torch.empty(3, 3, 2)  # 3x3 gray alpha
        >>> ref[..., 1] = torch.tensor([0.0, 0.5, 1.0])  # set alpha transparent to blind
        >>> ref[..., 1]  # a_r
        tensor([[0.0000, 0.5000, 1.0000],
                [0.0000, 0.5000, 1.0000],
                [0.0000, 0.5000, 1.0000]])
        >>> ref[..., 0] = torch.tensor([[0.0], [0.5], [1.0]])  # set different gray scale
        >>> ref[..., 0]  # c_r and a_o
        tensor([[0.0000, 0.0000, 0.0000],
                [0.5000, 0.5000, 0.5000],
                [1.0000, 1.0000, 1.0000]])
        >>> other_black = torch.full((3, 3, 2), 0.0)
        >>> other_black[..., 1] = torch.tensor([[0.0], [0.5], [1.0]])  # alpha transparent to blind
        >>> other_gray = torch.full((3, 3, 2), 0.5)
        >>> other_gray[..., 1] = torch.tensor([[0.0], [0.5], [1.0]])
        >>> other_white = torch.full((3, 3, 2), 1.0)
        >>> other_white[..., 1] = torch.tensor([[0.0], [0.5], [1.0]])
        >>>
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_black)[..., 1]  # alpha
        tensor([[0.0000, 0.5000, 1.0000],
                [0.5000, 0.7500, 1.0000],
                [1.0000, 1.0000, 1.0000]])
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_black)[..., 0]  # doctest: +ELLIPSIS
        tensor([[   ..., 0.0000, 0.0000],
                [0.0000, 0.3333, 0.5000],
                [0.0000, 0.5000, 1.0000]])
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_gray)[..., 0]  # doctest: +ELLIPSIS
        tensor([[   ..., 0.0000, 0.0000],
                [0.5000, 0.5000, 0.5000],
                [0.5000, 0.7500, 1.0000]])
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_white)[..., 0]  # doctest: +ELLIPSIS
        tensor([[   ..., 0.0000, 0.0000],
                [1.0000, 0.6667, 0.5000],
                [1.0000, 1.0000, 1.0000]])
        >>>
        """
        a_r = ref[..., 1]  # a_r
        a_o = other[..., 1]  # a_o
        c_r = ref[..., 0]  # c_r
        c_o = other[..., 0]  # c_r

        alpha = a_r * a_o  # a_r*a_o
        alpha = torch.neg(alpha, out=alpha)  # -a_r*a_o
        alpha += a_o  # a_o - a_r*a_o = a_o * (1-a_r)
        color = c_o * alpha  # c_o * a_o * (1-a_r)
        color += c_r * a_r  # (c_r * a_r) + (c_o * a_o * (1-a_r))
        alpha += a_r  # a_r + a_o - a_r*a_o
        color /= alpha  # (c_r*a_r+c_o*a_o*(1-a_r)) / (a_r+a_o-a_r*a_o)

        ref[..., 0] = color
        ref[..., 1] = alpha
        return ref

    @staticmethod
    def _add_2_with_3(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """Pseudo alias to ``cutcutcodec.core.filter.video.add._StreamVideoAdd._add_4_with_3``."""
        return _StreamVideoAdd._add_4_with_3(to_rgb_alpha(ref), other)

    @staticmethod
    def _add_2_with_4(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """Pseudo alias to ``cutcutcodec.core.filter.video.add._StreamVideoAdd._add_4_with_4``."""
        return _StreamVideoAdd._add_4_with_4(to_rgb_alpha(ref), other)

    @staticmethod
    def _add_4_with_1(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """Pseudo alias to ``cutcutcodec.core.filter.video.add._StreamVideoAdd._add_4_with_3``."""
        return _StreamVideoAdd._add_4_with_3(ref, to_rgb(other))

    @staticmethod
    def _add_4_with_2(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """Pseudo alias to ``cutcutcodec.core.filter.video.add._StreamVideoAdd._add_4_with_4``."""
        return _StreamVideoAdd._add_4_with_3(ref, to_rgb(other))

    @staticmethod
    def _add_4_with_3(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """Add a rgb frame to the rgb alpha frame_ref.

        Like ``cutcutcodec.core.filter.video.add._StreamVideoAdd._add_2_with_1`` with 3 channels.
        """
        a_r = ref[..., 3]  # a_r
        a_r = torch.unsqueeze(a_r, 2)
        color = ref[..., :3]  # c_r
        c_o = other[..., :3]  # c_o
        color -= c_o  # c_r - c_o
        color *= a_r  # a_r * (c_r-c_o)
        color += c_o  # a_r * (c_r - c_o) + c_o = c_r*a_r + c_o*(1-a_r)
        return color

    @staticmethod
    def _add_4_with_4(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """Add a rgb alpha frame to the rgb alpha frame_ref.

        Like ``cutcutcodec.core.filter.video.add._StreamVideoAdd._add_2_with_2`` with 4 channels.
        """
        a_r = ref[..., 3]  # a_r
        a_r = torch.unsqueeze(a_r, 2)
        a_o = other[..., 3]  # o_r
        a_o = torch.unsqueeze(a_o, 2)
        c_r = ref[..., :3]  # c_r
        c_o = other[..., :3]  # c_o

        alpha = a_r * a_o  # a_r*a_o
        alpha = torch.neg(alpha, out=alpha)  # -a_r*a_o
        alpha += a_o  # a_o - a_r*a_o = a_o * (1-a_r)
        color = c_o * alpha  # c_o * a_o * (1-a_r)
        color += c_r * a_r  # (c_r * a_r) + (c_o * a_o * (1-a_r))
        alpha += a_r  # a_r + a_o - a_r*a_o
        color /= alpha  # (c_r*a_r+c_o*a_o*(1-a_r)) / (a_r+a_o-a_r*a_o)

        ref[..., :3] = color
        ref[..., 3] = torch.squeeze(alpha, 2)
        return ref

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        # selection of the concerned streams
        if not (
            streams := [
                s for s in self.node.in_streams if s.beginning <= timestamp < s.beginning+s.duration
            ]
        ):
            if timestamp < self.beginning or timestamp >= self.beginning + self.duration:
                raise OutOfTimeRange(
                    f"stream start {self.beginning} and end {self.beginning + self.duration}, "
                    f"no stream at timestamp {timestamp}"
                )
            return FrameVideo(
                timestamp, torch.zeros((*mask.shape, 2), dtype=torch.uint8)
            )

        # general combinaison of the frames
        frame_ref = streams.pop(0)._snapshot(timestamp, mask)  # pylint: disable=W0212
        for stream in streams:
            # verif for avoid useless computing
            if frame_ref.shape[2] in {1, 3}:  # if no alpha channel
                return frame_ref
            if np.ma.allequal(frame_ref.numpy(force=True), 255):
                return frame_ref.convert(frame_ref.shape[2]-1)
            # combination
            other = stream._snapshot(timestamp, mask)  # pylint: disable=W0212
            func_add = getattr(_StreamVideoAdd, f"_add_{frame_ref.shape[2]}_with_{other.shape[2]}")
            frame_ref = func_add(frame_ref, other)
        return frame_ref

    @property
    def beginning(self) -> Fraction:
        return min(s.beginning for s in self.node.in_streams)

    @property
    def colorspace(self) -> Colorspace:
        if len(colorspace := {s.colorspace for s in self.node.in_streams}) != 1:
            raise ValueError(f"ambiguous input colorspace {colorspace}")
        return colorspace.pop()

    @property
    def duration(self) -> Fraction | float:
        end = max(s.beginning + s.duration for s in self.node.in_streams)
        return end - self.beginning
