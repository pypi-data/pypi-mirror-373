#!/usr/bin/env python3

"""Perform advanced on ``FilterAudioCut`` and ``FilterVideoCut``."""

from fractions import Fraction
import math

import pytest

from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.filter.audio.cut import FilterAudioCut
from cutcutcodec.core.filter.video.cut import FilterVideoCut
from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise


def _chec_audio(stream, beginning, duration):
    assert stream.type == "audio"
    assert stream.beginning == beginning
    assert stream.duration == duration
    if beginning:
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(0, 1, 1)
    if duration == math.inf:
        stream.snapshot(beginning, 1, 1)
    else:
        rate = math.ceil(Fraction(3, duration))
        stream.snapshot(beginning, rate, 3)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(beginning+duration, 1, 1)


def _chec_video(stream, beginning, duration):
    assert stream.type == "video"
    assert stream.beginning == beginning
    assert stream.duration == duration
    if beginning:
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(0, (1, 1))
    stream.snapshot(beginning, (1, 1))
    if duration != math.inf:
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(beginning+duration, (1, 1))


def test_cut_n_audio():
    """Cuts several audio streams in severals points."""
    bounds = [0, 1, 2, math.inf]
    (stream_a,) = GeneratorAudioNoise(0).out_streams
    (stream_b,) = GeneratorAudioNoise(0).out_streams
    for i, stream in enumerate(FilterAudioCut([stream_a, stream_b], *bounds[1:-1]).out_streams):
        bound_index = i//2
        beginning, end = bounds[bound_index], bounds[bound_index+1]
        _chec_audio(stream, beginning, end-beginning)


def test_cut_n_video():
    """Cuts several video streams in severals points."""
    bounds = [0, 1, 2, math.inf]
    (stream_a,) = GeneratorVideoNoise(0).out_streams
    (stream_b,) = GeneratorVideoNoise(0).out_streams
    for i, stream in enumerate(FilterVideoCut([stream_a, stream_b], *bounds[1:-1]).out_streams):
        bound_index = i//2
        beginning, end = bounds[bound_index], bounds[bound_index+1]
        _chec_video(stream, beginning, end-beginning)


def test_cut_one_audio():
    """Cuts only the end of an audio stream."""
    (s_base_audio,) = GeneratorAudioNoise(0).out_streams
    cut_streams = FilterAudioCut([s_base_audio], 10).out_streams
    assert len(cut_streams) == 2
    (cut_stream_low, cut_stream_high) = cut_streams
    _chec_audio(cut_stream_low, 0, 10)
    _chec_audio(cut_stream_high, 10, math.inf)


def test_cut_one_video():
    """Does not cut a video streams."""
    (s_base_video,) = GeneratorVideoNoise(0).out_streams
    cut_streams = FilterVideoCut([s_base_video], 10).out_streams
    assert len(cut_streams) == 2
    (cut_stream_low, cut_stream_high) = cut_streams
    _chec_video(cut_stream_low, 0, 10)
    _chec_video(cut_stream_high, 10, math.inf)


def test_no_cut_audio():
    """Does not cut audio streams."""
    (s_base_audio,) = GeneratorAudioNoise(0).out_streams
    cut_streams = FilterAudioCut([s_base_audio]).out_streams
    assert len(cut_streams) == 1
    (cut_stream,) = cut_streams
    assert cut_stream.beginning == 0
    assert cut_stream.duration == math.inf
    cut_stream.snapshot(0, 1, 1)  # [0, 1[


def test_no_cut_video():
    """Does not cut a video streams."""
    (s_base_video,) = GeneratorVideoNoise(0).out_streams
    cut_streams = FilterVideoCut([s_base_video]).out_streams
    assert len(cut_streams) == 1
    (cut_stream,) = cut_streams
    assert cut_stream.beginning == 0
    assert cut_stream.duration == math.inf
    cut_stream.snapshot(0, (1, 1))
