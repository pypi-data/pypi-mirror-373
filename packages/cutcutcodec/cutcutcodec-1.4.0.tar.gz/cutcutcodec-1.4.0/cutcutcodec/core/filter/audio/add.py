#!/usr/bin/env python3

"""Allow to combine overlapping streams."""

from fractions import Fraction
import math
import typing

import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.layout import Layout
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.exceptions import OutOfTimeRange


class FilterAudioAdd(Filter):
    """Combine the stream in once by additing the overlapping slices.

    Examples
    --------
    >>> from cutcutcodec.core.filter.audio.add import FilterAudioAdd
    >>> from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>>
    >>> (s_audio_0,) = GeneratorAudioNoise(0).out_streams
    >>> (s_audio_1,) = FilterAudioDelay(GeneratorAudioNoise(.5).out_streams, 10).out_streams
    >>> (s_add_audio,) = FilterAudioAdd([s_audio_0, s_audio_1]).out_streams
    >>>
    >>> s_audio_0.snapshot(8, 1, 5)
    FrameAudio(8, 1, 'stereo', [[-0.6345538 ,  0.4154123 , -0.7169694 ,
                                  0.78363144,  0.61358166],
                                [-0.5202795 , -0.46771908,  0.16872191,
                                  0.01911473,  0.62246954]])
    >>> s_audio_1.snapshot(10, 1, 3)
    FrameAudio(10, 1, 'stereo', [[-0.15122247, -0.22395265,  0.25110817],
                                 [-0.6546018 , -0.37251115,  0.3317027 ]])
    >>> s_add_audio.snapshot(8, 1, 5)
    FrameAudio(8, 1, 'stereo', [[-0.6345538 ,  0.4154123 , -0.86819184,
                                  0.5596788 ,  0.8646898 ],
                                [-0.5202795 , -0.46771908, -0.4858799 ,
                                 -0.35339642,  0.95417225]])
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
        super().__init__(self.in_streams, [_StreamAudioAdd(self)])

    def _getstate(self) -> dict:
        return {}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterAudioAdd.__init__(self, in_streams)


class _StreamAudioAdd(StreamAudio):
    """Concatenate and add the audio streams."""

    def __init__(self, node: FilterAudioAdd):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.filter.audio.add.FilterAudioAdd
            The node containing the StreamAudio to add.
        """
        assert isinstance(node, FilterAudioAdd), node.__class__.__name__
        assert node.in_streams, "requires at least 1 audio stream to add"
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        # selection of the concerned streams
        end = timestamp + Fraction(samples, rate)  # apparition of last sample
        if timestamp < self.beginning or end > self.beginning + self.duration:
            raise OutOfTimeRange(
                f"stream start {self.beginning} and end {self.beginning + self.duration}, "
                f"no stream at timestamp {timestamp} to {timestamp} + {samples}/{rate}"
            )
        streams = [
            s for s in self.node.in_streams
            if end > s.beginning and timestamp < s.beginning + s.duration
        ]

        # slices selection
        slices = [
            (
                max(s.beginning, timestamp),
                min(s.beginning+s.duration, end)
            )
            for s in streams
        ]
        slices = [(start, math.floor(rate*(end_-start))) for start, end_ in slices]
        slices = [
            (stream, start, samples)
            for stream, (start, samples) in zip(streams, slices)
            if samples > 0
        ]

        # frames portion recuperations
        frames = [
            stream._snapshot(start, rate, samples)  # pylint: disable=W0212
            for stream, start, samples in slices
        ]
        if len(layout := {frame.layout for frame in frames}) > 1:
            raise RuntimeError(
                f"impossible to combine frames of different layouts {layout} "
                f"at timestamp {timestamp} to {timestamp} + {samples}/{rate}"
            )
        layout = layout.pop() if layout else 1

        # create the new empty audio frame
        dtypes = {frame.dtype for frame in frames}
        dtypes = sorted(
            dtypes, key=lambda t: {torch.float16: 2, torch.float32: 1, torch.float64: 0}[t]
        ) + [torch.float32]  # if slice = []
        frame = FrameAudio(
            timestamp,
            rate,
            layout,
            torch.full((len(layout), samples), torch.nan, dtype=dtypes[0]),
        )

        # frames addition
        for frame_ in frames:
            start = math.floor(rate * (frame_.time-timestamp))
            part = frame[:, start:start+frame_.samples]
            part = torch.where(torch.isnan(part), frame_, part+frame_)
            frame[:, start:start+frame_.samples] = part
        return frame

    @property
    def beginning(self) -> Fraction:
        return min(s.beginning for s in self.node.in_streams)

    @property
    def duration(self) -> Fraction | float:
        end = max(s.beginning + s.duration for s in self.node.in_streams)
        return end - self.beginning

    @property
    def layout(self) -> Layout:
        if len(layouts := {s.layout for s in self.node.in_streams}) != 1:
            raise AttributeError(f"add audio streams only implemented for same layout {layouts}")
        return layouts.pop()
