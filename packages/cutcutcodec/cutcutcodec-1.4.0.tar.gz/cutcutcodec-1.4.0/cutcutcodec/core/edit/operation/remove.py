#!/usr/bin/env python3

"""Allow to remove elements from the graph by managing collateral damage."""

import typing

import networkx


def remove_edge(
    graph: networkx.MultiDiGraph, edge: tuple[str, str, str]
) -> dict[tuple[str, str, str], None | tuple[str, str, str]]:
    """Delete an edge from the graph.

    Parameters
    ----------
    graph : network.MultiDiGraph
        The assembly graph containing the edge to be deleted.
        The operations on this graph will be performed in-place.
    edge : tuple[str, str, str]
        The name of the edge to delete from the graph (src_node, dst_node, key).

    Returns
    -------
    edges : dict
        Each old edge name is associated with its new name.
        If the new name is None, it means that the edge has been deleted.
        This allows to be informed of all the operations performed.

    Raises
    ------
    KeyError
        If the edge is not in the graph.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.edit.operation.remove import remove_edge
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> with ContainerInputFFMPEG(media) as container:
    ...     tree = ContainerOutput(container.out_streams)
    ...
    >>> graph = tree_to_graph(tree)
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_1', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'),
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->3')]
    >>> pprint(remove_edge(graph, ('container_input_ffmpeg_1', 'container_output_1', '1->1')))
    {('container_input_ffmpeg_1', 'container_output_1', '1->1'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'): ('container_input_ffmpeg_1',
                                                                  'container_output_1',
                                                                  '2->1'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'): ('container_input_ffmpeg_1',
                                                                  'container_output_1',
                                                                  '3->2')}
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_1', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_1', 'container_output_1', '2->1'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->2')]
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(edge, tuple), edge.__class__.__name__
    assert len(edge) == 3, edge
    for name in edge:
        assert isinstance(name, str), name.__class__.__name__
    if not graph.has_edge(*edge):
        raise KeyError(f"the edge {edge} is not in the graph")

    transformations = {edge: None}
    attrs = {}
    ref_index = int(edge[2].split("->")[1])
    for edge_name in graph.in_edges(edge[1], keys=True):
        src, dst, key = edge_name
        if (current_index := int(key.split("->")[1])) <= ref_index:
            continue
        transformations[edge_name] = (src, dst, f"{key.split('->')[0]}->{current_index-1}")
        attrs[transformations[edge_name]] = graph.edges[src, dst, key]
    graph.remove_edges_from(transformations)
    for edge_name, attr in attrs.items():
        graph.add_edge(*edge_name, **attr)

    return transformations


def remove_edges(
    graph: networkx.MultiDiGraph, edges: typing.Iterable[tuple[str, str, str]]
) -> dict[tuple[str, str, str], None | tuple[str, str, str]]:
    """Delete several edges from the graph.

    Parameters
    ----------
    graph : network.MultiDiGraph
        The assembly graph containing the edges to be deleted.
        The operations on this graph will be performed in-place.
    edges : typing.Iterable[tuple[str, str, str]]
        The name of the edges to delete from the graph [(src_node, dst_node, key), ...].

    Returns
    -------
    edges : dict
        Each old edge name is associated with its new name.
        If the new name is None, it means that the edge has been deleted.
        This allows to be informed of all the operations performed.

    Raises
    ------
    KeyError
        If one of the edges is not in the graph.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.edit.operation.remove import remove_edges
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> with ContainerInputFFMPEG(media) as container:
    ...     tree = ContainerOutput(container.out_streams)
    ...
    >>> graph = tree_to_graph(tree)
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_1', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'),
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->3')]
    >>> pprint(remove_edges(
    ...     graph,
    ...     [
    ...         ('container_input_ffmpeg_1', 'container_output_1', '1->1'),
    ...         ('container_input_ffmpeg_1', 'container_output_1', '2->2'),
    ...     ],
    ... ))
    {('container_input_ffmpeg_1', 'container_output_1', '1->1'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'): ('container_input_ffmpeg_1',
                                                                  'container_output_1',
                                                                  '3->1')}
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_1', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->1')]
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(edges, typing.Iterable), edges.__class__.__name__
    edges = list(edges)
    assert all(isinstance(e, tuple) for e in edges), edges
    assert all(len(e) == 3 for e in edges), edges
    for i in range(3):
        assert all(isinstance(e[i], str) for e in edges), edges
    if not all(graph.has_edge(*e) for e in edges):
        raise KeyError(f"one of the edges {edges} is not in the graph")

    inv_trans = {}
    del_list = []
    edges = list(set(edges))  # eliminates redundancies
    while edges:  # as long as there are edges to remove
        local_trans = remove_edge(graph, edges.pop())
        edges = [local_trans.get(e, e) for e in edges]
        for old, new in local_trans.items():
            inv_trans[new] = inv_trans.get(old, old)
            if new is None:
                del_list.append(inv_trans[new])
            if old in inv_trans:  # case renamed for second time
                del inv_trans[old]
    trans = {old: new for new, old in inv_trans.items()} | {el: None for el in del_list}

    return trans


