#!/usr/bin/env python3

"""Allow to append elements from the graph by managing collateral damage."""

import networkx


def add_edge(
    graph: networkx.MultiDiGraph, node_src: str, node_dst: str, index: int
) -> tuple[str, str, str]:
    """Add a stream to the graph.

    Parameters
    ----------
    graph : network.MultiDiGraph
        The assembly graph which does not yet contain the edge to be added.
        The operations on this graph will be performed in-place.
    node_src : str
        The name of the starting node, must be present in the graph.
    node_dst : str
        The name of the arriving node, must be present in the graph.
    index : int
        The index of the output stream of the node ``node_src``.

    Returns
    -------
    edge : tuple[str, str, str]
        The name of the edge added to the graph.

    Raises
    ------
    KeyError
        If one of the nodes is not in the graph.
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(node_src, str), node_src.__class__.__name__
    assert isinstance(node_dst, str), node_dst.__class__.__name__
    if node_src not in graph or node_dst not in graph:
        raise KeyError(f"the node {node_src} or {node_dst} is not in the graph")

    key = f"{index}->{graph.in_degree(node_dst)}"
    edge = (node_src, node_dst, key)
    graph.add_edge(*edge)

    return edge


def add_node(graph: networkx.MultiDiGraph, node: str, attrs: dict[str]) -> None:
    """Add a node to the graph.

    The parameters can be compute by ``cutcutcodec.core.compilation.tree_to_graph.new_node``.

    Parameters
    ----------
    graph : network.MultiDiGraph
        The assembly graph which does not yet contain the node to be added.
        The operations on this graph will be performed in-place.
    node : str
        The name of the node to add. It must be new.
    attrs : dict[str]
        The new node attributes.

    Raises
    ------
    KeyError
        If the node is in the graph.
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(node, str), node.__class__.__name__
    if node in graph:
        raise KeyError(f"the node {node} is already in the graph")

    graph.add_node(node, **attrs)
