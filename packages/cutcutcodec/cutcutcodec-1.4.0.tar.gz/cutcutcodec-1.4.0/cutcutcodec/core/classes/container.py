#!/usr/bin/env python3

"""Defines the entry and exit points of the assembly graph."""

import typing

from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream


class ContainerInput(Node):
    """Entry point of an assembly graph."""

    def __init__(self, out_streams: typing.Iterable[Stream]):
        super().__init__((), out_streams)
        assert len(self.out_streams) != 0, "at least one flow must leave in the input container"


class ContainerOutput(Node):
    """Coming back point of an assembly graph."""

    def __init__(self, in_streams: typing.Iterable[Stream]):
        super().__init__(in_streams, ())
        assert len(self.in_streams) != 0, "at least one flow must arrive in the output container"

    def _getstate(self) -> dict:
        return {}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}, state
        ContainerOutput.__init__(self, in_streams)

    def write(self):
        """Run the complete assembly graph and exploite the last streams."""
        raise NotImplementedError
