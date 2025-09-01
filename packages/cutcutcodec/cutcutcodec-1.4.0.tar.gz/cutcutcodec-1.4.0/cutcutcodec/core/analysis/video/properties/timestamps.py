#!/usr/bin/env python3

"""Recover the date of all the frames that make up a video stream.

This information is more accurate than the simple ``fps``
but it takes much longer to retrieve since it requires decoding the entire file.
"""

from fractions import Fraction
import collections
import pathlib
import typing

import cv2  # pip install opencv-contrib-python-headless
import numpy as np

from cutcutcodec.core.analysis._helper_properties import _check_pathexists_index, _mix_and_check
from cutcutcodec.core.analysis.ffprobe import _decode_timestamps_ffmpeg, _map_index_rel_to_abs
from cutcutcodec.core.exceptions import MissingStreamError


def _decode_timestamps_cv2(filename: str, index: int) -> np.ndarray[None | Fraction]:
    """Retrieve from cv2 the position of the frames in the video.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.timestamps import _decode_timestamps_cv2
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _decode_timestamps_cv2(video, 0)  # doctest: +ELLIPSIS
    array([Fraction(0, 1), Fraction(33, 1000), Fraction(67, 1000),
           Fraction(1, 10), Fraction(133, 1000), Fraction(167, 1000),
           Fraction(1, 5), Fraction(117, 500), Fraction(267, 1000),
           ...
           Fraction(951, 100), Fraction(9543, 1000), Fraction(1197, 125),
           Fraction(961, 100), Fraction(9643, 1000), Fraction(2419, 250),
           Fraction(971, 100), Fraction(9743, 1000), Fraction(1222, 125)],
          dtype=object)
    >>>
    """
    cap = cv2.VideoCapture(filename, index)
    if not cap.isOpened():
        raise MissingStreamError(f"impossible to open '{filename}' stream {index} with 'cv2'")

    pos_list = []

    while True:
        if not cap.read()[0]:
            break
        pos_curr = cap.get(cv2.CAP_PROP_POS_MSEC)
        if pos_curr == 0.0 and pos_list:
            pos_list.append(None)
        else:
            pos_list.append(Fraction(round(pos_curr), 1000))
    cap.release()

    if not pos_list:
        raise MissingStreamError(f"'cv2' does not detect any frame in '{filename}' stream {index}")
    if np.all(np.equal(pos_list, None)):
        raise MissingStreamError(
            f"'cv2' is unable to locate the frames of '{filename}' stream {index}"
        )

    return np.array(pos_list, dtype=object)


def _interpolate(
    sequence: np.ndarray[typing.Optional[Fraction]]
) -> np.ndarray[None | Fraction]:
    """Interpolates a numpy vector to replace the None with a consistent value.

    The interpolation is a linear interpolation based on the least squares.

    Parameters
    ----------
    sequence : np.ndarray[typing.Optional[Fraction]]
        The 1d vector containing None.

    Returns
    -------
    interp : np.ndarray[None | Fraction]
        The input vector with the nan replaced by there interpolated value.

    Notes
    -----
    Modifies inplace the values of the array, does not make a copy.

    Examples
    --------
    >>> from fractions import Fraction
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.properties.timestamps import _interpolate
    >>> _interpolate(np.array([Fraction(0), None, Fraction(1)]))
    array([Fraction(0, 1), Fraction(1, 2), Fraction(1, 1)], dtype=object)
    >>> _interpolate(np.array([None, Fraction(1, 2), Fraction(1)]))
    array([Fraction(0, 1), Fraction(1, 2), Fraction(1, 1)], dtype=object)
    >>> _interpolate(np.array([Fraction(0), Fraction(1, 2), None]))
    array([Fraction(0, 1), Fraction(1, 2), Fraction(1, 1)], dtype=object)
    >>>
    """
    assert isinstance(sequence, np.ndarray)
    assert sequence.ndim == 1

    nans = np.equal(sequence, None)
    not_nans = ~nans
    grade, mean = np.polyfit(
        np.arange(len(sequence))[not_nans], sequence[not_nans].astype(float), deg=1
    )
    new_vals = mean + grade*np.arange(len(sequence))[nans]
    new_vals = np.vectorize(lambda v: Fraction(v).limit_denominator(1001))(new_vals)
    sequence[nans] = new_vals
    return sequence


def get_timestamps_video(
    filename: pathlib.Path | str | bytes,
    index: int = 0,
    *,
    backend: typing.Optional[str] = None,
    interpolate: bool = True
) -> np.ndarray[None | Fraction]:
    """Recover the date of appearance of the frames.

    In case the frame rate is perfectly constant, this returns
    ``[0, 1/fps, 2/fps, ..., (n-1)/fps]`` with n the number of frames present in the video.
    But in case the frequency of images is not quite constant, this function has more interest.

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
    interpolate : bool, optional
        If True (default), then the frames whose position is unknown
        are interpolated from the set of correctly dated frames.
        If False, the unconfirmed positions are translated as 'np.nan'.

    Returns
    -------
    dates : Fraction or None
        The numpy 1d list containing the dates in seconds, encoded in Fraction.
        If a position is unknown and interpolate is set to False, the values None are used.

    Raises
    ------
    MissingStreamError
        If the file does not contain a playable video stream.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.video.properties.timestamps import get_timestamps_video
    >>> from cutcutcodec.utils import get_project_root
    >>> video = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> get_timestamps_video(video)  # doctest: +ELLIPSIS
    array([Fraction(0, 1), Fraction(33, 1000), Fraction(67, 1000),
           Fraction(1, 10), Fraction(133, 1000), Fraction(167, 1000),
           Fraction(1, 5), Fraction(117, 500), Fraction(267, 1000),
           ...
           Fraction(961, 100), Fraction(9643, 1000), Fraction(2419, 250),
           Fraction(971, 100), Fraction(9743, 1000), Fraction(1222, 125)],
          dtype=object)
    >>>
    """
    _check_pathexists_index(filename, index)
    assert isinstance(interpolate, bool), interpolate.__class__.__name__

    timestamps = _mix_and_check(
        backend, True, (str(pathlib.Path(filename)), index),
        collections.OrderedDict([
            (
                (
                    lambda filename, index: _decode_timestamps_ffmpeg(
                        filename, _map_index_rel_to_abs(filename, index, "video")
                    )
                ),
                {"accurate": True, "backend": "ffmpeg"},
            ),
            (_decode_timestamps_cv2, {"accurate": True, "backend": "cv2"}),
        ])
    )

    if interpolate and None in timestamps:
        return _interpolate(timestamps)
    return timestamps
