#!/usr/bin/env python3

"""Resample an audio signal."""

from fractions import Fraction
import math
import numbers
import typing

import numpy as np
import torch

from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.filter.audio.fir import FilterAudioFIR


def anti_aliasing(
    rate: numbers.Integral,
    cutoff: numbers.Real,
    band: typing.Optional[numbers.Real] = None,
    attenuation: numbers.Real = 120.0,
) -> np.ndarray:
    """Find the best type 1 impulse response that perfectly matchs the constraints.

    Search the low pass symetric odd filter filter as possible.
    This filter introduces a linear phase shift, with a time delay equal to ``len(rif)/(2*rate)``.

    Parameters
    ----------
    rate : int
        The sampling rate of the filter in time domain in Hz.
    cutoff : float
        The cut-off absolute frequency in Hz. It has to be < rate/2.
        It is not the -3 dB but the ``-attenuation`` dB frequency.
    band : float, optional
        The absolute width of the transition band in Hz.
        If not provide, the value is compute for an audio application that
        correspond to the perceptive frequency hearing threshold resolution.
        It is based on a MEL cut-off of 5 musical cents, or 5 `mel_cent`.
        One cent is define by cent = f0 * 2**(1/1200).
    attenuation : float, default=120
        The attenuation in the stopband in dB.
        Transmitted to ``cutcutcodec.core.filter.audio.resample.kaiser``.

    Returns
    -------
    rif : np.ndarray
        The 1d symetric odd finite response that matche the given constraints.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.filter.audio.resample import anti_aliasing
    >>> fir = anti_aliasing(48000, 8000)
    >>> np.round(fir, 11)
    array([-3.8e-10, -5.6e-10, -1.8e-10, ..., -1.8e-10, -5.6e-10, -3.8e-10])
    >>>
    >>> # import matplotlib.pyplot as plt
    >>> # fig, (ax_t, ax_f) = plt.subplots(ncols=2)
    >>> # _ = fig.suptitle("FIR filter design")
    >>> # _ = ax_f.set_title("Frequency domain response")
    >>> # _ = ax_f.set_xlabel("freq [Hz]")
    >>> # _ = ax_f.set_ylabel("gain [dB]")
    >>> # _ = ax_t.set_title("Temporal domain response")
    >>> # _ = ax_t.set_xlabel("time [s]")
    >>> # _ = ax_t.set_ylabel("magnitude")
    >>> # _ = ax_t.plot(np.arange(len(fir))/48000, fir, "o-")
    >>> # _ = ax_f.plot(
    >>> #      np.linspace(-24000, 24000, 128*len(fir)+1),
    >>> #      20*np.log10(abs(np.fft.fftshift(np.fft.fft(fir, n=128*len(fir)+1)/48000))))
    >>> # fig.tight_layout()
    >>> # plt.show()
    >>>
    """
    assert isinstance(rate, numbers.Integral), rate.__class__.__name__
    assert rate > 0, rate
    rate = int(rate)
    assert isinstance(cutoff, numbers.Real), cutoff.__class__.__name__
    cutoff = float(cutoff)
    if band is not None:
        assert isinstance(band, numbers.Real), band.__class__.__name__
        band = float(band)
        assert band > 0, band
    assert cutoff < .5*rate, cutoff

    if band is None:
        band = 1127.0 * math.log(1.0 + cutoff/700.0)  # mel scale
        band *= (2.0**(1.0/240.0) - 1.0)  # 5 cents
    cutoff -= .5*band
    win = kaiser(band/rate, attenuation)
    times = np.arange(-(len(win)-1)//2, (len(win)+1)//2, dtype=float) / rate
    rif = 2.0*cutoff*np.sinc(2.0*cutoff*times)
    rif /= rate  # normalize to get unity gain
    rif *= win
    return rif


def kaiser(band: numbers.Real, attenuation: numbers.Real) -> np.ndarray:
    """Design a kaiser window with some frequencial properties.

    Parameters
    ----------
    band : float
        Transition band, as a fraction of the sampling rate in ]0, 0.5[.
    attenuation : float
        The attenuation in the stopband in dB.

    Returns
    -------
    window : torch.Tensor
        The 1d symetric odd window.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.filter.audio.resample import kaiser
    >>> np.round(kaiser(0.05, 80), 5)
    array([0.00267, 0.00453, 0.00692, 0.00991, 0.01359, 0.01803, 0.02331,
           0.02951, 0.03671, 0.04499, 0.05443, 0.06508, 0.07702, 0.0903 ,
           0.10497, 0.12107, 0.13863, 0.15766, 0.17817, 0.20016, 0.22359,
           0.24845, 0.27467, 0.30219, 0.33093, 0.3608 , 0.39168, 0.42346,
           0.45599, 0.48912, 0.5227 , 0.55654, 0.59048, 0.62431, 0.65784,
           0.69088, 0.72321, 0.75464, 0.78496, 0.81398, 0.84149, 0.86731,
           0.89127, 0.91319, 0.93292, 0.95033, 0.96527, 0.97765, 0.98737,
           0.99437, 0.99859, 1.     , 0.99859, 0.99437, 0.98737, 0.97765,
           0.96527, 0.95033, 0.93292, 0.91319, 0.89127, 0.86731, 0.84149,
           0.81398, 0.78496, 0.75464, 0.72321, 0.69088, 0.65784, 0.62431,
           0.59048, 0.55654, 0.5227 , 0.48912, 0.45599, 0.42346, 0.39168,
           0.3608 , 0.33093, 0.30219, 0.27467, 0.24845, 0.22359, 0.20016,
           0.17817, 0.15766, 0.13863, 0.12107, 0.10497, 0.0903 , 0.07702,
           0.06508, 0.05443, 0.04499, 0.03671, 0.02951, 0.02331, 0.01803,
           0.01359, 0.00991, 0.00692, 0.00453, 0.00267])
    """
    # verifs
    assert isinstance(band, numbers.Real), band.__class__.__name__
    assert 0 < band < 0.5, band
    assert isinstance(attenuation, numbers.Real), attenuation.__class__.__name__
    band = float(band)
    attenuation = abs(float(attenuation))

    # parameters
    if not (nb_samples := math.ceil((attenuation - 8) / (2.285 * 2 * math.pi * band)) + 1) % 2:
        nb_samples += 1  # make sure is odd
    if attenuation < 21:
        beta = 0.0
    elif attenuation <= 50:
        beta = 0.5842 * (attenuation-21)**0.4 + 0.07886 * (attenuation-21)
    else:
        beta = 0.1102 * (attenuation-8.7)

    # compute window
    win = np.kaiser(nb_samples, beta)
    return win


def sinc_continuous(
    frame: FrameAudio, timestamp: Fraction, rate: int, samples: int, *, win: int = 256
) -> FrameAudio:
    """Resample the signal by the exact continuous function.

    It process in two steps:
    1) Discrete to continuous signal. Convolute by a cardinal sinus.
    2) Continus to dicrete. Eval the continuous signal on some points.

    There is no anti-aliasing filter for downsampeling.
    We assume that the signal doese not contains any frequecies other `rate/2`.
    The temporal and spacial complexity is o(samples*win).

    Parameters
    ----------
    frame : cutcutcodec.core.classes.fream_audio.FrameAudio
        The reference frame to resample.
    timestamp : Fraction
        The starting time the new resampled frame.
        For more information, see ``cutcutcodec.core.classes.stream_audio.StreamAudio.snapshot``.
    rate : int
        The new sample rate.
        For more information, see ``cutcutcodec.core.classes.stream_audio.StreamAudio.snapshot``.
    samples : int
        The number of samples in the new resampled frame.
        For more information, see ``cutcutcodec.core.classes.stream_audio.StreamAudio.snapshot``.
    win : int, optinal
        The maximum half width of the sliding windows.
        It correspond to the number of samples in the source frame
        that contribute to compute one sample in the destination frame.
        Bigger it is, slowler is the computation o(n), but more is accurate. Has to be odd number.

    Returns
    -------
    new_frame : cutcutcodec.core.classes.fream_audio.FrameAudio
        The resampled frame.

    Examples
    --------
    >>> from fractions import Fraction
    >>> import torch
    >>> from cutcutcodec.core.filter.audio.resample import sinc_continuous
    >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
    >>> frame = FrameAudio(1, 8000, "mono", torch.empty(1, 512))
    >>> frame[:, :] = torch.sin(2*torch.pi*3960*frame.timestamps).reshape(1, -1)  # 1% to shannon
    >>> frame[:, :] *= torch.blackman_window(frame.samples, periodic=False).reshape(1, -1)
    >>> new_frame = sinc_continuous(frame, 1-Fraction(16, 8000), 96000, 96000*544//8000)
    >>>
    >>> torch.round(frame, decimals=3)
    FrameAudio(1, 8000, 'mono', [[-0.   ,  0.   , -0.   ,  0.   , -0.   ,
                                   0.   , -0.   ,  0.   , -0.   ,  0.   ,
                                  -0.   ,  0.001, -0.001,  0.001, -0.001,
                                   0.001, -0.002,  0.002, -0.002,  0.003,
                                  -0.003,  0.004, -0.004,  0.005, -0.006,
                                   0.006, -0.007,  0.008, -0.009,  0.009,
                                  -0.01 ,  0.011, -0.012,  0.013, -0.015,
                                   0.016, -0.017,  0.018, -0.02 ,  0.021,
                                  -0.022,  0.024, -0.025,  0.027, -0.028,
                                   0.03 , -0.032,  0.033, -0.035,  0.037,
                                  -0.038,  0.04 , -0.042,  0.043, -0.045,
                                   0.047, -0.048,  0.05 , -0.052,  0.053,
                                  -0.055,  0.056, -0.058,  0.059, -0.06 ,
                                   0.062, -0.063,  0.064, -0.065,  0.066,
                                  -0.066,  0.067, -0.067,  0.068, -0.068,
                                   0.068, -0.068,  0.068, -0.067,  0.067,
                                  -0.066,  0.065, -0.064,  0.062, -0.061,
                                   0.059, -0.057,  0.054, -0.052,  0.049,
                                  -0.046,  0.042, -0.039,  0.035, -0.031,
                                   0.026, -0.022,  0.017, -0.011,  0.006,
                                  -0.   , -0.006,  0.012, -0.019,  0.026,
                                  -0.034,  0.041, -0.049,  0.057, -0.065,
                                   0.074, -0.083,  0.091, -0.101,  0.111,
                                  -0.121,  0.13 , -0.141,  0.152, -0.161,
                                   0.173, -0.183,  0.195, -0.206,  0.218,
                                  -0.229,  0.24 , -0.252,  0.263, -0.275,
                                   0.286, -0.298,  0.31 , -0.321,  0.332,
                                  -0.343,  0.355, -0.366,  0.377, -0.388,
                                   0.398, -0.408,  0.418, -0.428,  0.438,
                                  -0.447,  0.456, -0.464,  0.472, -0.48 ,
                                   0.487, -0.493,  0.5  , -0.505,  0.511,
                                  -0.515,  0.519, -0.523,  0.526, -0.528,
                                   0.53 , -0.531,  0.531, -0.531,  0.529,
                                  -0.528,  0.526, -0.522,  0.518, -0.513,
                                   0.508, -0.501,  0.494, -0.488,  0.478,
                                  -0.469,  0.458, -0.448,  0.437, -0.423,
                                   0.41 , -0.395,  0.381, -0.365,  0.35 ,
                                  -0.333,  0.314, -0.296,  0.276, -0.257,
                                   0.235, -0.214,  0.193, -0.17 ,  0.148,
                                  -0.124,  0.101, -0.075,  0.051, -0.026,
                                   0.   ,  0.025, -0.054,  0.08 , -0.106,
                                   0.133, -0.16 ,  0.188, -0.215,  0.245,
                                  -0.272,  0.299, -0.327,  0.354, -0.384,
                                   0.408, -0.438,  0.464, -0.49 ,  0.517,
                                  -0.542,  0.57 , -0.594,  0.62 , -0.643,
                                   0.666, -0.69 ,  0.712, -0.736,  0.756,
                                  -0.777,  0.796, -0.815,  0.835, -0.851,
                                   0.868, -0.884,  0.898, -0.912,  0.924,
                                  -0.937,  0.948, -0.958,  0.966, -0.974,
                                   0.981, -0.987,  0.991, -0.995,  0.997,
                                  -0.998,  0.998, -0.997,  0.995, -0.992,
                                   0.988, -0.982,  0.976, -0.969,  0.959,
                                  -0.95 ,  0.939, -0.928,  0.915, -0.901,
                                   0.886, -0.87 ,  0.854, -0.835,  0.819,
                                  -0.8  ,  0.778, -0.758,  0.736, -0.715,
                                   0.69 , -0.667,  0.643, -0.618,  0.593,
                                  -0.567,  0.541, -0.512,  0.486, -0.459,
                                   0.43 , -0.403,  0.372, -0.345,  0.315,
                                  -0.287,  0.259, -0.229,  0.201, -0.17 ,
                                   0.142, -0.112,  0.085, -0.057,  0.027,
                                   0.   , -0.028,  0.055, -0.08 ,  0.108,
                                  -0.133,  0.161, -0.185,  0.21 , -0.233,
                                   0.255, -0.28 ,  0.3  , -0.323,  0.343,
                                  -0.364,  0.382, -0.4  ,  0.42 , -0.436,
                                   0.453, -0.467,  0.484, -0.496,  0.508,
                                  -0.522,  0.532, -0.543,  0.552, -0.561,
                                   0.57 , -0.576,  0.583, -0.588,  0.593,
                                  -0.596,  0.599, -0.602,  0.603, -0.604,
                                   0.603, -0.603,  0.601, -0.599,  0.596,
                                  -0.592,  0.588, -0.583,  0.577, -0.571,
                                   0.564, -0.557,  0.549, -0.54 ,  0.532,
                                  -0.522,  0.512, -0.502,  0.492, -0.481,
                                   0.469, -0.458,  0.446, -0.434,  0.422,
                                  -0.409,  0.397, -0.383,  0.37 , -0.358,
                                   0.344, -0.331,  0.317, -0.304,  0.291,
                                  -0.277,  0.265, -0.251,  0.238, -0.224,
                                   0.212, -0.199,  0.187, -0.174,  0.161,
                                  -0.15 ,  0.137, -0.126,  0.115, -0.104,
                                   0.093, -0.082,  0.072, -0.062,  0.052,
                                  -0.043,  0.033, -0.025,  0.016, -0.008,
                                  -0.   ,  0.007, -0.014,  0.022, -0.028,
                                   0.034, -0.04 ,  0.046, -0.051,  0.055,
                                  -0.06 ,  0.064, -0.068,  0.072, -0.076,
                                   0.079, -0.081,  0.084, -0.086,  0.088,
                                  -0.089,  0.091, -0.092,  0.093, -0.094,
                                   0.094, -0.094,  0.094, -0.094,  0.094,
                                  -0.093,  0.093, -0.092,  0.091, -0.09 ,
                                   0.088, -0.087,  0.086, -0.084,  0.082,
                                  -0.081,  0.079, -0.077,  0.075, -0.073,
                                   0.071, -0.069,  0.066, -0.064,  0.062,
                                  -0.06 ,  0.058, -0.055,  0.053, -0.051,
                                   0.049, -0.047,  0.044, -0.042,  0.04 ,
                                  -0.038,  0.036, -0.034,  0.032, -0.03 ,
                                   0.028, -0.027,  0.025, -0.023,  0.022,
                                  -0.02 ,  0.019, -0.017,  0.016, -0.015,
                                   0.013, -0.012,  0.011, -0.01 ,  0.009,
                                  -0.008,  0.007, -0.006,  0.006, -0.005,
                                   0.004, -0.004,  0.003, -0.003,  0.002,
                                  -0.002,  0.002, -0.001,  0.001, -0.001,
                                   0.001, -0.   ,  0.   , -0.   ,  0.   ,
                                   0.   , -0.   ,  0.   , -0.   ,  0.   ,
                                  -0.   ,  0.   , -0.   ,  0.   , -0.   ,
                                   0.   ,  0.   ]])
    >>> middle = new_frame.samples//2
    >>> torch.round(new_frame[:, middle-32:middle+32], decimals=3).numpy()
    array([[ 0.588,  0.359,  0.109, -0.151, -0.398, -0.619, -0.8  , -0.927,
            -0.992, -0.99 , -0.923, -0.793, -0.612, -0.39 , -0.139,  0.118,
             0.371,  0.595,  0.781,  0.915,  0.988,  0.995,  0.935,  0.813,
             0.635,  0.417,  0.172, -0.088, -0.339, -0.571, -0.761, -0.901,
            -0.982, -0.997, -0.946, -0.83 , -0.66 , -0.444, -0.201,  0.056,
             0.312,  0.544,  0.742,  0.889,  0.976,  0.999,  0.956,  0.848,
             0.683,  0.474,  0.231, -0.025, -0.28 , -0.518, -0.719, -0.873,
            -0.969, -1.   , -0.964, -0.864, -0.707, -0.501, -0.263, -0.009]],
          dtype=float32)
    >>>
    >>> # import matplotlib.pyplot as plt
    >>> # plt.xlabel("time (s)"); plt.ylabel("magnitude")
    >>> # plt.plot(frame.timestamps.numpy(), frame.transpose(0, 1).numpy(), marker="o")
    >>> # plt.plot(new_frame.timestamps.numpy(), new_frame.transpose(0, 1).numpy(), marker="o")
    >>> # plt.show()
    >>>
    """
    assert isinstance(frame, FrameAudio), frame.__class__.__name__
    assert isinstance(timestamp, Fraction), timestamp.__class__.__name__
    assert isinstance(rate, int), rate.__class__.__name__
    assert isinstance(samples, int), samples.__class__.__name__
    assert isinstance(win, int), win.__class__.__name__

    # initialisation of the empty new frame
    dst_frame = FrameAudio(
        timestamp,
        rate,
        frame.layout,
        torch.empty((frame.channels, samples), dtype=frame.dtype, device=frame.device),
    )

    # precompute and cache some useful values
    src_t = frame.timestamps  # shape (frame.samples,)
    dst_t = dst_frame.timestamps  # shape (samples,)

    # For the dst sample i, j=indexs[i] corresponds to the src sample j, with the time matching
    indexs = dst_t - float(frame.time)  # copy, shape (samples,)
    indexs *= frame.rate
    indexs = indexs.to(torch.int32, copy=False)
    indexs = ((dst_t - float(frame.time)) * frame.rate).to(torch.int32)
    win = min(win, (frame.samples-1)//2)
    indexs = torch.clip(indexs, win, frame.samples-1-win, out=indexs)

    # the cardinal sinuns to convolve
    sinc_conv = torch.empty(
        (samples, 2*win+1), dtype=frame.dtype, device=frame.device
    )  # shape (samples, 2*win+1)
    for i in range(2*win+1):
        sinc_conv[:, i] = src_t[indexs-win+i]  # src_t
    sinc_conv -= dst_t.unsqueeze(1)  # src_t - dst_t
    sinc_conv *= frame.rate  # src_rate * (src_t - dst_t), pi is included in the sinc torch function
    sinc_conv = torch.sinc(sinc_conv, out=sinc_conv)  # sin(x)/x, x = pi*src_rate*(src_t-dst_t)

    # the cardinal sinuns magnitude
    magnitude = torch.empty(
        (frame.channels, samples, 2*win+1), dtype=frame.dtype, device=frame.device
    )  # shape (nb_channels, samples, 2*win+1)
    for i in range(2*win+1):
        magnitude[:, :, i] = frame[:, indexs-win+i]

    # final dot product
    values = torch.mul(magnitude, sinc_conv.unsqueeze(0), out=magnitude)
    del sinc_conv
    values = torch.sum(values, dim=2, keepdim=False)  # shape (nb_channels, samples, 2*win+1)
    dst_frame[:, :] = values

    return dst_frame


class FilterAudioAntiAliasing(FilterAudioFIR):
    """Anti-aliasing filter for audio subsampling.

    This filter is a class 1 finite impulse response linear phase low-pass filter.

    Attributes
    ----------
    cutoff : float
        The cutoff frequency in Hz (readonly).
    delay : Fraction
        The delay introduced by the filter in seconds (readonly).

    Examples
    --------
    >>> from cutcutcodec.core.filter.audio.resample import FilterAudioAntiAliasing
    >>> from cutcutcodec.core.generation.audio.equation import GeneratorAudioEquation
    >>> (audio_a4,) = GeneratorAudioEquation("sin(2*pi*440*t)").out_streams
    >>> (audio_a5,) = GeneratorAudioEquation("sin(2*pi*880*t)").out_streams
    >>> out_a4, out_a5 = FilterAudioAntiAliasing([audio_a4, audio_a5], 622).out_streams
    >>> (out_a4.snapshot(10, 48000, 768000)**2).mean()  # signal power (no attenuation)
    tensor(0.5000)
    >>> (out_a5.snapshot(10, 48000, 768000)**2).mean()  # signal power (attenuation)
    tensor(3.9965e-08)
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[StreamAudio], cutoff: numbers.Real):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.filter.audio.fir.FilterAudioFIR``.
        cutoff : float
            The cut-off frequency in Hz. For the Shannon criteria, it is the half sample rate.
            The margin, the band with and the attenuation have been automatically chosen
            for the earing sensibility in the case of an audio application.
        """
        assert isinstance(cutoff, numbers.Real), cutoff.__class__.__name__
        assert cutoff > 0, cutoff
        self._cutoff = float(cutoff)
        rate = math.floor(2*self._cutoff) + 1
        fir = torch.from_numpy(anti_aliasing(rate, cutoff))
        super().__init__(in_streams, fir, rate)

    def _getstate(self) -> dict:
        return {
            "cutoff": self.cutoff,
        }

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"cutoff"}, set(state)
        FilterAudioAntiAliasing.__init__(self, in_streams, state["cutoff"])

    @property
    def cutoff(self) -> Fraction:
        """Return the cutoff frequency in Hz."""
        return self._cutoff

    @property
    def delay(self) -> Fraction:
        """Return the delay introduced by the filter in seconds."""
        return Fraction(len(self._fir)-1, 2*self._fir_rate)

    def resample_fir(self, rate: int) -> torch.Tensor:
        """Recompute the antialiasing fir from scratch."""
        return torch.from_numpy(anti_aliasing(rate, self._cutoff))
