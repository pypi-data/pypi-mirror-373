#!/usr/bin/env python3

"""Ensures that the methods and attributes of abstract classes are well defined."""

import pytest

from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo


def test_node_getstate():
    """Make sure the ``getstate`` method is abstract."""

    class _Node(Node):
        _setstate = None

    class _NodeOk(_Node):
        _getstate = None

    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class _Node",
    ):
        _Node([], [])  # pylint: disable=E0110
    _NodeOk([], [])


def test_node_setstate():
    """Make sure the ``getstate`` method is abstract."""

    class _Node(Node):
        _getstate = None

    class _NodeOk(_Node):
        _setstate = None

    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class _Node",
    ):
        _Node([], [])  # pylint: disable=E0110
    _NodeOk([], [])


def test_stream_beginning():
    """Make sure the ``duration`` method is abstract."""

    class _Node(Node):
        _getstate = None
        _setstate = None

    class _Stream(Stream):
        duration = None
        type = None

    class _StreamOk(_Stream):
        beginning = None

    node = _Node([], [])
    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class _Stream",
    ):
        _Stream(node)  # pylint: disable=E0110
    _StreamOk(node)


def test_stream_colorspace():
    """Make sure the ``colorspace`` method is abstract."""

    class _Node(Node):
        _getstate = None
        _setstate = None

    class _Stream(StreamVideo):
        beginning = None
        duration = None
        type = None

    class _StreamOk(_Stream):
        colorspace = None

    node = _Node([], [])
    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class _Stream",
    ):
        _Stream(node)  # pylint: disable=E0110
    _StreamOk(node)


def test_stream_duration():
    """Make sure the ``duration`` method is abstract."""

    class _Node(Node):
        _getstate = None
        _setstate = None

    class _Stream(Stream):
        beginning = None
        type = None

    class _StreamOk(_Stream):
        duration = None

    node = _Node([], [])
    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class _Stream",
    ):
        _Stream(node)  # pylint: disable=E0110
    _StreamOk(node)


def test_stream_type():
    """Make sure the ``type`` method is abstract."""

    class _Node(Node):
        _getstate = None
        _setstate = None

    class _Stream(Stream):
        beginning = None
        duration = None

    class _StreamOk(_Stream):
        type = None

    node = _Node([], [])
    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class _Stream",
    ):
        _Stream(node)  # pylint: disable=E0110
    _StreamOk(node)
