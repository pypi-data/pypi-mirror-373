#!/usr/bin/env python3

"""Apply an invariant linear convolutional filter to an audio signal."""

from fractions import Fraction
import base64
import lzma
import math
import numbers
import typing

import numpy as np
import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.layout import Layout
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.exceptions import OutOfTimeRange


class FilterAudioFIR(Filter):
    """Invariant finite impulse response convolutional filter (FIR).

    Attributes
    ----------
    fir : torch.Tensor
        The impulsional response (1d) (readonly).
    fir_rate : int
        The sample rate of the impulsional response (readonly).

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.audio.fir import FilterAudioFIR
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> (stream_in,) = GeneratorAudioNoise(0).out_streams
    >>> stream_in.snapshot(0, 48000, 4)
    FrameAudio(0, 48000, 'stereo', [[ 0.44649088,  0.8031031 , -0.25397146,
                                     -0.1199106 ],
                                    [-0.8036704 ,  0.72772765,  0.17409873,
                                      0.42185044]])
    >>> (stream_out,) = FilterAudioFIR([stream_in], torch.tensor([1, 0, -.5]), 48000).out_streams
    >>> stream_out.snapshot(0, 48000, 4).to(torch.float16)
    FrameAudio(0, 48000, 'stereo', [[ 0.4465 ,  0.803  , -0.4773 , -0.5215 ],
                                    [-0.8037 ,  0.7275 ,  0.576  ,  0.05798]],
                                   dtype=torch.float16)
    >>>
    """

    def __init__(
        self,
        in_streams: typing.Iterable[StreamAudio],
        fir: torch.Tensor,
        fir_rate: numbers.Integral,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        fir : torch.Tensor
            The impulsional response, 1d vector.
        fir_rate : int
            The samplerate of the impulsional response.
        """
        # check
        assert isinstance(in_streams, typing.Iterable), in_streams.__class__.__name__
        in_streams = tuple(in_streams)
        assert isinstance(fir, torch.Tensor), fir.__class__.__name__
        assert fir.ndim == 1, fir.shape
        assert fir.shape[0] > 0, fir.shape
        assert fir.dtype.is_floating_point, fir.dtype
        assert isinstance(fir_rate, numbers.Integral), fir_rate.__class__.__name__
        assert fir_rate > 0, fir_rate

        # initialisation
        self._fir = fir
        self._fir_rate = int(fir_rate)
        super().__init__(
            in_streams, [_StreamAudioConvolution(self) for _ in range(len(in_streams))]
        )

    def _getstate(self) -> dict:
        return {
            "fir_encoded": FilterAudioFIR.encode_fir(self._fir),
            "fir_rate": self._fir_rate,
        }

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"fir_encoded", "fir_rate"}, set(state)
        FilterAudioFIR.__init__(
            self, in_streams, FilterAudioFIR.decode_fir(state["fir_encoded"]), state["fir_rate"]
        )

    @staticmethod
    def encode_fir(fir: torch.Tensor) -> str:
        """Encode the fir tensor into a jsonisable string."""
        return base64.b64encode(
            lzma.compress(
                fir.numpy(force=True).astype(np.float64).tobytes(),
                format=lzma.FORMAT_ALONE,
                check=lzma.CHECK_NONE,
                preset=9,
            )
        ).decode()

    @staticmethod
    def decode_fir(fir: str) -> torch.Tensor:
        """Decode the encoded fir."""
        return torch.from_numpy(
            np.frombuffer(
                bytearray(lzma.decompress(base64.b64decode(fir), format=lzma.FORMAT_ALONE)),
                dtype=np.float64,
            )
        )

    @property
    def fir(self) -> torch.Tensor:
        """Return the impulsional response, 1d vector."""
        return self._fir

    @property
    def fir_rate(self) -> int:
        """Return the sample rate of the impulsional response."""
        return self._fir_rate

    def resample_fir(self, rate: int) -> torch.Tensor:
        """Resample the fir to the right rate.

        It can be overwritten.
        """
        assert isinstance(rate, int), rate.__class__.__name__
        if rate != self._fir_rate:
            raise NotImplementedError(
                f"the impulsional rate ({self._fir_rate} Hz) "
                f"and the signal rate ({rate} Hz) have to be the same."
            )
        return self._fir


class _StreamAudioConvolution(StreamAudio):
    """A convoluted audio stream."""

    def __init__(self, node: FilterAudioFIR):
        assert isinstance(node, FilterAudioFIR), node.__class__.__name__
        super().__init__(node)
        self._fir = node.fir.flip(0).reshape(1, 1, -1)  # torch conv is correlation, not convolution
        self._fir_fft = None  # for fast fft convolution
        self._fir_rate = node.fir_rate

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        # resample impulsional response
        if rate != self._fir_rate:
            self._fir = self.node.resample_fir(rate).flip(0).reshape(1, 1, -1)
            self._fir_fft = None
            self._fir_rate = rate

        # new parameters considering convolution shift
        req_timestamp = timestamp - Fraction((self._fir.shape[2]-1), rate)
        req_samples = samples + self._fir.shape[2] - 1

        # zero padding left
        if req_timestamp < self.beginning:
            if (pad_l := math.ceil(rate * (self.beginning-req_timestamp))) >= self._fir.shape[2]:
                raise OutOfTimeRange(
                    f"the is no audio frame at timestamp {timestamp} (need >= {self.beginning})"
                )
            req_timestamp += Fraction(pad_l, rate)
            req_samples -= pad_l
        else:
            pad_l = 0

        # zero padding right
        exedent_time = (
            req_timestamp+Fraction(req_samples, rate)
            - (self.beginning+self.node.in_streams[self.index].duration)
        )
        if exedent_time > 0:
            if (pad_r := math.floor(rate * exedent_time)) >= self._fir.shape[2]:
                raise OutOfTimeRange(
                    f"stream start {self.beginning} and end {self.beginning + self.duration}, "
                    f"no stream at timestamp {timestamp} to {timestamp} + {samples}/{rate}"
                )
            req_samples -= pad_r
        else:
            pad_r = 0

        # get input signal and add zeros if it is required
        frame = (
            self.node.in_streams[self.index]  # pylint: disable=W0212
            ._snapshot(req_timestamp, rate, req_samples)
        )
        if pad_l or pad_r:
            signal = torch.nn.functional.pad(frame, (pad_l, pad_r), mode="constant", value=0.0)
        else:
            signal = frame

        # cast, apply convolution and recast
        if self._fir.shape[2] < 256:
            self._fir = self._fir.to(device=signal.device, dtype=signal.dtype)
            out = torch.nn.functional.conv1d(signal.unsqueeze(1), self._fir, padding=0).squeeze(1)
        else:
            if self._fir_fft is None or self._fir_fft.shape[1] != signal.shape[1]:
                self._fir_fft = torch.fft.fft(
                    self._fir.reshape(1, -1).flip(1), n=signal.shape[1], dim=1
                )
            dtype = {
                torch.float16: torch.complex32,
                torch.float32: torch.complex64,
                torch.float64: torch.complex128,
            }[signal.dtype]
            self._fir_fft = self._fir_fft.to(device=signal.device, dtype=dtype)
            sig = torch.fft.fft(signal, dim=1)  # copy because float to complex
            out = (
                torch.fft.ifft(torch.mul(sig, self._fir_fft, out=sig), dim=1, out=sig)
                [:, self._fir.shape[2]-1:]
                .real
            )

        return FrameAudio(timestamp, rate, signal.layout, out)

    @property
    def beginning(self) -> Fraction:
        return self.node.in_streams[self.index].beginning

    @property
    def duration(self) -> Fraction | float:
        return (
            self.node.in_streams[self.index].duration
            + Fraction(len(self.node.fir)-1, self.node.fir_rate)
        )

    @property
    def layout(self) -> Layout:
        """Return the signification of each channels."""
        return self.node.in_streams[self.index].layout
