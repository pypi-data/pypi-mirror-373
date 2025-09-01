#!/usr/bin/env python3

"""Backpropagation of the time interval in a node."""

from fractions import Fraction
import math

import networkx

from cutcutcodec.core.analysis.graph.find import find_edge_from_edge_tree
from cutcutcodec.core.analysis.stream.time_backprop import time_backprop as time_backprop_stream
from cutcutcodec.core.compilation.graph_to_tree import update_trees


def time_backprop(
    graph: networkx.MultiDiGraph,
    edge: tuple[str, str, str],
    t_min: Fraction,
    t_max: Fraction | float,
) -> tuple[tuple[str, str, str], tuple[Fraction, Fraction | float]]:
    """Graph version of ``cutcutcodec.core.analysis.stream.time_backprop.time_backprop``.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph. The graph is supposed to be updated.
        It means ``cutcutcodec.core.compilation.graph_to_tree.update_trees`` was called.
    edge : tuple[str, str, str]
        The name of the edge corresponding to the outgoing stream. It can be a stream of any type.
    t_min : Fraction
        The starting included time of decoding the data of the given stream.
    t_max : frctions.Fraction or inf
        The final excluded time of decoding the data of the given stream.

    Yields
    ------
    in_edge : tuple[str, str, str]
        Turn by turn, the input edge of the main node given by the edge in argument.
        If the node is a generator, no edge are yields.
    new_t_min : Fraction
        The start time of this slice matching with the given time slice.
    new_t_max : Fraction or inf
        The final time of this slice matching with the given time slice.
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(edge, tuple), edge.__class__.__name__
    assert len(edge) == 3, edge
    assert all(isinstance(e, str) for e in edge), edge
    assert edge in graph.edges, (edge, graph.edges)
    assert isinstance(t_min, Fraction), t_min.__class__.__name__
    assert t_max == math.inf or isinstance(t_max, Fraction), t_max

    update_trees(graph)
    stream = graph.edges[edge]["cache"][1]["tree"]

    def _time_backprop(stream, t_min, t_max):
        for in_stream, t_min_, t_max_ in time_backprop_stream(stream, t_min, t_max):
            try:
                in_edge = find_edge_from_edge_tree(
                    graph, in_stream, nbunch=graph.in_edges(edge[0], keys=True), pointer=True
                )
            except KeyError:  # case meta filter
                yield from _time_backprop(in_stream, t_min_, t_max_)
            else:
                yield in_edge, t_min_, t_max_

    yield from _time_backprop(stream, t_min, t_max)
