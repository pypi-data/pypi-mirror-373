#!/usr/bin/env python3

"""Defines the structure of an abstract multimedia stream."""

from fractions import Fraction
import abc
import numbers


class Stream(abc.ABC):
    """A General multimedia stream.

    Attributes
    ----------
    beginning : Fraction
        The stream beginning instant in second (readonly).
    duration : Fraction or inf
        The duration of the flow in seconds, it can be infinite (readonly).
        This value needs to be accurate.
    index : int
        The absolute stream index from the parent node (0 to n-1) (readonly).
    node : cutcutcodec.core.classes.node.Node
        The node where this stream comes from (readonly).
        Allows back propagation in the assembly graph.
    node_main : cutcutcodec.core.classes.node.Node
        The node used for the compilation. This node has the same output_streams
        as ``node`` but not nescessary the same input_streams and te same properties.
        It can be used for factorisation (read and write).
    """

    def __init__(self, node):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.classes.node.Node
            The node where this stream comes from.
            The audit must be conducted in the children's classes.
            It is not done here in order to avoid cyclic imports.
        node_main : cutcutcodec.core.classes.node.Node
            In the case this streams comes from ``cutcutcodec.core.filter.meta_filter.MetaFilter``,
            `node_main` is the meta filter while `node` is the subgraph of the meta-filter.
        """
        self._node = node
        self._node_main = node

    def __eq__(self, other) -> bool:
        """2 streams are equivalent if there parent nodes are similar."""
        if self.__class__ != other.__class__:
            return False
        if self.index != other.index:
            return False
        if self.node != other.node:
            return False
        return True

    def __or__(self, other):
        """Concatenate self and other in a new node."""
        from cutcutcodec.core.filter.identity import FilterIdentity
        return FilterIdentity([self]) | other

    def __reduce__(self):
        """Allow ``pickle`` to serialize efficiently.

        You can't just use ``__getstate__`` and ``__setstate__``
        because we don't want to duplicate the stream.
        This allows to retrieve the equivalent stream generated in the parent node.
        """
        return Stream._stream_from_parent_node, (self.node, self.index)

    def __getattr__(self, name: str) -> object:
        """If the attribute starts with 'apply_', it is an alias to Node.__getattr__."""

        class StreamFilterCreator:  # pylint: disable=R0903
            """Make the attribute callable."""

            def __init__(self, FilterCreator):
                """Memorize the filter and the streams."""
                self.FilterCreator = FilterCreator

            def __call__(self, *args, **kwargs):
                """Create the stream, see help(self.FilterCreator) for the documentation."""
                return self.FilterCreator(*args, **kwargs).out_streams[0]

        from cutcutcodec.core.filter.identity import FilterIdentity
        if name.startswith("apply_"):
            return StreamFilterCreator(FilterIdentity([self]).__getattr__(name))
        raise AttributeError

    @staticmethod
    def _stream_from_parent_node(node, index):
        """Return the equivalent stream contained in the parent node."""
        return node.out_streams[index]

    @property
    @abc.abstractmethod
    def beginning(self) -> Fraction:
        """Return the stream beginning instant in second."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def duration(self) -> Fraction | float:
        """Return the duration of the flow in seconds, positive fraction or infinite."""
        raise NotImplementedError

    @property
    def index(self) -> int:
        """Return the stream index from the parent node (0 to n-1)."""
        return self._node.out_index(self)

    @property
    def node(self):
        """Return the node where this stream comes from."""
        return self._node

    @property
    def node_main(self):
        """Return the global node, can be an alias to the classic node."""
        return self._node_main

    @node_main.setter
    def node_main(self, new_node):
        """Change the node if this stream is already present in the new node at the same place."""
        for i, stream in enumerate(new_node.out_streams):
            if stream is self:
                if self.index != i:
                    raise AttributeError(
                        f"the index of the stream {self} "
                        f"in the node {self.node} is {self.index}, "
                        f"but it is {i} in the node {new_node}"
                    )
                self._node_main = new_node
                return
        raise AttributeError(f"the stream {self} is not in the node {new_node}")

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """Return the type of stream, 'audio', 'subtitle' or 'video'."""
        raise NotImplementedError


class StreamWrapper(Stream):
    """Allow to dynamically transfer the methods of an instanced stream.

    Attribute
    ---------
    stream : cutcutcodec.core.classes.stream.Stream
        The stream containing the properties to be transferred (readonly).
        This stream is one of the input streams of the parent node.
    """

    def __init__(self, node, index: numbers.Integral):
        """Initialise and create the class.

        Parameters
        ----------
        node : cutcutcodec.core.classes.node.Node
            The parent node, transmitted to ``cutcutcodec.core.classes.stream.Stream``.
        index : number.Integral
            The index of the stream among all the input streams of the ``node``.
            0 for the first, 1 for the second ...
        """
        super().__init__(node)
        assert isinstance(index, numbers.Integral) and index >= 0, index
        assert len(node.in_streams) > index, f"only {len(node.in_streams)} streams, no {index}"
        self._index = int(index)

    @property
    def beginning(self) -> Fraction:
        """Return the stream beginning instant in second."""
        return self.stream.beginning

    @property
    def duration(self) -> Fraction | float:
        """Return the duration of the flow in seconds, positive fraction or infinite."""
        return self.stream.duration

    @property
    def index(self) -> int:
        """Return the stream index from the parent node (0 to n-1)."""
        return self._index

    @property
    def stream(self) -> Stream:
        """Return the audio stream containing the properties to be transferred."""
        return self.node.in_streams[self.index]

    @property
    def type(self) -> str:
        """Implement ``cutcutcodec.core.classes.stream.Stream.type``."""
        return self.stream.type
