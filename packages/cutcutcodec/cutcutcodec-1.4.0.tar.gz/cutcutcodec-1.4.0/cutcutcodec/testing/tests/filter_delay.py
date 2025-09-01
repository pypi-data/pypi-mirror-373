#!/usr/bin/env python3

"""Perform tests on ``FilterAudioDelay`` and ``FilterVideoDelay``."""

from fractions import Fraction

import pytest

from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
from cutcutcodec.core.filter.video.delay import FilterVideoDelay
from cutcutcodec.core.filter.video.subclip import FilterVideoSubclip
from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise


def test_limits_audio():
    """Ensures that the limits move in the right direction by the right amount."""
    container = FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 0, 1)
    for delay in (0, 1):
        stream = FilterAudioDelay(container.out_streams, delay).out_streams[0]
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(delay - Fraction(1, 100_000), 1, 1)
        stream.snapshot(delay, 1, 1)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(delay + 1, 1, 1)
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(delay + 1 + Fraction(1, 100_000), 1, 1)


def test_limits_video():
    """Ensures that the limits move in the right direction by the right amount."""
    container = FilterVideoSubclip(GeneratorVideoNoise(0).out_streams, 0, 1)
    for delay in (0, 1):
        stream = FilterVideoDelay(container.out_streams, delay).out_streams[0]
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(delay - Fraction(1, 100_000), (1, 1))
        stream.snapshot(delay, (1, 1))
        stream.snapshot(delay + 1 - Fraction(1, 100_000), (1, 1))
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(delay + 1, (1, 1))
        with pytest.raises(OutOfTimeRange):
            stream.snapshot(delay + 1 + Fraction(1, 100_000), (1, 1))


def test_concat_audio():
    """Ensure that the concatenation of the stream is coherent."""
    container = FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 0, 1)
    stream = FilterAudioDelay(
        FilterAudioDelay(container.out_streams, 1).out_streams, 2
    ).out_streams[0]
    with pytest.raises(OutOfTimeRange):
        stream.snapshot(3 - Fraction(1, 100_000), 1, 1)
    stream.snapshot(3, 1, 1)
    with pytest.raises(OutOfTimeRange):
        stream.snapshot(4, 1, 1)


def test_concat_video():
    """Ensure that the concatenation of the stream is coherent."""
    container = FilterVideoSubclip(GeneratorVideoNoise(0).out_streams, 0, 1)
    stream = FilterVideoDelay(
        FilterVideoDelay(container.out_streams, 1).out_streams, 2
    ).out_streams[0]
    with pytest.raises(OutOfTimeRange):
        stream.snapshot(3 - Fraction(1, 100_000), (1, 1))
    stream.snapshot(3, (1, 1))
    stream.snapshot(4 - Fraction(1, 100_000), (1, 1))
    with pytest.raises(OutOfTimeRange):
        stream.snapshot(4, (1, 1))
