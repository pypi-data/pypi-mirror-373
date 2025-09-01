#!/usr/bin/env python3

"""Smartly choose the framerate of a video stream."""

from fractions import Fraction
import typing

from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG


FPS_ESTIMATORS = {}  # to each node stream class, associate the func to find the optimal rate


def _add_estimator(node_cls: type) -> callable:
    def _add_func(func) -> callable:
        FPS_ESTIMATORS[node_cls] = func
        return func
    return _add_func


@_add_estimator(ContainerInputFFMPEG)
def _optimal_rate_container_input_ffmpeg(stream: StreamVideo) -> Fraction:
    """Detect the rate of a ContainerInputFFMPEG stream.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.stream.rate_video import optimal_rate_video
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> video = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> stream = ContainerInputFFMPEG(video).out_select("video")[0]
    >>> optimal_rate_video(stream)
    Fraction(30000, 1001)
    >>>
    """
    assert isinstance(stream.node, ContainerInputFFMPEG), stream.node.__class__.__name__
    return stream.rate


def optimal_rate_video(
    stream: StreamVideo,
    choices: typing.Optional[set[Fraction]] = None,
) -> Fraction:
    """Find the optimal frame rate for a given video stream.

    Parameters
    ----------
    stream : cutcutcodec.core.classes.stream_video.StreamVideo
        The video stream that we want to find the optimal fps.
    choices : set[Fraction], optional
        The possible fps. If provide, returns the most appropriate fps of this set.

    Returns
    -------
    framerate : numbers.Real
        The framerate (maximum) that allows to minimize / cancel the loss of information,
        (minimum) and avoids an excess of frame that does not bring more information.
    """
    # verifications
    assert isinstance(stream, StreamVideo), stream.__class__.__name__
    if choices is not None:
        assert isinstance(choices, set) and all(isinstance(r, Fraction) and r > 0 for r in choices)

    # optimisation
    if choices and len(choices) == 1:  # case not nescessary to do computing
        return choices.pop()

    # estimation of the best fps
    if (estimator := FPS_ESTIMATORS.get(stream.node.__class__, None)) is not None:
        fps = estimator(stream)
    else:
        fps = max(
            (optimal_rate_video(s) for s in stream.node.in_streams if s.type == "video"),
            default=0,
        )

    # select the most appropriate rate among the choices
    if not choices or not fps:
        return min(choices) if choices else fps
    for choice in sorted(choices):
        if fps <= choice:
            return choice
    return max(choices)