def remove_element(
    graph: networkx.MultiDiGraph, element: str | tuple[str, str, str]
) -> dict[str | tuple[str, str, str], None | tuple[str, str, str]]:
    """Alias to ``cutcutcodec.core.edit.operation.remove.remove_elements``."""
    return remove_elements(graph, [element])


def remove_elements(
    graph: networkx.MultiDiGraph, elements: typing.Iterable[str | tuple[str, str, str]]
) -> dict[str | tuple[str, str, str], None | tuple[str, str, str]]:
    """Delete several nodes or edges from the graph.

    Parameters
    ----------
    graph : network.MultiDiGraph
        The assembly graph containing the nodes and edges to be deleted.
        The operations on this graph will be performed in-place.
    elements : typing.Iterable[str | tuple[str, str, str]]
        The name of nodes and edges to delete from the graph.

    Returns
    -------
    transformations : dict
        Each old edge or node name is associated with its new name.
        If the new name is None, it means that the element has been deleted.
        This allows to be informed of all the operations performed.

    Raises
    ------
    KeyError
        If one of the elements is not in the graph.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.edit.operation.remove import remove_elements
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> with (
    ...     ContainerInputFFMPEG(media) as container_1,
    ...     ContainerInputFFMPEG(media) as container_2,
    ... ):
    ...     tree = ContainerOutput([*container_1.out_streams, *container_2.out_streams])
    ...
    >>> graph = tree_to_graph(tree)
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_1', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'),
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'),
     ('container_input_ffmpeg_2', 'container_output_1', '0->4'),
     ('container_input_ffmpeg_2', 'container_output_1', '1->5'),
     ('container_input_ffmpeg_2', 'container_output_1', '2->6'),
     ('container_input_ffmpeg_2', 'container_output_1', '3->7')]
    >>> pprint(list(graph.nodes))
    ['container_output_1', 'container_input_ffmpeg_1', 'container_input_ffmpeg_2']
    >>> pprint(remove_elements(
    ...     graph,
    ...     ["container_input_ffmpeg_1", ('container_input_ffmpeg_2', 'container_output_1', '1->5')]
    ... ))
    {'container_input_ffmpeg_1': None,
     ('container_input_ffmpeg_1', 'container_output_1', '0->0'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'): None,
     ('container_input_ffmpeg_2', 'container_output_1', '0->4'): ('container_input_ffmpeg_2',
                                                                  'container_output_1',
                                                                  '0->0'),
     ('container_input_ffmpeg_2', 'container_output_1', '1->5'): None,
     ('container_input_ffmpeg_2', 'container_output_1', '2->6'): ('container_input_ffmpeg_2',
                                                                  'container_output_1',
                                                                  '2->1'),
     ('container_input_ffmpeg_2', 'container_output_1', '3->7'): ('container_input_ffmpeg_2',
                                                                  'container_output_1',
                                                                  '3->2')}
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_2', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_2', 'container_output_1', '2->1'),
     ('container_input_ffmpeg_2', 'container_output_1', '3->2')]
    >>> pprint(list(graph.nodes))
    ['container_output_1', 'container_input_ffmpeg_2']
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(elements, typing.Iterable), elements.__class__.__name__
    elements = list(elements)

    # separate nodes and edges
    nodes = [n for n in elements if isinstance(n, str)]
    if not all(n in graph for n in nodes):
        raise KeyError(f"one of the nodes {nodes} is not in the graph")
    edges = [e for e in elements if isinstance(e, tuple)]
    assert len(nodes) + len(edges) == len(elements)

    edges.extend([edge for node in nodes for edge in graph.out_edges(node, keys=True)])
    edges.extend([edge for node in nodes for edge in graph.in_edges(node, keys=True)])
    transformations = remove_edges(graph, edges)
    transformations.update(remove_nodes(graph, nodes))

    return transformations


def remove_node(
    graph: networkx.MultiDiGraph, node: str
) -> dict[str | tuple[str, str, str], None | tuple[str, str, str]]:
    """Delete a node from the graph.

    Also deletes the edges linked to this node.

    Parameters
    ----------
    graph : network.MultiDiGraph
        The assembly graph containing the node to be deleted.
        The operations on this graph will be performed in-place.
    node : str
        The name of the node to delete from the graph.

    Returns
    -------
    transformations : dict
        Each old edge or node name is associated with its new name.
        If the new name is None, it means that the element has been deleted.
        This allows to be informed of all the operations performed.

    Raises
    ------
    KeyError
        If the node is not in the graph.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.edit.operation.remove import remove_node
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> with (
    ...     ContainerInputFFMPEG(media) as container_1,
    ...     ContainerInputFFMPEG(media) as container_2,
    ... ):
    ...     tree = ContainerOutput([*container_1.out_streams, *container_2.out_streams])
    ...
    >>> graph = tree_to_graph(tree)
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_1', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'),
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'),
     ('container_input_ffmpeg_2', 'container_output_1', '0->4'),
     ('container_input_ffmpeg_2', 'container_output_1', '1->5'),
     ('container_input_ffmpeg_2', 'container_output_1', '2->6'),
     ('container_input_ffmpeg_2', 'container_output_1', '3->7')]
    >>> pprint(list(graph.nodes))
    ['container_output_1', 'container_input_ffmpeg_1', 'container_input_ffmpeg_2']
    >>> pprint(remove_node(graph, "container_input_ffmpeg_1"))
    {'container_input_ffmpeg_1': None,
     ('container_input_ffmpeg_1', 'container_output_1', '0->0'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'): None,
     ('container_input_ffmpeg_2', 'container_output_1', '0->4'): ('container_input_ffmpeg_2',
                                                                  'container_output_1',
                                                                  '0->0'),
     ('container_input_ffmpeg_2', 'container_output_1', '1->5'): ('container_input_ffmpeg_2',
                                                                  'container_output_1',
                                                                  '1->1'),
     ('container_input_ffmpeg_2', 'container_output_1', '2->6'): ('container_input_ffmpeg_2',
                                                                  'container_output_1',
                                                                  '2->2'),
     ('container_input_ffmpeg_2', 'container_output_1', '3->7'): ('container_input_ffmpeg_2',
                                                                  'container_output_1',
                                                                  '3->3')}
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_2', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_2', 'container_output_1', '1->1'),
     ('container_input_ffmpeg_2', 'container_output_1', '2->2'),
     ('container_input_ffmpeg_2', 'container_output_1', '3->3')]
    >>> pprint(list(graph.nodes))
    ['container_output_1', 'container_input_ffmpeg_2']
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(node, str), node.__class__.__name__
    if node not in graph:
        raise KeyError(f"the node {node} is not in the graph")

    transformations = {edge: None for edge in graph.in_edges(node, keys=True)}
    graph.remove_edges_from(transformations)
    transformations.update(remove_edges(graph, graph.out_edges(node, keys=True)))
    transformations[node] = None
    graph.remove_node(node)

    return transformations


