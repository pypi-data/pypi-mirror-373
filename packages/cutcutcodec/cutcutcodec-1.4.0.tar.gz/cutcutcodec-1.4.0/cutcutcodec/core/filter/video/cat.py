#!/usr/bin/env python3

"""Allow to temporarily concatenate several video streams."""

import logging
import math
import typing

from cutcutcodec.core.classes.meta_filter import MetaFilter
from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.filter.video.add import FilterVideoAdd
from cutcutcodec.core.filter.video.delay import FilterVideoDelay


class FilterVideoCat(MetaFilter):
    """Concatenate the streams end-to-end.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.video.cat import FilterVideoCat
    >>> from cutcutcodec.core.filter.video.subclip import FilterVideoSubclip
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_video_0,) = FilterVideoSubclip(GeneratorVideoNoise(0).out_streams, 0, 10).out_streams
    >>> (s_video_1,) = GeneratorVideoNoise(.5).out_streams
    >>> (s_chain_video,) = FilterVideoCat([s_video_0, s_video_1]).out_streams
    >>>
    >>> (s_video_0.snapshot(0, (2, 2)) == s_chain_video.snapshot(0, (2, 2))).all()
    tensor(True)
    >>> (s_video_1.snapshot(0, (2, 2)) == s_chain_video.snapshot(10, (2, 2))).all()
    tensor(True)
    >>> (s_video_1.snapshot(10, (2, 2)) == s_chain_video.snapshot(20, (2, 2))).all()
    tensor(True)
    >>>
    """

    def _compile(self, in_streams: tuple[Stream]) -> Node:
        streams = [in_streams[0]]  # can not raise IndexError because not empty
        pos = streams[0].beginning + streams[0].duration
        for i, stream in enumerate(in_streams[1:]):
            if pos == math.inf:
                logging.warning("the stream video %i is infinite, can not chain an other after", i)
                break
            streams.append(FilterVideoDelay([stream], pos-stream.beginning).out_streams[0])
            pos += stream.duration
        return FilterVideoAdd(streams)

    def _getstate(self) -> dict:
        return {}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterVideoCat.__init__(self, in_streams)
