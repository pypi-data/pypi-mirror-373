#!/usr/bin/env python3

"""Check that the decoding of the audio and video files goes well."""

from fractions import Fraction
import itertools
import math
import random

import pytest
import torch

from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
from cutcutcodec.utils import get_project_root


def test_duration_audio():
    """Ensure the duration is optimized and repetable."""
    audio = get_project_root().parent / "media" / "audio" / "narration_5_1.oga"
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        duration = stream.duration
        assert duration is not None
    # test read all frames once
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        rate = stream.rate
        try:
            stream.snapshot(0, rate, int(2*duration*rate))
        except OutOfTimeRange:
            pass
        assert getattr(stream, "_duration", None) is not None
        assert getattr(stream, "_duration", None) == duration
    # test seek
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        try:
            stream.seek(duration + 3600)
        except OutOfTimeRange:
            pass
        assert getattr(stream, "_duration", None) is not None
        assert getattr(stream, "_duration", None) == duration
    # test duration from scratch
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        assert stream.duration == duration


def test_duration_video():
    """Ensure the duration is optimized and repetable."""
    # test read all frames
    video = get_project_root().parent / "media" / "video" / "intro.webm"
    with ContainerInputFFMPEG(video) as container:
        stream = container.out_select("video")[0]
        shape = (stream.height, stream.width)
        rate = stream.rate
        try:
            for timestamp in itertools.count():
                stream.snapshot(Fraction(timestamp, rate), shape)
        except OutOfTimeRange:
            pass
        assert getattr(stream, "_duration", None) is not None
        duration = getattr(stream, "_duration", None)
    # test seek
    with ContainerInputFFMPEG(video) as container:
        stream = container.out_select("video")[0]
        try:
            stream.seek(duration + 3600)
        except OutOfTimeRange:
            pass
        assert getattr(stream, "_duration", None) is not None
        assert getattr(stream, "_duration", None) == duration
    # test duration from scratch
    with ContainerInputFFMPEG(video) as container:
        stream = container.out_select("video")[0]
        assert stream.duration == duration


def test_linear_reading_audio():
    """Linear reading of the entiere audio file."""
    audio = get_project_root().parent / "media" / "audio" / "narration_5_1.oga"
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        samples = math.floor(stream.duration * stream.rate)
        stream.snapshot(0, stream.rate, samples)
        for i in range(0, samples-512, 512):
            stream.snapshot(Fraction(i, stream.rate), stream.rate, 512)


def test_linear_reading_video():
    """Linear reading of the entire video file."""
    video = get_project_root().parent / "media" / "video" / "intro.webm"
    with ContainerInputFFMPEG(video) as container:
        stream = container.out_select("video")[0]
        shape = (stream.height, stream.width)
        prec_time = stream.snapshot(0, shape).time
        for i in range(1, math.ceil(stream.duration * stream.rate)):
            timestamp = (i-1) / stream.rate
            next_time = stream.snapshot(i/stream.rate, shape).time
            assert prec_time <= timestamp
            assert next_time > timestamp
            assert prec_time <= next_time  # the time of the images must be increasing


def test_out_of_bounds_audio():
    """Make sure that you can't reach outside the duration of the audio."""
    audio = get_project_root().parent / "media" / "audio" / "narration_5_1.oga"
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(-Fraction(1, 100_000), stream.rate, 1)
        stream.snapshot(0, stream.rate, 1)
        stream.snapshot(stream.duration - 2*Fraction(1, stream.rate), stream.rate, 2)
        stream.snapshot(stream.duration - Fraction(1, stream.rate), stream.rate, 1)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(stream.duration - Fraction(1, stream.rate), stream.rate, 2)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(stream.duration, stream.rate, 1)


def test_out_of_bounds_video():
    """Make sure that you can't reach outside the duration of the video."""
    video = get_project_root().parent / "media" / "video" / "intro.webm"
    with ContainerInputFFMPEG(video) as container:
        stream = container.out_select("video")[0]
        shape = (stream.height, stream.width)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(Fraction(-1, 100_000), shape)
        stream.snapshot(0, shape)
        stream.snapshot(stream.duration - Fraction(1, 100_000), shape)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(stream.duration, shape)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(stream.duration + Fraction(1, 100_000), shape)


@pytest.mark.slow
def test_random_reading_video():
    """Random reading of the entire video file."""
    video = get_project_root().parent / "media" / "video" / "intro.webm"
    with ContainerInputFFMPEG(video) as container:
        stream = container.out_select("video")[0]
        shape = (stream.height, stream.width)
        frames = [
            stream.snapshot(i/stream.rate, shape)
            for i in range(math.ceil(stream.duration*stream.rate))
        ]
        random.Random(0).shuffle(frames)
        for frame_ref in frames:
            frame = stream.snapshot(frame_ref.time, shape)
            assert frame.time == frame_ref.time
            assert torch.equal(frame, frame_ref)


def test_random_reading_audio():
    """Random reading of the entire audio file."""
    audio = get_project_root().parent / "media" / "audio" / "narration_5_1.oga"
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        frames = [
            stream.snapshot(Fraction(i, stream.rate), stream.rate, 512)
            for i in range(0, math.ceil(stream.duration * stream.rate)-513, 512)
        ]
        random.Random(0).shuffle(frames)
        for frame_ref in frames:
            frame = stream.snapshot(frame_ref.time, stream.rate, 512)
            assert frame.time == frame_ref.time
            assert torch.equal(frame, frame_ref), (frame_ref, frame)


@pytest.mark.slow
def test_reverse_reading_video():
    """Read all frames in reverse order."""
    video = get_project_root().parent / "media" / "video" / "intro.webm"
    with ContainerInputFFMPEG(video) as container:
        stream = container.out_select("video")[0]
        shape = (stream.height, stream.width)
        frames = [
            stream.snapshot(i/stream.rate, shape)
            for i in range(math.ceil(stream.duration*stream.rate))
        ]
        frames.reverse()
        for frame_ref in frames:
            frame = stream.snapshot(frame_ref.time, shape)
            assert frame.time == frame_ref.time
            assert torch.equal(frame, frame_ref)


def test_reverse_reading_audio():
    """Random reading of the entire audio file."""
    audio = get_project_root().parent / "media" / "audio" / "narration_5_1.oga"
    with ContainerInputFFMPEG(audio) as container:
        (stream,) = container.out_streams
        frames = [
            stream.snapshot(Fraction(i, stream.rate), stream.rate, 512)
            for i in range(0, math.ceil(stream.duration * stream.rate)-513, 512)
        ]
        frames.reverse()
        for frame_ref in frames:
            frame = stream.snapshot(frame_ref.time, stream.rate, 512)
            assert frame.time == frame_ref.time
            assert torch.equal(frame, frame_ref), (frame_ref, frame)
