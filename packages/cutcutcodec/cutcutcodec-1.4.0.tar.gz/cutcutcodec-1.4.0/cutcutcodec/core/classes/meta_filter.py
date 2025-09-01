#!/usr/bin/env python3

"""It's an effect that combine several effects."""

import abc
import typing

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream


class MetaFilter(Filter):
    """A filter that combine several filters, a sub-graph."""

    def __init__(self, in_streams: typing.Iterable[Stream]):
        super().__init__(in_streams, in_streams)
        if not self.in_streams:
            self.subgraph = self
        else:
            self.subgraph = self._compile(self.in_streams)
            assert isinstance(self.subgraph, Node), self.subgraph.__class__.__name__
            super().__init__(self.in_streams, self.subgraph.out_streams)
        for out_stream in self.out_streams:
            out_stream.node_main = self

    @abc.abstractmethod
    def _compile(self, in_streams: tuple[Stream]) -> Node:
        """Create and returns the sub graph.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            The none empty list of the ordered input streams.

        Return
        ------
        node : cutcutcodec.core.classes.node.Node
            The final node used as itself.
        """
        raise NotImplementedError
