#!/usr/bin/env python3

"""Recover the number of frames in a video stream.

This allows not only the characteristics of the files but also the tags if there are any.
"""

import collections
import pathlib
import typing

import cv2  # pip install opencv-contrib-python-headless

from cutcutcodec.core.analysis._helper_properties import _check_pathexists_index, _mix_and_check
from cutcutcodec.core.analysis.ffprobe import (_estimate_len_ffmpeg, _map_index_rel_to_abs,
                                               get_slices_metadata)
from cutcutcodec.core.exceptions import MissingStreamError, MissingInformation


def _count_frames_ffmpeg(filename: str, index: int) -> int:
    """Count the number of frames with the ffmpeg decoder.

    Slow but 100% accurate method.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.nb_frames import _count_frames_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _count_frames_ffmpeg(video, 0)
    294
    >>>
    """
    _, infos = get_slices_metadata(filename, slice_type="frame")
    if index >= len(infos):
        raise MissingInformation(f"'ffmpeg' did not decode '{filename}' stream {index}")
    frames = infos[index].shape[0]
    return frames


def _count_frames_cv2(filename: str, index: int) -> int:
    """Count the number of frames with the cv2 decoder.

    Slow but 100% accurate method.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.nb_frames import _count_frames_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _count_frames_cv2(video, 0)
    294
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")
    frames = 0
    while True:
        if not cap.read()[0]:
            break
        frames += 1
    cap.release()
    if not frames:
        raise MissingStreamError(f"'cv2' did not find any frames '{filename}' stream {index}")
    return frames


def _estimate_frames_cv2(filename: str, index: int) -> int:
    """Extract the number of frames from the metadata.

    Very fast method but inaccurate. It doesn't work all the time.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.nb_frames import _estimate_frames_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_frames_cv2(video, 0)
    296
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    if frames <= 0:  # we saw a case at -553402322211286528
        raise MissingInformation(f"'cv2' does not detect any frame in '{filename}' stream {index}")
    return frames


def get_nb_frames(
    filename: pathlib.Path | str | bytes,
    index: int = 0,
    *,
    backend: typing.Optional[str] = None,
    accurate: bool = False,
) -> int:
    """Recovers the number of frames present in a video stream.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the file containing a video stream.
    index : int
        The relative index of the video stream being considered,
        by default the first stream encountered is selected.
    backend : str, optional
        - None (default) : Try to read the stream by trying differents backends.
        - 'ffmpeg' : Uses the ``ffmpeg`` program in the background.
        - 'cv2' : Uses the module ``pip install opencv-contrib-python-headless``.
    accurate : boolean, optional
        If True, recovers the number of frames by fully decoding all the frames in the video.
        It is very accurate but very slow. If False (default),
        first tries to get the frame count from the file metadata.
        It's not accurate but very fast.

    Returns
    -------
    nbr : int
        The number of readed frames.

    Raises
    ------
    MissingStreamError
        If the file does not contain a playable video stream.
    MissingInformation
        If the information is unavailable.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.nb_frames import get_nb_frames
    >>> from cutcutcodec.utils import get_project_root
    >>> video = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> get_nb_frames(video)
    294
    >>>
    """
    _check_pathexists_index(filename, index)

    return _mix_and_check(
        backend, accurate, (str(pathlib.Path(filename)), index),
        collections.OrderedDict([
            (
                (
                    lambda filename, index: _estimate_len_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video")
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (_estimate_frames_cv2, {"accurate": False, "backend": "cv2"}),
            (
                (
                    lambda filename, index: _count_frames_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video")
                    )
                ),
                {"accurate": True, "backend": "ffmpeg"},
            ),
            (_count_frames_cv2, {"accurate": True, "backend": "cv2"}),
        ])
    )
