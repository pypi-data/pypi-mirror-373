#!/usr/bin/env python3

"""Check the consistency between the number of incoming and outgoing streams."""

import pytest

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.generation.audio.empty import GeneratorAudioEmpty


def test_raise_semi_empty():
    """Ensures that a filter cannot be half empty."""
    class _Filter(Filter):
        _getstate = None
        _setstate = None
        default = None

    stream = GeneratorAudioEmpty().out_streams[0]
    _Filter([], [])
    with pytest.raises(AssertionError):
        _Filter([stream], [])
    with pytest.raises(AssertionError):
        _Filter([], [stream])
    _Filter([stream], [stream])
    _Filter([stream], [stream, stream])
    _Filter([stream, stream], [stream])
    _Filter([stream, stream], [stream, stream])
