#!/usr/bin/env python3

"""Find the average frame rate of a video stream.

This information is collected in the metadata of the file.
Its access is fast but its value is not always accurate.
Especially since the framerate is not always constant within the same stream.
"""

from fractions import Fraction
import collections
import pathlib
import typing

import cv2  # pip install opencv-contrib-python-headless

from cutcutcodec.core.analysis._helper_properties import _check_pathexists_index, _mix_and_check
from cutcutcodec.core.analysis.ffprobe import _estimate_rate_ffmpeg, _map_index_rel_to_abs
from cutcutcodec.core.exceptions import MissingStreamError, MissingInformation


def _estimate_rate_cv2(filename: str, index: int) -> Fraction:
    """Retrieve via cv2, the metadata concerning the fps.

    This function is fast because it reads only the header of the file.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.rate import _estimate_rate_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_rate_cv2(video, 0)
    Fraction(30000, 1001)
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")
    fps = Fraction(cap.get(cv2.CAP_PROP_FPS)).limit_denominator(1001)
    cap.release()
    if fps <= 0:
        raise MissingInformation(f"'cv2' finds an fps of {fps} in '{filename}' stream {index}")
    return fps


def get_rate_video(
    filename: pathlib.Path | str | bytes,
    index: int = 0,
    *,
    backend: typing.Optional[str] = None
) -> Fraction:
    """Read in the metadata, the average frequency of the frames.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the file containing a video stream.
    index : int
        The relative index of the video stream being considered,
        by default the first stream encountered is selected.
    backend : str, optional
        - None (default) : Try to read the stream by trying differents backends.
        - 'ffmpeg' : Uses the modules ``pip install ffmpeg-python``
            which are using the ``ffmpeg`` program in the background.
        - 'cv2' : Uses the module ``pip install opencv-contrib-python-headless``.

    Returns
    -------
    fps : Fraction
        The average frequency of the frames in Hz.

    Raises
    ------
    MissingStreamError
        If the file does not contain a playable video stream.
    MissingInformation
        If the information is unavailable.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.rate import get_rate_video
    >>> from cutcutcodec.utils import get_project_root
    >>> video = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> get_rate_video(video)
    Fraction(30000, 1001)
    >>>
    """
    _check_pathexists_index(filename, index)

    return _mix_and_check(
        backend, False, (str(pathlib.Path(filename)), index),
        collections.OrderedDict([
            (
                (
                    lambda filename, index: _estimate_rate_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video")
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (_estimate_rate_cv2, {"accurate": False, "backend": "cv2"}),
        ])
    )
