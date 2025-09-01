#!/usr/bin/env python3

"""Test the bijection of the audio linear cast."""

from fractions import Fraction

import torch

from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.layout import Layout
from cutcutcodec.core.filter.mix.audio_cast import AudioConvertor


def test_bijection():
    """Ensure that the conversion of A to B to A with B higher is identity."""
    for p_in, p_out in AudioConvertor.all_layouts():
        if len(Layout(p_in)) <= len(Layout(p_out)):
            conv_1 = AudioConvertor(p_in, p_out)
            conv_2 = AudioConvertor(p_out, p_in)
            for var, equation in conv_2.equations.items():
                assert 1.0*var == 1.0*equation.subs(conv_1.equations).simplify()
            frame = FrameAudio(0, 1, p_in, torch.randn((len(Layout(p_in)), 1024)))
            assert torch.equal(frame, conv_2(conv_1(frame))), (p_in, p_out)


def test_conserve_meta():
    """Ensure that the metadatas are conserved."""
    converter = AudioConvertor("stereo", "mono")
    assert converter(FrameAudio(0, 1, "stereo", torch.empty(2, 128))).time == 0
    assert converter(FrameAudio("1/2", 1, "stereo", torch.empty(2, 128))).time == Fraction(1, 2)
    assert converter(FrameAudio(1, 1, "stereo", torch.empty(2, 128))).time == 1
    assert converter(FrameAudio(0, 1, "stereo", torch.empty(2, 128))).rate == 1
    assert converter(FrameAudio(0, 48000, "stereo", torch.empty(2, 128))).rate == 48000
    assert converter(FrameAudio(0, 1, "stereo", torch.empty(2, 128))).samples == 128
    assert converter(FrameAudio(0, 1, "stereo", torch.empty(2, 256))).samples == 256
