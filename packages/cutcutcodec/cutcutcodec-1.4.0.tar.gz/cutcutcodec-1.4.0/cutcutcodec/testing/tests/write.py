#!/usr/bin/env python3

"""Check that the encoding of the multimedia files goes well."""

from fractions import Fraction
import pathlib
import tempfile
import uuid

import pytest

from cutcutcodec.core.exceptions import MissingStreamError
from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
from cutcutcodec.core.filter.video.subclip import FilterVideoSubclip
from cutcutcodec.core.generation.audio.empty import GeneratorAudioEmpty
from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
from cutcutcodec.core.generation.video.empty import GeneratorVideoEmpty
from cutcutcodec.core.generation.video.equation import GeneratorVideoEquation
from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
from cutcutcodec.core.io.scheduler import scheduler
from cutcutcodec.core.io.write_ffmpeg import ContainerOutputFFMPEG


def test_detect_empty_audio():
    """Ensures that empty stream detection works."""
    (stream_empty,) = GeneratorAudioEmpty().out_streams
    with pytest.raises(MissingStreamError):
        list(scheduler([stream_empty], [Fraction(1)]))


def test_detect_empty_video():
    """Ensures that empty stream detection works."""
    (stream_empty,) = GeneratorVideoEmpty().out_streams
    with pytest.raises(MissingStreamError):
        list(scheduler([stream_empty], [Fraction(1)], shape=(1, 1)))


def test_transcode_audio_alone():
    """Writes a file with only one audio stream."""
    streams_settings = [{"encodec": "libopus", "rate": 8000}]
    filename = pathlib.Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.ogg"
    (audio_stream,) = FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 0, 1).out_streams
    ContainerOutputFFMPEG([audio_stream], filename, streams_settings=streams_settings).write()
    filename.unlink()


def test_transcode_multi_streams():
    """Writes a file with multiple video and audio streams."""
    filename = pathlib.Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.mkv"
    container_a = FilterAudioSubclip(
        (GeneratorAudioNoise(0).out_streams + GeneratorAudioNoise(0).out_streams), 0, 1
    )
    container_v = FilterVideoSubclip(
        (GeneratorVideoNoise(0).out_streams + GeneratorVideoNoise(0).out_streams), 0, 1
    )
    streams = container_a.out_streams + container_v.out_streams
    settings = [
        {"encodec": "libopus", "rate": 8000},
        {"encodec": "libopus", "rate": 8000},
        {"encodec": "libx264", "rate": 12, "shape": (2, 2)},
        {"encodec": "libx264", "rate": 12, "shape": (2, 2)}
    ]
    ContainerOutputFFMPEG(streams, filename, streams_settings=settings).write()
    filename.unlink()


def test_transcode_video_alone():
    """Writes a file with only one video stream."""
    streams_settings = [{"encodec": "libx264", "rate": 12, "shape": (2, 2)}]
    filename = pathlib.Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.mkv"
    (video_stream,) = FilterVideoSubclip(GeneratorVideoNoise(0).out_streams, 0, 1).out_streams
    ContainerOutputFFMPEG([video_stream], filename, streams_settings=streams_settings).write()
    filename.unlink()


def test_video_scheduler():
    """Check that in case of a tie, the left frame is given away before the right one."""
    (stream_inf,) = GeneratorVideoEquation(0).out_streams
    fps = Fraction(10)
    (stream,) = FilterVideoSubclip([stream_inf], 0, Fraction(1, 2)).out_streams

    # single input
    inds = [ind for ind, _ in scheduler([stream], [fps], shape=(1, 1))]
    assert inds == [0]*5  # 500 ms & 10 fps => 5 frames
    # 2 synchronous inputs
    inds = [ind for ind, _ in scheduler([stream, stream], [fps, fps], shape=(1, 1))]
    assert inds == [0, 1]*5
    # 3 synchronous inputs
    inds = [ind for ind, _ in scheduler([stream, stream, stream], [fps, fps, fps], shape=(1, 1))]
    assert inds == [0, 1, 2]*5
    # 2 inputs, the first twice as fast as the seconde
    inds = [ind for ind, _ in scheduler([stream, stream], [2*fps, fps], shape=(1, 1))]
    assert inds == [0, 1, 0]*5
    # 2 inputs, the second twice as fast as the first
    inds = [ind for ind, _ in scheduler([stream, stream], [fps, 2*fps], shape=(1, 1))]
    assert inds == [0, 1, 1]*5
