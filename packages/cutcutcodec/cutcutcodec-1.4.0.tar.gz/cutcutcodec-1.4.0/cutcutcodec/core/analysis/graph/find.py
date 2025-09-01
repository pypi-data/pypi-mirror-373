#!/usr/bin/env python3

"""Allow to search for elements in the graph."""

import typing

import networkx

from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.compilation.graph_to_tree import update_trees


def find_edge_from_edge_tree(
    graph: networkx.MultiDiGraph,
    stream: Stream,
    nbunch: typing.Optional[typing.Iterable[tuple[str, str, str]]] = None,
    pointer: bool = False,
) -> tuple[str, str, str]:
    """Search in the graph for the edge that corresponds to the stream provided.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph.
    stream : :py:class:`cutcutcodec.core.classes.stream.Stream`
        One of the output stream of the node. It can be a stream of any type.
    nbunch : typing.Iterable[tuple[str, str, str]], optional
        The edges to be analyzed. By default all edges are analyzed.
    pointer : boolean
        If True, returns only if the node stream is the same objet as the provide stream.
        If False (default), compare the streams contents. It is slower but stronger.

    Returns
    -------
    edge : tuple[str, str, str]
        The name of the corresponding edge.

    Raises
    ------
    KeyError
        If no edge matches.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.graph.find import find_edge_from_edge_tree
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> container_out = ContainerOutput(
    ...     FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 1, 2).out_streams
    ... )
    >>> graph = tree_to_graph(container_out)
    >>> find_edge_from_edge_tree(graph, container_out.in_streams[0])
    ('filter_audio_subclip_1', 'container_output_1', '0->0')
    >>>
    """
    # verifications
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(stream, Stream), stream.__class__.__name__
    if nbunch is not None:
        assert isinstance(nbunch, typing.Iterable), nbunch.__class__.__name__
        nbunch = set(nbunch)
        assert all(
            isinstance(e, tuple) and len(e) == 3 and all(isinstance(k, str) for k in e)
            for e in nbunch
        ), nbunch

    update_trees(graph)

    # search the right edge
    for src, dst, key, cache in graph.edges(data="cache", keys=True):
        if nbunch is not None and (src, dst, key) not in nbunch:
            continue
        tree = cache[1]["tree"]
        if pointer:
            if stream is tree:
                return (src, dst, key)
        else:
            if stream == tree:
                return (src, dst, key)
    raise KeyError(f"{stream} not founded in the graph")
