#!/usr/bin/env python3

"""Optimize the assembly graph."""

import networkx


def optimize(graph: networkx.MultiDiGraph) -> networkx.MultiDiGraph:
    """Optimize the graph in order to improve the exportation speed.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The brut assembly graph, not yet optimizated.
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    return graph
