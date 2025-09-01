#!/usr/bin/env python3

"""Check is the properties are working for all codecs."""

import pytest

from cutcutcodec.core.classes.encoder import AllEncoders, Encoder


@pytest.mark.slow
def test_doc():
    """Try to extract the doc for all codecs."""
    for encoder_name in AllEncoders().set:
        doc = Encoder(encoder_name).doc
        assert isinstance(doc, str), \
            f"bad type {doc.__class__.__name__} for the doc of {encoder_name}"
        assert doc != "", f"the doc of {encoder_name} is empty"


def test_parse():
    """Ensure all encoders can be parsed."""
    for encoder in AllEncoders().set:
        Encoder(encoder)
