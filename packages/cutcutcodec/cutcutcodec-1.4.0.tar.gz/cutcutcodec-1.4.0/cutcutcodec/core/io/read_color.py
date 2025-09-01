#!/usr/bin/env python3

"""Delegate the reading to the module read_ffmpeg, and add a filter to manage the colorspace."""

import typing

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.filter.identity import FilterIdentity
from cutcutcodec.core.filter.video.colorspace import FilterVideoColorspace


def filter_video_colorspace(
    container: Node, colorspace: typing.Optional[Colorspace | str] = None
) -> FilterIdentity:
    """Apply FilterVideoColorspace for the video streams only."""
    assert isinstance(container, Node), container.__class__.__name__
    streams = []
    for stream in container.out_streams:
        if stream.type == "video":
            try:
                alpha = stream.has_alpha
            except AttributeError:
                alpha = False
            streams.append(FilterVideoColorspace([stream], colorspace, alpha).out_streams[0])
        else:
            streams.append(stream)
    return FilterIdentity(streams)
