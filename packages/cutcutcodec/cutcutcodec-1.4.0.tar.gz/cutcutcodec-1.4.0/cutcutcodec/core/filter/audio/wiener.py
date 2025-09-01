#!/usr/bin/env python3

"""Implement the denoising wiener filter."""

from fractions import Fraction
import math
import numbers
import typing

import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.layout import Layout
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.signal.psd import welch


class FilterAudioWiener(Filter):
    """Denoised a signal for a given stationary noise spectral density estimation.

    Attributes
    ----------
    level : float
        The denoising level in [0, 1] (readonly).
    band : float or None
        The frequency resolution in Hz (readonly).

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.audio.add import FilterAudioAdd
    >>> from cutcutcodec.core.filter.audio.equation import FilterAudioEquation
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.filter.audio.wiener import FilterAudioWiener
    >>> from cutcutcodec.core.generation.audio.equation import GeneratorAudioEquation
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> _ = torch.manual_seed(0)
    >>> (noise,) = FilterAudioEquation(
    ...     GeneratorAudioNoise(0).out_streams,
    ...     "0.5*fl_0 + 0.2*sin(2*pi*100*t) + 0.1*sin(2*pi*200*t) + 0.1*sin(2*pi*400*t)",
    ...     "0.5*fr_0 + 0.2*cos(2*pi*100*t) + 0.1*cos(2*pi*200*t) + 0.1*cos(2*pi*400*t)",
    ... ).out_streams
    >>> (signal,) = GeneratorAudioEquation("0.5*sin(2*pi*440*t)", "0.5*cos(2*pi*440*t)").out_streams
    >>> (real_signal,) = FilterAudioAdd([signal, noise]).out_streams
    >>> (noise_slice,) = FilterAudioSubclip([noise], 0, 10).out_streams  # select the 10 first sec
    >>> (denoised,) = FilterAudioWiener([noise_slice, real_signal]).out_streams
    >>> frame_denoised = denoised.snapshot(10, 48000, 768000)
    >>> frame_signal = signal.snapshot(10, 48000, 768000)
    >>> torch.mean((frame_signal - real_signal.snapshot(10, 48000, 768000))**2)
    tensor(0.1134)
    >>> torch.mean((frame_signal - frame_denoised)**2)
    tensor(0.0111)
    >>>
    """

    def __init__(
        self,
        in_streams: typing.Iterable[StreamAudio],
        level: numbers.Real = 1.0,
        band: typing.Optional[numbers.Real] = None,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[StreamAudio]
            The concatenation of the noise stream and the audio streams to be denoised.
            Transmitted to :py:class:`cutcutcodec.core.classes.filter.Filter`.
        level : float, default = 1.0
            The denoised level, 0 for the minimum and 1 for the optimal denoised ratio.
        band : float, optional
            The absolute frequency resolution (in Hz) for the estimation of the psd,
            normalized then transmitted to :py:func:`cutcutcodec.core.signal.psd.welch`.
        """
        super().__init__(in_streams, in_streams)
        if len(self.in_streams) != 0:
            super().__init__(in_streams, [_StreamAudioWiener(self)])
            noise = self.in_streams[0]
            assert isinstance(noise, StreamAudio), noise.__class__.__name__
            assert not math.isinf(noise.duration), "the noise stream has to be finite"
        else:
            noise = None
        assert isinstance(level, numbers.Real), level.__class__.__name__
        assert 0 <= level <= 1, level
        self._level = float(level)
        if band is not None:
            assert isinstance(band, numbers.Real), band.__class__.__name__
            band = float(band)
        self._band = band

    def _getstate(self) -> dict:
        return {"level": self._level, "band": self._band}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"level", "band"}, set(state)
        FilterAudioWiener.__init__(self, in_streams, **state)

    @property
    def band(self) -> None | float:
        """Return the frequency resolution in Hz."""
        return self._band

    @property
    def level(self) -> float:
        """Return the denoising level in [0, 1]."""
        return self._level


class _StreamAudioWiener(StreamAudio):
    """Denoise the audio streams."""

    def __init__(self, node: FilterAudioWiener):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.filter.audio.wiener.FilterAudioWiener
            The node containing the StreamAudio to denoise.
        """
        assert isinstance(node, FilterAudioWiener), node.__class__.__name__
        super().__init__(node)
        self._psd_noise = {}

    def _get_psd_noise(self, rate: int) -> torch.Tensor:
        """Cache and compute the psd of the noise."""
        if rate not in self._psd_noise:
            noise_stream = self.node.in_streams[0]
            noise_frame = noise_stream.snapshot(
                noise_stream.beginning, rate, math.floor(rate * noise_stream.duration),
            )
            if (band := self.node.band) is not None:
                band /= noise_frame.rate
            self._psd_noise[rate] = welch(noise_frame, freq_res=band) * self.node.level
        return self._psd_noise[rate]

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        if (
            timestamp + Fraction(samples, rate) > self.beginning + self.duration
            or timestamp < self.beginning
        ):
            raise OutOfTimeRange(
                "the stream has been truncated under "
                f"{self.beginning} and over {self.beginning+self.duration} seconds, "
                f"eval from {timestamp} to length {Fraction(samples, rate)}"
            )

        # get estimation of the noise psd (toto, set in cache to compute it only once)
        psd_noise = self._get_psd_noise(rate)
        win = torch.signal.windows.hann(2*(psd_noise.shape[-1]-1))  # the sum of hanning is cst

        # adjust position to avoid falling in the middle of a window
        pad = [0, 0]  # padding left and right
        before = round((timestamp - self.beginning) * rate)  # number of samples before this frame
        pad[0] = before % (len(win)//2)  # min nbr to add to start at the beginning of the win
        samples += pad[0]
        pad[1] = -(samples % -(len(win)//2))
        samples += pad[1]

        # get raw signal
        samples += len(win)
        raw = self.node.in_streams[1].snapshot(
            timestamp - Fraction(pad[0], rate) - Fraction(len(win)//2, rate),
            rate,
            samples + len(win),
            pad=True,
        )

        # compute filter h
        raw = raw.contiguous()
        fft_raw = raw.as_strided(  # shape (channels, nb_win, len(win))
            (
                raw.shape[0],
                2 * samples // len(win) - 1,  # number of slices
                len(win),
            ),
            (raw.stride(0), len(win)//2, 1),
        )
        fft_raw = fft_raw * win  # not inplace because blocs was not contiguous
        fft_raw = torch.fft.rfft(fft_raw, norm="ortho", dim=2)  # norm ortho for perceval theorem
        psd_raw = fft_raw.real**2 + fft_raw.imag**2
        psd_raw *= len(win) / torch.sum(win)
        psd_src = torch.maximum(
            torch.tensor(1e-8, dtype=psd_raw.dtype, device=psd_raw.device),
            psd_raw - psd_noise[:, None, :]
        )

        # apply filter on each slice
        denoised_slices = torch.fft.irfft(
            (
                fft_raw
                * psd_src / (psd_src + psd_noise[:, None, :])  # filter h in frequency domain
            ),
            norm="ortho",
            dim=-1,
        )

        # overlapp add
        denoised = torch.zeros_like(raw)
        for i in range(denoised_slices.shape[1]):
            denoised[..., i*len(win)//2:i*len(win)//2+len(win)] += denoised_slices[:, i, :].real

        # truncate the padded edges
        denoised = FrameAudio(
            timestamp, rate, raw.layout, denoised[:, pad[0]+len(win)//2:samples-pad[1]-len(win)//2]
        )
        return denoised

    @property
    def beginning(self) -> Fraction:
        return min(s.beginning for s in self.node.in_streams[1:])

    @property
    def duration(self) -> Fraction | float:
        end = max(s.beginning + s.duration for s in self.node.in_streams[1:])
        return end - self.beginning

    @property
    def layout(self) -> Layout:
        if len(layouts := {s.layout for s in self.node.in_streams[1:]}) != 1:
            raise AttributeError(f"add audio streams only implemented for same layout {layouts}")
        return layouts.pop()
