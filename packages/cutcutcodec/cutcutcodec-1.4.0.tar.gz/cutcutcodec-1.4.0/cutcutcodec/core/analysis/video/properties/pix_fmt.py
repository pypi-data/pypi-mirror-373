#!/usr/bin/env python3

"""Find pixel format of a video stream."""

import collections
import pathlib
import typing

import cv2  # pip install opencv-contrib-python-headless

from cutcutcodec.core.analysis._helper_properties import _check_pathexists_index, _mix_and_check
from cutcutcodec.core.analysis.ffprobe import _estimate_pix_fmt_ffmpeg, _map_index_rel_to_abs
from cutcutcodec.core.exceptions import MissingStreamError, MissingInformation


def _estimate_pix_fmt_cv2(filename: str, index: int) -> tuple[int, int]:
    """Retrieve via cv2, the metadata concerning the pixel format.

    This function is fast because it reads only the header of the file.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.pix_fmt import _estimate_pix_fmt_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> media = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_pix_fmt_cv2(media, 0)
    'yuv420'
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")
    if (code := cap.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT)) == -1.0:
        raise MissingInformation(
            f"'cv2' did not find the pixel format of '{filename}' stream {index}"
        )
    PIXEL_FORMAT_MAP = {
        134230855.0: "gbrp",
        168440665.0: "yuv422p10le",
        168506201.0: "yuv420p10le",
        808596553.0: "yuv420",
    }
    if code not in PIXEL_FORMAT_MAP:
        raise MissingInformation(
            f"the 'cv2' pixel format code {code} is unknown '{filename}' stream {index}"
        )
    return PIXEL_FORMAT_MAP[code]


def get_pix_fmt(
    filename: pathlib.Path | str | bytes,
    index: int = 0,
    *,
    backend: typing.Optional[str] = None
) -> str:
    """Read in the metadata, the pixel format.

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
    pix_fmt : int
        The name of the pixel format.

    Raises
    ------
    MissingStreamError
        If the file does not contain a playable video stream.
    MissingInformation
        If the information is unavailable.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.pix_fmt import get_pix_fmt
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> get_pix_fmt(media)
    'yuv420p'
    >>>
    """
    _check_pathexists_index(filename, index)

    return _mix_and_check(
        backend, False, (str(pathlib.Path(filename)), index),
        collections.OrderedDict([
            (
                (
                    lambda filename, index: _estimate_pix_fmt_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video")
                    )
                ),
                {"accurate": False, "backend": "ffmpeg"},
            ),
            (_estimate_pix_fmt_cv2, {"accurate": False, "backend": "cv2"}),
        ])
    )
