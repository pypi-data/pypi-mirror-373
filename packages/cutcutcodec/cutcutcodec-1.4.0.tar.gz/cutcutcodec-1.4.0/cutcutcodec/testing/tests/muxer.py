#!/usr/bin/env python3

"""Check is the properties are working for all muxers."""

import pytest

from cutcutcodec.core.classes.muxer import AllMuxers, Muxer


@pytest.mark.slow
def test_doc():
    """Try to extract the doc for all muxers."""
    for muxer in AllMuxers().set:
        doc = Muxer(muxer).doc
        assert isinstance(doc, str), f"bad type {doc.__class__.__name__} for the doc of {muxer}"
        assert doc != "", f"the doc of {muxer} is empty"


def test_parse():
    """Ensure all muxers can be parsed."""
    for muxer in AllMuxers().set:
        Muxer(muxer)
