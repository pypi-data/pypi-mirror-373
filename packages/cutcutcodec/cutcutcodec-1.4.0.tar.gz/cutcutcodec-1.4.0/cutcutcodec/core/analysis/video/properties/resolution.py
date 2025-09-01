#!/usr/bin/env python3

"""Find frame shape of a video stream."""

import collections
import pathlib
import typing

import cv2  # pip install opencv-contrib-python-headless

from cutcutcodec.core.analysis._helper_properties import _check_pathexists_index, _mix_and_check
from cutcutcodec.core.analysis.ffprobe import _estimate_resolution_ffmpeg, _map_index_rel_to_abs
from cutcutcodec.core.exceptions import MissingStreamError, MissingInformation


def _estimate_resolution_cv2(filename: str, index: int) -> tuple[int, int]:
    """Retrieve via cv2, the metadata concerning the resolution.

    This function is fast because it reads only the header of the file.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.resolution import _estimate_resolution_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> media = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_resolution_cv2(media, 0)
    (720, 1280)
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")
    try:
        shape = (
            round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        )
    except TypeError as err:
        raise MissingInformation(
            f"'cv2' failed to find the resolution of '{filename}' stream {index}"
        ) from err
    return shape


def get_resolution(
    filename: pathlib.Path | str | bytes,
    index: int = 0,
    *,
    backend: typing.Optional[str] = None
) -> tuple[int, int]:
    """Read in the metadata, the display video resolution.

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
    height, width : int
        The number of diplay pixel of the frames of the video stream.

    Raises
    ------
    MissingStreamError
        If the file does not contain a playable video stream.
    MissingInformation
        If the information is unavailable.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.resolution import get_resolution
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> get_resolution(media)
    (720, 1280)
    >>>
    """
    _check_pathexists_index(filename, index)

    return _mix_and_check(
        backend, False, (str(pathlib.Path(filename)), index),
        collections.OrderedDict([
            (
                (
                    lambda filename, index: _estimate_resolution_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video")
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (_estimate_resolution_cv2, {"accurate": False, "backend": "cv2"}),
        ])
    )
