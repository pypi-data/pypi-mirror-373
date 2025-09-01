#!/usr/bin/env python3

"""Check that padding is correct."""

from fractions import Fraction

import torch

from cutcutcodec.core.generation.audio.equation import GeneratorAudioEquation
from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip


def test_pad_stream_audio():
    """Test all possible padding scenarios for an audio stream."""
    # pad if start sample in ]-oo, 0[ U [2-sr, +oo[
    (stream,) = FilterAudioSubclip(GeneratorAudioEquation(1).out_streams, 0, 2).out_streams

    # case the entire frame is before the start of the stream
    assert torch.equal(  # far ahead
        stream.snapshot(-3, 1, 2, pad=True), torch.tensor([[0.0, 0.0]])
    )
    assert torch.equal(  # far ahead (end of sample in open interval)
        stream.snapshot(-2, 1, 2, pad=True), torch.tensor([[0.0, 0.0]])
    )
    assert torch.equal(  # close ahead
        stream.snapshot(-1 - Fraction(1, 1000), 1, 2, pad=True), torch.tensor([[0.0, 0.0]])
    )
    # case the entire frame is after the start of the stream
    assert torch.equal(  # far behind
        stream.snapshot(3, 1, 2, pad=True), torch.tensor([[0.0, 0.0]])
    )
    assert torch.equal(  # close behind
        stream.snapshot(1 + Fraction(1, 1000), 1, 2, pad=True), torch.tensor([[0.0, 0.0]])
    )
    assert torch.equal(  # very close behind, 1 in [0, 2[
        stream.snapshot(1, 1, 2, pad=True), torch.tensor([[0.0, 0.0]])
    )
    # case straddling the start
    assert torch.equal(stream.snapshot(-1, 1, 2, pad=True), torch.tensor([[0.0, 1.0]]))
    assert torch.equal(
        stream.snapshot(-1 + Fraction(1, 1000), 1, 2, pad=True), torch.tensor([[0.0, 1.0]])
    )
    # case straddling the start
    assert torch.equal(
        stream.snapshot(1 - Fraction(1, 1000), 1, 2, pad=True), torch.tensor([[1.0, 0.0]])
    )
    # case fully included (optional pad argument)
    assert torch.equal(stream.snapshot(0, 2, 3, pad=True), torch.tensor([[1.0, 1.0, 1.0]]))
    # case protrudes on both sides
    assert torch.equal(stream.snapshot(-1, 1, 3, pad=True), torch.tensor([[0.0, 1.0, 0.0]]))
