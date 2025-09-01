#!/usr/bin/env python3

"""Backpropagation of the time interval in a node."""

from fractions import Fraction
import math

from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.filter.audio.add import FilterAudioAdd
from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
from cutcutcodec.core.filter.video.add import FilterVideoAdd
from cutcutcodec.core.filter.video.delay import FilterVideoDelay


SLICE_ESTIMATORS = {}  # to each node stream class, associate the func to find the time translation


def _add_estimator(node_cls: type) -> callable:
    def _add_func(func) -> callable:
        SLICE_ESTIMATORS[node_cls] = func
        return func
    return _add_func


@_add_estimator(FilterAudioAdd)
def _slice_filter_audio_add(
    stream: Stream, t_min: Fraction, t_max: Fraction | float
) -> tuple[Stream, tuple[Fraction, Fraction | float]]:
    """Detect the time propagation into a FilterAudioAdd stream.

    Examples
    --------
    >>> from fractions import Fraction
    >>> from cutcutcodec.core.analysis.stream.time_backprop import time_backprop
    >>> from cutcutcodec.core.filter.audio.add import FilterAudioAdd
    >>> from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>>
    >>> (s_audio_0,) = GeneratorAudioNoise(0).out_streams
    >>> (s_audio_1,) = FilterAudioDelay(GeneratorAudioNoise(0).out_streams, 10).out_streams
    >>> (s_add_audio,) = FilterAudioAdd([s_audio_0, s_audio_1]).out_streams
    >>>
    >>> for _, t_min, t_max in time_backprop(s_add_audio, Fraction(5), Fraction(15)):
    ...     t_min, t_max
    ...
    (Fraction(5, 1), Fraction(15, 1))
    (Fraction(10, 1), Fraction(15, 1))
    >>>
    """
    assert isinstance(stream.node, FilterAudioAdd), stream.node.__class__.__name__
    for in_stream in stream.node.in_streams:
        new_t_min = max(in_stream.beginning, t_min)
        new_t_max = min(in_stream.beginning+in_stream.duration, t_max)
        yield in_stream, new_t_min, new_t_max


@_add_estimator(FilterVideoAdd)
def _slice_filter_video_add(
    stream: Stream, t_min: Fraction, t_max: Fraction | float
) -> tuple[Stream, tuple[Fraction, Fraction | float]]:
    """Detect the time propagation into a FilterVideoAdd stream.

    Examples
    --------
    >>> from fractions import Fraction
    >>> from cutcutcodec.core.analysis.stream.time_backprop import time_backprop
    >>> from cutcutcodec.core.filter.video.add import FilterVideoAdd
    >>> from cutcutcodec.core.filter.video.delay import FilterVideoDelay
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_video_0,) = GeneratorVideoNoise(0).out_streams
    >>> (s_video_1,) = FilterVideoDelay(GeneratorVideoNoise(0).out_streams, 10).out_streams
    >>> (s_add_video,) = FilterVideoAdd([s_video_0, s_video_1]).out_streams
    >>>
    >>> for _, t_min, t_max in time_backprop(s_add_video, Fraction(5), Fraction(15)):
    ...     t_min, t_max
    ...
    (Fraction(5, 1), Fraction(15, 1))
    (Fraction(10, 1), Fraction(15, 1))
    >>>
    """
    assert isinstance(stream.node, FilterVideoAdd), stream.node.__class__.__name__
    for in_stream in stream.node.in_streams:
        new_t_min = max(in_stream.beginning, t_min)
        new_t_max = min(in_stream.beginning+in_stream.duration, t_max)
        yield in_stream, new_t_min, new_t_max


@_add_estimator(FilterAudioDelay)
def _slice_filter_audio_delay(
    stream: Stream, t_min: Fraction, t_max: Fraction | float
) -> tuple[Stream, tuple[Fraction, Fraction | float]]:
    """Detect the time propagation into a FilterAudioDelay stream.

    Examples
    --------
    >>> from fractions import Fraction
    >>> from cutcutcodec.core.analysis.stream.time_backprop import time_backprop
    >>> from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> stream = GeneratorAudioNoise().out_streams[0]
    >>> (s_a,) = FilterAudioDelay([stream], 10).out_streams
    >>> ((stream, t_min, t_max),) = time_backprop(s_a, Fraction(20), Fraction(40))
    >>> stream.type
    'audio'
    >>> t_min
    Fraction(10, 1)
    >>> t_max
    Fraction(30, 1)
    >>>
    """
    assert isinstance(stream.node, FilterAudioDelay), stream.node.__class__.__name__
    node = stream.node
    yield node.in_streams[stream.index], t_min-node.delay, t_max-node.delay


@_add_estimator(FilterVideoDelay)
def _slice_filter_video_delay(
    stream: Stream, t_min: Fraction, t_max: Fraction | float
) -> tuple[Stream, tuple[Fraction, Fraction | float]]:
    """Detect the time propagation into a FilterVideoDelay stream.

    Examples
    --------
    >>> from fractions import Fraction
    >>> from cutcutcodec.core.analysis.stream.time_backprop import time_backprop
    >>> from cutcutcodec.core.filter.video.delay import FilterVideoDelay
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>> stream = GeneratorVideoNoise().out_streams[0]
    >>> (s_v,) = FilterVideoDelay([stream], 10).out_streams
    >>> ((stream, t_min, t_max),) = time_backprop(s_v, Fraction(20), Fraction(40))
    >>> stream.type
    'video'
    >>> t_min
    Fraction(10, 1)
    >>> t_max
    Fraction(30, 1)
    >>>
    """
    assert isinstance(stream.node, FilterVideoDelay), stream.node.__class__.__name__
    node = stream.node
    yield node.in_streams[stream.index], t_min-node.delay, t_max-node.delay


def time_backprop(
    stream: Stream, t_min: Fraction, t_max: Fraction | float
) -> tuple[Stream, tuple[Fraction, Fraction | float]]:
    """Match the time slice to the input streams of a node.

    Helper for ``cutcutcodec.core.compilation.export.time_slice.time_backprop``.

    Parameters
    ----------
    stream : cutcutcodec.core.classes.stream.Stream
        One of the output stream of the node. It can be a stream of any type.
    t_min : Fraction
        The starting included time of decoding the data of the given stream.
    t_max : Fraction or inf
        The final excluded time of decoding the data of the given stream.

    Yields
    ------
    in_stream : cutcutcodec.core.classes.stream.Stream
        Turn by turn, the input stream of the node given by the stream in argument.
        If the node is a generator, no stream are yields.
    new_t_min : Fraction
        The start time of this slice matching with the given time slice.
    new_t_max : Fraction or inf
        The final time of this slice matching with the given time slice.
    """
    assert isinstance(stream, Stream), stream.__class__.__name__
    assert isinstance(t_min, Fraction), t_min.__class__.__name__
    assert t_max == math.inf or isinstance(t_max, Fraction), t_max

    if (estimator := SLICE_ESTIMATORS.get(stream.node.__class__, None)) is not None:
        for in_stream, t_min_, t_max_ in estimator(stream, t_min, t_max):
            if t_min_ < t_max_:
                yield in_stream, t_min_, t_max_
    else:
        if t_min < t_max:
            for in_stream in stream.node.in_streams:
                yield in_stream, t_min, t_max
