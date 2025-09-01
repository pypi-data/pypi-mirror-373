#!/usr/bin/env python3

"""Find the duration of an audio stream.

This allows not only the characteristics of the files but also the tags if there are any.
"""

from fractions import Fraction
import collections
import pathlib

from cutcutcodec.core.analysis._helper_properties import _check_pathexists_index, _mix_and_check
from cutcutcodec.core.analysis.ffprobe import (_decode_duration_ffmpeg, _estimate_duration_ffmpeg,
                                               _map_index_rel_to_abs)


def get_duration_audio(
    filename: pathlib.Path | str | bytes,
    index: int = 0,
    *,
    accurate: bool = False,
) -> Fraction:
    """Recovers the total duration of an audio stream.

    The duration includes the display time o the last frame.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the file containing an audio stream.
    index : int
        The relative index of the audio stream being considered,
        by default the first audio stream encountered is selected.
    accurate : boolean, optional
        If True, recovers the duration by fully decoding all the frames in the audio.
        It is very accurate but very slow. If False (default),
        first tries to get the duration from the file metadata.
        It's not accurate but very fast.

    Returns
    -------
    duration : Fraction
        The total duration of the considerated audio stream.

    Raises
    ------
    MissingStreamError
        If the file does not contain a playable audio stream.
    MissingInformation
        If the information is unavailable.
    """
    _check_pathexists_index(filename, index)

    return _mix_and_check(
        "ffmpeg", accurate, (str(pathlib.Path(filename)), index),
        collections.OrderedDict([
            (
                (
                    lambda filename, index: _estimate_duration_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "audio")
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (
                (
                    lambda filename, index: _decode_duration_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "audio"), accurate=False
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (
                (
                    lambda filename, index: _decode_duration_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "audio"), accurate=True
                    )
                ),
                {"accurate": True, "backend": "ffmpeg"},
            ),
        ])
    )