def remove_nodes(
    graph: networkx.MultiDiGraph, nodes: typing.Iterable[str]
) -> dict[str | tuple[str, str, str], None | tuple[str, str, str]]:
    """Delete several nodes from the graph.

    Parameters
    ----------
    graph : network.MultiDiGraph
        The assembly graph containing the nodes to be deleted.
        The operations on this graph will be performed in-place.
    nodes : typing.Iterable[str]
        The name of the nodes to delete from the graph.

    Returns
    -------
    transformations : dict
        Each old edge or node name is associated with its new name.
        If the new name is None, it means that the element has been deleted.
        This allows to be informed of all the operations performed.

    Raises
    ------
    KeyError
        If one of the nodes is not in the graph.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.edit.operation.remove import remove_nodes
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> with (
    ...     ContainerInputFFMPEG(media) as container_1,
    ...     ContainerInputFFMPEG(media) as container_2,
    ...     ContainerInputFFMPEG(media) as container_3,
    ... ):
    ...     tree = ContainerOutput(
    ...         [*container_1.out_streams, *container_2.out_streams, *container_3.out_streams]
    ...     )
    ...
    >>> graph = tree_to_graph(tree)
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_1', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'),
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'),
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'),
     ('container_input_ffmpeg_2', 'container_output_1', '0->4'),
     ('container_input_ffmpeg_2', 'container_output_1', '1->5'),
     ('container_input_ffmpeg_2', 'container_output_1', '2->6'),
     ('container_input_ffmpeg_2', 'container_output_1', '3->7'),
     ('container_input_ffmpeg_3', 'container_output_1', '0->8'),
     ('container_input_ffmpeg_3', 'container_output_1', '1->9'),
     ('container_input_ffmpeg_3', 'container_output_1', '2->10'),
     ('container_input_ffmpeg_3', 'container_output_1', '3->11')]
    >>> pprint(list(graph.nodes))
    ['container_output_1',
     'container_input_ffmpeg_1',
     'container_input_ffmpeg_2',
     'container_input_ffmpeg_3']
    >>> pprint(remove_nodes(graph, ["container_input_ffmpeg_1", "container_input_ffmpeg_2"]))
    {'container_input_ffmpeg_1': None,
     'container_input_ffmpeg_2': None,
     ('container_input_ffmpeg_1', 'container_output_1', '0->0'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '1->1'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '2->2'): None,
     ('container_input_ffmpeg_1', 'container_output_1', '3->3'): None,
     ('container_input_ffmpeg_2', 'container_output_1', '0->4'): None,
     ('container_input_ffmpeg_2', 'container_output_1', '1->5'): None,
     ('container_input_ffmpeg_2', 'container_output_1', '2->6'): None,
     ('container_input_ffmpeg_2', 'container_output_1', '3->7'): None,
     ('container_input_ffmpeg_3', 'container_output_1', '0->8'): ('container_input_ffmpeg_3',
                                                                  'container_output_1',
                                                                  '0->0'),
     ('container_input_ffmpeg_3', 'container_output_1', '1->9'): ('container_input_ffmpeg_3',
                                                                  'container_output_1',
                                                                  '1->1'),
     ('container_input_ffmpeg_3', 'container_output_1', '2->10'): ('container_input_ffmpeg_3',
                                                                   'container_output_1',
                                                                   '2->2'),
     ('container_input_ffmpeg_3', 'container_output_1', '3->11'): ('container_input_ffmpeg_3',
                                                                   'container_output_1',
                                                                   '3->3')}
    >>> pprint(list(graph.edges))
    [('container_input_ffmpeg_3', 'container_output_1', '0->0'),
     ('container_input_ffmpeg_3', 'container_output_1', '1->1'),
     ('container_input_ffmpeg_3', 'container_output_1', '2->2'),
     ('container_input_ffmpeg_3', 'container_output_1', '3->3')]
    >>> pprint(list(graph.nodes))
    ['container_output_1', 'container_input_ffmpeg_3']
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(nodes, typing.Iterable), nodes.__class__.__name__
    nodes = list(nodes)
    assert all(isinstance(n, str) for n in nodes), nodes
    if not all(n in graph for n in nodes):
        raise KeyError(f"one of the nodes {nodes} is not in the graph")

    transformations = {edge: None for node in nodes for edge in graph.in_edges(node, keys=True)}
    graph.remove_edges_from(transformations)
    edges = {edge for node in nodes for edge in graph.out_edges(node, keys=True)}
    transformations.update(remove_edges(graph, edges))
    transformations.update({node: None for node in nodes})
    graph.remove_nodes_from(set(nodes))

    return transformations
