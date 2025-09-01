#!/usr/bin/env python3

"""Ensure the behavor of nan value in timestamp for snapshot is taken in account."""

import math

import numpy as np
import torch

from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream_video import StreamVideo


def test_video_nan():
    """Test nan value on a video stream."""
    class NodeEmpty(Node):
        """Fake Node."""

        _getstate = None
        _setstate = None
        default = None

    class Stream(StreamVideo):
        """Fake Stream."""

        beginning = None
        colorspace = None
        duration = None

    stream = Stream(NodeEmpty([], []))
    assert np.array_equal(
        stream.snapshot(math.nan, (480, 720)).numpy(force=True),
        np.zeros((480, 720, 2), dtype=np.float32),
    )
    assert np.array_equal(
        stream.snapshot(np.nan, (480, 720)).numpy(force=True),
        np.zeros((480, 720, 2), dtype=np.float32),
    )
    assert np.array_equal(
        stream.snapshot(torch.nan, (480, 720)).numpy(force=True),
        np.zeros((480, 720, 2), dtype=np.float32),
    )
