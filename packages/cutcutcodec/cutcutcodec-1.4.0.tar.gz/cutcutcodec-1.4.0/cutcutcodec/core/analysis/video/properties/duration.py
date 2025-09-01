#!/usr/bin/env python3

"""Find the duration of a video stream.

This allows not only the characteristics of the files but also the tags if there are any.
"""

from fractions import Fraction
import collections
import pathlib
import typing

import cv2  # pip install opencv-contrib-python-headless

from cutcutcodec.core.analysis._helper_properties import _check_pathexists_index, _mix_and_check
from cutcutcodec.core.analysis.ffprobe import (_decode_duration_ffmpeg, _estimate_duration_ffmpeg,
                                               _map_index_rel_to_abs)
from cutcutcodec.core.exceptions import MissingStreamError, MissingInformation


def _decode_duration_cv2(filename: str, index: int) -> Fraction:
    """Extract the duration by the complete decoding of the stream.

    Slow but 100% accurate method.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.duration import _decode_duration_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _decode_duration_cv2(video, 0)
    Fraction(294281, 30000)
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")
    if (fps := Fraction(cap.get(cv2.CAP_PROP_FPS)).limit_denominator(1001)) <= 0:
        one_over_fps = 0
    else:
        one_over_fps = 1 / fps
    duration = Fraction(0)
    while True:
        duration = (
            Fraction(round(cap.get(cv2.CAP_PROP_POS_MSEC))) / 1000
            or duration + one_over_fps
        )
        if not cap.read()[0]:
            break
    cap.release()
    if not duration:
        raise MissingStreamError(f"'cv2' did not find duration '{filename}' stream {index}")
    return duration + one_over_fps


def _estimate_duration_cv2(filename: str, index: int) -> Fraction:
    """Extract the duration from the metadata.

    Very fast method but inaccurate. It doesn't work all the time.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.duration import _estimate_duration_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_duration_cv2(video, 0)
    Fraction(37037, 3750)
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")
    frames = round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = Fraction(cap.get(cv2.CAP_PROP_FPS)).limit_denominator(1001)
    duration = frames / fps if fps and frames else 0
    cap.release()
    if duration <= 0:
        raise MissingInformation(
            f"'cv2' does not detect any duration in '{filename}' stream {index}"
        )
    return duration


def get_duration_video(
    filename: pathlib.Path | str | bytes,
    index: int = 0,
    *,
    backend: typing.Optional[str] = None,
    accurate: bool = False,
) -> Fraction:
    """Recovers the total duration of a video stream.

    The duration includes the display time o the last frame.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the file containing a video stream.
    index : int
        The relative index of the video stream being considered,
        by default the first video stream encountered is selected.
    backend : str, optional
        - None (default) : Try to read the stream by trying differents backends.
        - 'ffmpeg' : Uses the ``ffmpeg`` program in the background.
        - 'cv2' : Uses the module ``pip install opencv-contrib-python-headless``.
    accurate : boolean, default=False
        If True, recovers the duration by fully decoding all the frames in the video.
        It is very accurate but very slow. If False (default),
        first tries to get the duration from the file metadata.
        It's not accurate but very fast.

    Returns
    -------
    duration : Fraction
        The total duration of the considerated video stream.

    Raises
    ------
    MissingStreamError
        If the file does not contain a playable video stream.
    MissingInformation
        If the information is unavailable.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.duration import get_duration_video
    >>> from cutcutcodec.utils import get_project_root
    >>> video = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> get_duration_video(video)
    Fraction(9809, 1000)
    >>>
    """
    _check_pathexists_index(filename, index)

    return _mix_and_check(
        backend, accurate, (str(pathlib.Path(filename)), index),
        collections.OrderedDict([
            (
                (
                    lambda filename, index: _estimate_duration_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video")
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (
                (
                    lambda filename, index: _decode_duration_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video"), accurate=False
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (_estimate_duration_cv2, {"accurate": False, "backend": "cv2"}),
            (
                (
                    lambda filename, index: _decode_duration_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video"), accurate=True
                    )
                ),
                {"accurate": True, "backend": "ffmpeg"},
            ),
            (_decode_duration_cv2, {"accurate": True, "backend": "cv2"}),
        ])
    )
