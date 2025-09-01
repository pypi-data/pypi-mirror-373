#!/usr/bin/env python3

"""Exhaustively test all possible combinations."""

import pytest

from cutcutcodec.core.compilation.export.compatibility import Compatibilities
from cutcutcodec.core.classes.encoder import AllEncoders
from cutcutcodec.core.classes.muxer import AllMuxers


@pytest.mark.slow
def test_audio_compatibilities():
    """Look for all muxers compatible with all audio encoders."""
    encoders = sorted(AllEncoders().audio)
    muxers = sorted(AllMuxers().set)
    comp = Compatibilities().check(encoders, muxers)
    assert (comp != "").any()


@pytest.mark.slow
def test_video_compatibilities():
    """Look for all muxers compatible with all video encoders."""
    encoders = sorted(AllEncoders().video)
    muxers = sorted(AllMuxers().set)
    comp = Compatibilities().check(encoders, muxers)
    assert (comp != "").any()
