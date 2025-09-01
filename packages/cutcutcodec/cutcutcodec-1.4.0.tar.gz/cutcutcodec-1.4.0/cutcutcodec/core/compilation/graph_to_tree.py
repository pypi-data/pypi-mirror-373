#!/usr/bin/env python3

"""Compile an assembly graph into an evaluable tree."""

import typing

import networkx

from cutcutcodec.core.classes.container import ContainerOutput
from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.opti.cache.clean.graph import clean_graph


def _tree_from_node(node_name: str, graph: networkx.MultiDiGraph) -> None:
    """Recursively retrieve the node corresponding to the node of the graph.

    Complete the ``tree`` attribute for this node and for the out streams of this node.
    This function is recursive, so all ancestors are also completed.

    Parameters
    ----------
    node_name : str
        The name of the node that allows to determine the corresponding subgraph.
    graph : networkx.MultiDiGraph
        The complete assembly graph.

    Notes
    -----
    If the node is a terminal node, it is the complete dynamic tree.
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(node_name, str), node_name.__class__.__name__
    assert node_name in graph.nodes, sorted(graph.nodes)

    # create node and recursively the parent nodes
    node = graph.nodes[node_name]
    if "tree" not in node["cache"][1]:
        for pred in graph.predecessors(node_name):
            _tree_from_node(pred, graph)  # editing by pointer
        in_edges = graph.in_edges(node_name, keys=True)
        if sorted(int(k.split("->")[1]) for _, _, k in in_edges) != list(range(len(in_edges))):
            raise IndexError(
                f"the streams ({in_edges}) arriving on {node_name} are not correctly incremented"
            )
        in_streams = [
            graph.edges[edge_name]["cache"][1]["tree"] for edge_name in
            sorted(in_edges, key=lambda src_dst_key: int(src_dst_key[2].split("->")[1]))
        ]  # the streams that arrive on the current node
        node["cache"][1]["tree"] = new_node(node["class"], in_streams, node["state"])
        assert node["cache"][1]["tree"].in_streams == tuple(in_streams), \
            f"the node {node_name} does not have the specified input streams"

    # complete out streams
    for out_edge_name in graph.out_edges(node_name, keys=True):
        out_edge = graph.edges[out_edge_name]
        if "tree" not in out_edge["cache"][1]:
            index = int(out_edge_name[2].split("->")[0])
            assert index < len(node["cache"][1]["tree"].out_streams), (
                f"the {out_edge_name[0]} node has only {len(node['cache'][1]['tree'].out_streams)} "
                f"output streams, impossible to access stream index {index}"
            )
            out_edge["cache"][1]["tree"] = node["cache"][1]["tree"].out_streams[index]


def graph_to_tree(graph: networkx.MultiDiGraph) -> ContainerOutput:
    """Create the dynamic tree from the assembly graph.

    The abstract dynamic tree alows the evaluation of the complete pipeline.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph.

    Returns
    -------
    container_out : cutcutcodec.core.classes.container.ContainerOutput
        An evaluable multimedia muxer.

    Examples
    --------
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.graph_to_tree import graph_to_tree
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> tree = tree_to_graph(ContainerOutput(GeneratorAudioNoise(0).out_streams))
    >>> graph_to_tree(tree)  # doctest: +ELLIPSIS
    <cutcutcodec.core.classes.container.ContainerOutput object at ...>
    >>>
    """
    # verification and extraction of the termination node
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    out_nodes = [n for n in graph.nodes if issubclass(graph.nodes[n]["class"], ContainerOutput)]
    assert len(out_nodes) == 1, f"only one output node is possible, not {len(out_nodes)}"
    out_node = out_nodes.pop()
    assert issubclass(graph.nodes[out_node]["class"], ContainerOutput), \
        graph.nodes[out_node]["class"].__name__

    # fill
    update_trees(graph)  # compute and add missing "tree" nodes
    container_out = graph.nodes[out_node]["cache"][1]["tree"]
    return container_out


def new_node(node_class: type, in_streams: typing.Iterable[Stream], state: dict) -> Node:
    """Instantiate and initialize a new node.

    Parameters
    ----------
    node_class : type
        The uninstantiated class describing the node to be created.
        This class must be inherited from the ``cutcutcodec.core.classes.node.Node`` class.
    in_streams : typing.Iterable[Stream]
        See ``cutcutcodec.core.classes.node.Node.setstate``.
    state : dict
        See ``cutcutcodec.core.classes.node.Node.setstate``.

    Returns
    -------
    node : Node
        A new instantiated and initialized node.
    """
    assert isinstance(node_class, type), f"{node_class} must be a class, not an object"
    assert issubclass(node_class, Node), f"{node_class.__name__} class does not inherit from Node"

    node = node_class.__new__(node_class)
    node.setstate(in_streams, state)
    return node


def update_trees(graph: networkx.MultiDiGraph) -> None:
    """Update on each node the ``tree`` attribute.

    From the assembly graph, this function reconstructs the dynamic instances
    and is able to perform the calculations.
    By adding to each node the attribute ``tree``,
    it allows not only to keep the graph structure but also
    to recalculate only the parts that need to be changed.

    The operation are applies in-place.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph who is going to have the updated ``tree`` attributes.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.graph_to_tree import update_trees
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> container_out = ContainerOutput(
    ...     FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 1, 2).out_streams
    ... )
    >>> graph = tree_to_graph(container_out)
    >>> update_trees(graph)
    >>> pprint(dict(graph.nodes("cache")))  # doctest: +ELLIPSIS
    {'container_output_1': ('b1c67b749185174850a2d5cdce2bcb82',
                            {'tree': <cutcutcodec.core.classes.container.ContainerOutput...>}),
     'filter_audio_subclip_1': ('ab86b53fe424b58e755eac50d87a77f0',
                                {'tree': <...FilterAudioSubclip...>}),
     'generator_audio_noise_1': ('4dc3de85c734bfd23024c381599bfe3f',
                                 {'tree': <...GeneratorAudioNoise...>})}
    >>> pprint(list(graph.edges(keys=True, data=True)))  # doctest: +ELLIPSIS
    [('filter_audio_subclip_1',
      'container_output_1',
      '0->0',
      {'cache': ('ab86b53fe424b58e755eac50d87a77f0|0',
                 {'tree': <cutcutcodec.core.filter.audio.cut._StreamAudioCut...>})}),
     ('generator_audio_noise_1',
      'filter_audio_subclip_1',
      '0->0',
      {'cache': ('4dc3de85c734bfd23024c381599bfe3f|0',
                 {'tree': <cutcutcodec.core.generation.audio.noise._StreamAudioNoiseUniform...>})})]
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__

    # delete obsolete cache and create field ["cache"][1]
    graph = clean_graph(graph)

    # complete graph
    out_nodes = [node for node in graph.nodes if graph.out_degree(node) == 0]
    assert out_nodes, "the graph is empty or contains cycle"
    for node_name in out_nodes:
        _tree_from_node(node_name, graph)
