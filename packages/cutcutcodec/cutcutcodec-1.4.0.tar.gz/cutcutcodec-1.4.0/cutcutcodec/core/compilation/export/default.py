#!/usr/bin/env python3

"""Find the default settings for ``cutcutcodec.core.io.write_ffmpeg.ContainerOutputFFMPEG``."""

import pathlib

from cutcutcodec.core.analysis.stream.shape import optimal_shape_video
from cutcutcodec.core.classes.muxer import Muxer
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.compilation.export.encodec import suggest_encodec
from cutcutcodec.core.compilation.export.muxer import suggest_muxer
from cutcutcodec.core.compilation.export.rate import available_audio_rates, suggest_audio_rate
from cutcutcodec.core.compilation.export.rate import suggest_video_rate


def suggest_export_params(
    in_streams: tuple[Stream],
    *,
    filename: pathlib.Path,
    streams_settings: list[dict],
    container_settings: dict,
):
    """Suggest a combination of suitable parameters for ContainerOutputFFMPEG.

    Parameters
    ----------
    in_streams : tuple[cutcutcodec.core.classes.stream.Stream]
        The ordered streams to be encoded.
    filename : pathlike, optional
        The final file, relative or absolute.
        If the suffix is provided, it allows to find the muxer (if it is not already provided).
        If the muxer is provided, the associated suffix is added to the file name
        (if the filename has no suffix)
    streams_settings: list[dict]
        As the input parameter `streams_settings` of the class
        ``cutcutcodec.core.io.write_ffmpeg.ContainerOutputFFMPEG`` with None values
        where you have to look for a suitable parameter.
    container_settings: dict
        As the input parameter `container_settings` of the class
        ``cutcutcodec.core.io.write_ffmpeg.ContainerOutputFFMPEG`` with None values
        where you have to look for a suitable parameter.

    Returns
    -------
    filename : pathlib.Path
        A default file name with the appropriate suffix.
    streams_settings : list[dict]
        Same structure as the input parameter but with the
        None fields replaced by there final value.
    container_settings : dict
        Same structure as the input parameter but with the
        None fields replaced by there final value.
    """
    assert isinstance(in_streams, tuple), in_streams.__class__.__name__
    assert all(isinstance(s, Stream) for s in in_streams), in_streams
    assert isinstance(filename, pathlib.Path), filename.__class__.__name__
    assert isinstance(streams_settings, list), streams_settings.__class__.__name__
    assert all(isinstance(s, dict) for s in streams_settings), streams_settings
    assert len(streams_settings) == len(in_streams), (streams_settings, in_streams)
    assert isinstance(container_settings, dict), container_settings.__class__.__name__

    # find muxer if no suffix and no muxer provided
    if not filename.suffix and container_settings["format"] is None:
        container_settings["format"] = suggest_muxer()

    # add suffix if muxer is given
    if (
        not filename.suffix and container_settings["format"] is not None
        and (extensions := Muxer(container_settings["format"]).extensions)
    ):
        filename = filename.with_suffix(sorted(extensions)[0])

    # find muxer if suffix is given
    if filename.suffix and container_settings["format"] is None:
        container_settings["format"] = Muxer(filename.suffix).name

    # find the parameters for each stream
    for stream, stream_settings in zip(in_streams, streams_settings):

        # find encodec if not provide
        if stream_settings["encodec"] is None:
            stream_settings["encodec"] = (
                suggest_encodec(stream, stream_settings, container_settings["format"])
            )

        # shape
        if stream.type == "video" and stream_settings.get("shape", None) is None:
            stream_settings["shape"] = optimal_shape_video(stream) or (720, 1080)

        # rate
        if stream.type == "audio" and stream_settings.get("rate", None) is None:
            stream_settings["rate"] = suggest_audio_rate(
                stream,
                available_audio_rates([stream_settings["encodec"]]),  # assume encoder, not codec
            )
        elif stream.type == "video" and stream_settings.get("rate", None) is None:
            stream_settings["rate"] = str(suggest_video_rate(stream))

    return filename, streams_settings, container_settings
