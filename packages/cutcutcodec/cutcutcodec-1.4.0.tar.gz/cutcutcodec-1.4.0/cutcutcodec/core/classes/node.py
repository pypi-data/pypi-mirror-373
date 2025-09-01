#!/usr/bin/env python3

"""General node of the assembly graph."""

import abc
import importlib
import typing

from cutcutcodec.core.classes.stream import Stream


class Node(abc.ABC):
    """General node of the assembly graph.

    Parameters
    ----------
    copy : boolean, default=True
        If False, try to avoid realocation as much as possible.
        By default, the modifications are not inplace (readonly).
    in_streams : tuple[Stream, ...]
        The streams arriving on the node (readonly).
    out_streams : tuple[Stream, ...]
        The streams coming back on the node (readonly).
    """

    def __init__(
        self,
        in_streams: list[Stream] | tuple[Stream],
        out_streams: list[Stream] | tuple[Stream],
    ):
        assert isinstance(in_streams, (list, tuple)), in_streams.__class__.__name__
        in_streams = tuple(in_streams)
        assert all(isinstance(stream, Stream) for stream in in_streams), \
            [stream.__class__.__name__ for stream in in_streams]
        assert isinstance(out_streams, (list, tuple)), out_streams.__class__.__name__
        out_streams = tuple(out_streams)
        assert all(isinstance(stream, Stream) for stream in out_streams), \
            [stream.__class__.__name__ for stream in out_streams]
        self._in_streams = in_streams
        self._out_streams = out_streams
        self._copy = getattr(self, "_copy", True)

    def __eq__(self, other) -> bool:
        """Check that 2 nodes are equivalent."""
        if self.__class__ != other.__class__:
            return False
        if self.getstate() != other.getstate():
            return False
        if self.in_streams != other.in_streams:
            return False  # not compare out_streams to avoide infinite loop
        return True

    def __enter__(self) -> typing.Self:
        """To allow context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        for stream in self.in_streams:
            stream.node.__exit__(exc_type, exc_val, exc_tb)

    def __getattr__(self, name: str) -> object:
        """Automates filter import to simplify graph creation syntax."""

        class FilterCreator:  # pylint: disable=R0903
            """Make the attribute callable."""

            def __init__(self, streams, Filter):
                """Memorize the filter and the streams."""
                self.streams = streams
                self.Filter = Filter

            def __call__(self, *args, **kwargs):
                """Create the filter, see help(self.Filter) for the documentation."""
                return self.Filter(self.streams, *args, **kwargs)

        if name.startswith("apply_"):  # apply a filter
            parts = name.split("_")[1:]
            try:
                mod = importlib.import_module(".".join(["cutcutcodec", "core", "filter"] + parts))
            except ModuleNotFoundError as err:
                raise AttributeError(f"failed to import the filter module {name}") from err
            try:
                Filter = getattr(mod, f"Filter{''.join(p.title() for p in parts)}")
            except AttributeError as err:
                raise AttributeError(f"failed to import the filter class {name}") from err
            return FilterCreator(self.out_streams, Filter)
        raise AttributeError

    def __getstate__(self) -> tuple[typing.Iterable[Stream], dict]:
        """Allow ``pickle`` to serialize efficiently."""
        return self.in_streams, self.getstate()

    def __or__(self, other):
        """Create a FilterIdentity containing the streams of self and other."""
        from cutcutcodec.core.filter.identity import FilterIdentity
        if isinstance(other, Node):
            return FilterIdentity(self.out_streams + other.out_streams)
        if isinstance(other, Stream):
            return FilterIdentity(self.out_streams + (other,))
        return NotImplemented

    def __setstate__(self, streams_state) -> None:
        """Allow ``pickle`` to recreate the object identically.

        Parameters
        ----------
        streams_state : tuple[typing.Iterable[cutcutcodec.core.classes.stream.Stream], dict]
            These are the input streams and the other arguments.
        """
        assert isinstance(streams_state, tuple), streams_state.__class__.__name__
        assert len(streams_state) == 2, streams_state
        in_streams, state = streams_state
        self.setstate(in_streams, state)

    @abc.abstractmethod
    def _getstate(self) -> dict:
        """Help for ``cutcutcodec.core.classes.node.Node.getstate``."""
        raise NotImplementedError

    @abc.abstractmethod
    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        """Help for ``cutcutcodec.core.classes.node.Node.setstate``."""
        raise NotImplementedError

    @property
    def copy(self) -> bool:
        """Try to avoid realocation as much as possible if False."""
        return self._copy

    def getstate(self) -> dict:
        """Retrieve the internal state of the object.

        Returns
        -------
        state : dict
            An explicit dictionary containing the different attributes of the object.
            Even if this is not optimal in terms of memory and speed,
            the objects must be explicit so that they can be easily manipulated
            when the assembly graph is optimized.
            The keys must be of type str and the dictionary must to be jsonisable.
        """
        state = self._getstate()
        if self._copy is False:
            state.update({"copy": False})
        return state

    def in_index(self, stream: Stream) -> int:
        """Return the input index of the stream comming on this node."""
        indexs = [index for index, stream_ in enumerate(self._in_streams) if stream_ is stream]
        if len(indexs) != 1:
            raise AttributeError(f"the stream {stream} doesn't comme into the node {self}")
        return indexs.pop()

    def in_select(self, type_: str) -> tuple[Stream, ...]:
        """Select the incoming streams of a specific type."""
        assert isinstance(type_, str), type_.__class__.__name__
        return tuple(s for s in self._in_streams if s.type == type_)

    @property
    def in_streams(self) -> tuple[Stream, ...]:
        """Return the incoming streams on the node."""
        return self._in_streams

    def out_index(self, stream: Stream) -> int:
        """Return the output index of the stream escaping this node."""
        indexs = [index for index, stream_ in enumerate(self._out_streams) if stream_ is stream]
        if len(indexs) != 1:
            raise AttributeError(f"the stream {stream} doesn't leave from the node {self}")
        return indexs.pop()

    def out_select(self, type_: str) -> tuple[Stream, ...]:
        """Select the outgoing streams of a specific type."""
        assert isinstance(type_, str), type_.__class__.__name__
        return tuple(s for s in self._out_streams if s.type == type_)

    @property
    def out_streams(self) -> tuple[Stream, ...]:
        """Return the outgoing streams on the node."""
        return self._out_streams

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        """Allow to completely change the internal state of the node.

        Parameters
        ----------
        in_streams
            Same as ``cutcutcodec.core.classes.stream.Stream.in_streams``.
        state : dict
            The internal state returned by the ``getstate`` method of the same class.
        """
        state = state.copy()
        if (copy := state.pop("copy", None)) is not None:
            self._copy = copy
        self._setstate(in_streams, state)
