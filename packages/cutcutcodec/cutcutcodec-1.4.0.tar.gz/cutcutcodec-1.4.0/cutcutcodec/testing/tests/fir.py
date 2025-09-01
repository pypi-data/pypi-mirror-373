#!/usr/bin/env python3

"""Check the Finite Impulse Response Filter."""


from fractions import Fraction

import pytest
import torch

from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.filter.audio.cut import FilterAudioCut
from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
from cutcutcodec.core.filter.audio.fir import FilterAudioFIR
from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise


def delay(size: int):
    """Convolution with a dirac translated of size sample, zero padding left."""
    stream_in, _ = FilterAudioCut(GeneratorAudioNoise(0).out_streams, 1).out_streams
    (stream_out,) = FilterAudioFIR([stream_in], torch.tensor([0.0]*size + [1.0]), 48000).out_streams
    (stream_out_exp,) = FilterAudioDelay([stream_in], Fraction(size, 48000)).out_streams

    # test values
    assert (
        stream_out_exp.snapshot(Fraction(1, 2) + Fraction(size, 48000), 48000, 64)
        == pytest.approx(
            stream_out.snapshot(Fraction(1, 2) + Fraction(size, 48000), 48000, 64),
            rel=1e-6,
            abs=1e-6,
        )
    )
    assert (abs(stream_out.snapshot(0, 48000, size)) <= 1e-6).all()  # zero padding left

    # test time limits
    assert stream_out.beginning == 0
    assert stream_out.duration == 1 + Fraction(size, 48000)
    stream_out.snapshot(0, 48000, 1)
    stream_out.snapshot(1 + Fraction(size-1, 48000), 48000, 1)
    with pytest.raises(OutOfTimeRange):
        stream_out.snapshot(1 + Fraction(size, 48000), 48000, 1)


def identity_queue(size: int):
    """Check the identity impulsional response with zero padding right."""
    stream_in, _ = FilterAudioCut(GeneratorAudioNoise(0).out_streams, 1).out_streams
    (stream_out,) = FilterAudioFIR([stream_in], torch.tensor([1.0] + [0.0]*size), 48000).out_streams

    # test values
    assert (
        stream_in.snapshot(Fraction(1, 2), 48000, 64)
        == pytest.approx(stream_out.snapshot(Fraction(1, 2), 48000, 64), rel=1e-6, abs=1e-6)
    )

    # test time limits
    assert stream_out.beginning == 0
    assert stream_out.duration == 1 + Fraction(size, 48000)
    stream_out.snapshot(0, 48000, 1)
    stream_out.snapshot(1 + Fraction(size-1, 48000), 48000, 1)
    with pytest.raises(OutOfTimeRange):
        stream_out.snapshot(1 + Fraction(size, 48000), 48000, 1)


def test_identity():
    """Test to convolute with the neutral."""
    identity_queue(0)


def test_identity_queue_1():
    """Test to convolute with the neutral, padded by one 0."""
    identity_queue(1)


def test_identity_queue_2():
    """Test to convolute with the neutral, padded by two 0."""
    identity_queue(2)


def test_identity_queue_128():
    """Test to convolute with the neutral, padded by 128 0."""
    identity_queue(128)


def test_identity_queue_65536():
    """Test to convolute with the neutral, padded by 65536 0."""
    identity_queue(65536)


def test_factor():
    """Test to convolute by a cst value."""
    stream_in, _ = FilterAudioCut(GeneratorAudioNoise(0).out_streams, 1).out_streams
    (stream_out,) = FilterAudioFIR([stream_in], torch.tensor([-.5]), 48000).out_streams
    assert (
        -.5*stream_in.snapshot(Fraction(1, 2), 48000, 64)
        == pytest.approx(stream_out.snapshot(Fraction(1, 2), 48000, 64), rel=1e-6, abs=1e-6)
    )


def test_delay_1():
    """Test to convolute by a delayed dirac (one sample late)."""
    delay(1)


def test_delay_2():
    """Test to convolute by a delayed dirac (two samples late)."""
    delay(2)


def test_delay_128():
    """Test to convolute by a delayed dirac (128 samples late)."""
    delay(128)


def test_delay_65536():
    """Test to convolute by a delayed dirac (65536 samples late)."""
    delay(65536)


# def timer():
#     """Test the perfs for differents sizes."""
#     import time
#     import matplotlib.pyplot as plt
#     (stream_in,) = GeneratorAudioNoise(0).out_streams
#     sizes = [round(2.0**(.25*i)) for i in range(64)]
#     samples2times = {1: [], 4096: [], 65536: []}
#     for size in sizes:
#         (stream,) = FilterAudioFIR([stream_in], torch.full((size,), 1.0/size), 48000).out_streams
#         for samples, times in samples2times.items():
#             stream.snapshot(0, 48000, samples)
#             t_ref = time.time()
#             for _ in range(50):
#                 stream.snapshot(0, 48000, samples)
#             times.append((time.time()-t_ref)/50)
#             print(f"kernel {size}, {samples} samples, {1000*times[-1]:3f} ms")

#     for samples, times in samples2times.items():
#         plt.plot(sizes, times, label=f"{samples} samples")
#     plt.xlabel("len kernel")
#     plt.ylabel("time (s)")
#     plt.legend()
#     plt.xscale("log")
#     plt.yscale("log")
#     plt.show()
