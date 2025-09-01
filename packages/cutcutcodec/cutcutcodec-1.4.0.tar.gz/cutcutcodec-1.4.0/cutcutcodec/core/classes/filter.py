#!/usr/bin/env python3

"""It's a node that acts on streams."""

from cutcutcodec.core.classes.container import ContainerInput, ContainerOutput
from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream


class Filter(Node):
    """Filter that applies to several streams.

    A filter can be empty, i.e. have no input and no output streams.
    On the other hand, it cannot have an input stream but no output stream,
    or an output stream but no input stream.
    """

    def __init__(
        self, in_streams: list[Stream] | tuple[Stream], out_streams: list[Stream] | tuple[Stream]
    ):
        Node.__init__(self, in_streams, out_streams)
        assert (
            len(self.in_streams) != 0 or len(self.out_streams) == 0
            or isinstance(self, ContainerInput)
        ), "an effect with no input flow, must have no output flow"
        assert (
            len(self.in_streams) == 0 or len(self.out_streams) != 0
            or isinstance(self, ContainerOutput)
        ), "an effect with at least one input stream, must have at least one output stream"
