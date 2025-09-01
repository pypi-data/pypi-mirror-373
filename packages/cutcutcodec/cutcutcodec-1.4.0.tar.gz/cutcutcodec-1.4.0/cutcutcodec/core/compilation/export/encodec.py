#!/usr/bin/env python3

"""Allow to suggest an appropriate encoder."""

from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.compilation.export.compatibility import Compatibilities


def suggest_encodec(stream: Stream, stream_settings: dict, muxer: str) -> str:
    """Return the name of an ffmpeg container format appropriate for the given parameters.

    Parameters
    ----------
    stream : cutcutcodec.core.classes.stream.Stream
        The stream that we want to encode.
    stream_settings : dict
        The parameters of the stream in question,
        provided by ``cutcutcodec.core.compilation.export.default.suggest_export_params``.
    muxer : str
        The name of the muxer ffmpeg, it is call "format" in pyav and in returns parameters.

    Returns
    -------
    encoder : str
        An encoder compatible with the provided context.
    """
    assert isinstance(stream, Stream), stream.__class__.__name__
    assert isinstance(stream_settings, dict), stream_settings.__class__.__name__
    assert isinstance(muxer, str), muxer.__class__.__name__

    if stream.type == "audio":
        defaults = ("libopus", "ac3", "aac", "vorbis")
    elif stream.type == "video":
        defaults = ("libaom-av1", "libx265", "libx264")
    else:
        raise TypeError(f"not yet supported {stream.type}")
    for encoder in defaults:
        if Compatibilities().check([encoder], [muxer]).item():
            return encoder
    raise RuntimeError(f"no encodecs found for the stream {stream} with the muxer {muxer}")
