#!/usr/bin/env python3

"""Allow to temporarily concatenate several audio streams."""

import logging
import math
import typing

from cutcutcodec.core.classes.meta_filter import MetaFilter
from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.filter.audio.add import FilterAudioAdd
from cutcutcodec.core.filter.audio.delay import FilterAudioDelay


class FilterAudioCat(MetaFilter):
    """Concatenate the streams end-to-end.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.audio.cat import FilterAudioCat
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>>
    >>> (s_audio_0,) = FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 0, 10).out_streams
    >>> (s_audio_1,) = GeneratorAudioNoise(.5).out_streams
    >>> (s_chain_audio,) = FilterAudioCat([s_audio_0, s_audio_1]).out_streams
    >>>
    >>> (
    ...     s_chain_audio.snapshot(0, 1, 20) == torch.cat(
    ...         (s_audio_0.snapshot(0, 1, 10), s_audio_1.snapshot(0, 1, 10)), 1
    ...     )
    ... ).all()
    tensor(True)
    >>>
    """

    def _compile(self, in_streams: tuple[Stream]) -> Node:
        streams = [in_streams[0]]  # can not raise IndexError because none empty
        pos = streams[0].beginning + streams[0].duration
        for i, stream in enumerate(in_streams[1:]):
            if pos == math.inf:
                logging.warning("the audio stream %i is infinite, can not chain an other after", i)
                break
            streams.append(FilterAudioDelay([stream], pos-stream.beginning).out_streams[0])
            pos += stream.duration
        return FilterAudioAdd(streams)

    def _getstate(self) -> dict:
        return {}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterAudioCat.__init__(self, in_streams)
