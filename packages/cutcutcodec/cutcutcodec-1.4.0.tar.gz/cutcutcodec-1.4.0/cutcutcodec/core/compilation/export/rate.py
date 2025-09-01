#!/usr/bin/env python3

"""Allow to suggest an appropriate rate."""

from fractions import Fraction
import logging
import typing

from cutcutcodec.core.analysis.stream.rate_audio import optimal_rate_audio
from cutcutcodec.core.analysis.stream.rate_video import optimal_rate_video
from cutcutcodec.core.classes.encoder import Encoder
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.classes.stream_video import StreamVideo


def available_audio_rates(encoders: typing.Iterable[str]) -> None | set[int]:
    """Search the different sampling frequencies available by this encoder.

    Parameters
    ----------
    encoders : list[str]
        The encoder name.

    Returns
    -------
    rates : set[int] or None
        The set of the available rates. The value None means their is no constraints.
        An empty set means there is not availaible or common rates.

    Examples
    --------
    >>> from cutcutcodec.core.compilation.export.rate import available_audio_rates
    >>> available_audio_rates([])
    set()
    >>> sorted(available_audio_rates(["libmp3lame"]))
    [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]
    >>> sorted(available_audio_rates(["libopus"]))
    [8000, 12000, 16000, 24000, 48000]
    >>> print(available_audio_rates(["flac"]))
    None
    >>> sorted(available_audio_rates(["libmp3lame", "libopus"]))
    [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]
    >>>
    """
    assert isinstance(encoders, typing.Iterable), encoders.__class__.__name__
    common_rates = set()
    for encoder in encoders:
        if (rates := Encoder(encoder).audio_rates) is None:
            return None
        common_rates |= set(rates)
    return common_rates


def suggest_audio_rate(
    stream: StreamAudio, choices: typing.Optional[typing.Iterable[int]] = None
) -> int:
    """Return the best compatible audio samplerate.

    Parameters
    ----------
    stream : cutcutcodec.core.classes.stream_audio.StreamAudio
        The stream that we want to encode.
    choices : set[int], optional
        The possible rates. If provide, returns the most appropriate rate of this set.
        The value None means all rates are allowed.
        This selection could be generated from
        ``cutcutcodec.core.compilation.export.rate.available_audio_rates``.

    Returns
    -------
    rate : int
        A suitable sampling rate compatible with the specified options.

    Examples
    --------
    >>> from cutcutcodec.core.compilation.export.rate import suggest_audio_rate
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> audio = get_project_root().parent / "media" / "audio" / "narration_5_1.oga"
    >>> (stream,) = ContainerInputFFMPEG(audio).out_streams
    >>> suggest_audio_rate(stream)  # no constraint
    16000
    >>> suggest_audio_rate(stream, [8000, 12000, 24000, 48000])  # constraint
    24000
    >>>
    """
    assert isinstance(stream, StreamAudio), stream.__class__.__name__
    if choices is not None:
        assert isinstance(choices, typing.Iterable), choices.__class__.__name__
        choices = set(choices)
        assert all(isinstance(r, int) for r in choices), choices
        assert all(r > 0 for r in choices), choices

    # estimation of the best rate
    optimal: int = optimal_rate_audio(stream)  # can be 0, not None

    # select the most appropriate rate among the choices
    if not optimal:  # if the optimal rate is not found
        choices = choices or [48000]  # default value
        return min(choices, key=lambda r: (r < 48000, abs(r-48000)))
    if choices is None:
        return optimal
    choice = min(choices, key=lambda r: (r < optimal, abs(r-optimal)))
    if choice < optimal:
        logging.warning(
            "spectral aliasing, append low pass filter because max rate is %d and best is %d",
            max(choices),
            optimal
        )
    return choice


def suggest_video_rate(stream: StreamVideo) -> Fraction:
    """Return the best compatible video framerate.

    Parameters
    ----------
    stream : cutcutcodec.core.classes.stream_video.StreamVideo
        The stream that we want to encode.

    Returns
    -------
    rate : Fraction
        An optimal frame rate.

    Examples
    --------
    >>> from cutcutcodec.core.compilation.export.rate import suggest_video_rate
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> video = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> stream = ContainerInputFFMPEG(video).out_select("video")[0]
    >>> suggest_video_rate(stream)
    Fraction(30000, 1001)
    >>>
    """
    return optimal_rate_video(stream) or Fraction(30000, 1001)
