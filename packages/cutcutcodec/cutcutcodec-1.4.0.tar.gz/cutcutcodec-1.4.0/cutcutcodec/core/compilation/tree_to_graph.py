#!/usr/bin/env python3

"""Create the graph from an ``cutcutcodec.core.classes.node.Node``."""

import re

import networkx

from cutcutcodec.core.classes.node import Node


def _complete_graph(graph: networkx.MultiDiGraph, node: Node, *, _names: dict) -> None:
    """Add to the graph, all nodes and arcs from the provided node.

    This function is recursive.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The graph on which we add the node.
    node : cutcutcodec.core.classes.node.Node
        The node to add to the graph.

    Notes
    -----
    The graph is modified inplace.
    """
    if id(node) in _names:
        if _names[id(node)] in graph:
            return None

    current_node_name = _node_name(graph, node, _names=_names)
    graph.add_node(current_node_name, **{"class": node.__class__, "state": node.getstate()})

    for index_dst, stream in enumerate(node.in_streams):
        new_node_name = _node_name(graph, stream.node_main, _names=_names)
        _complete_graph(graph, stream.node_main, _names=_names)
        graph.add_edge(new_node_name, current_node_name, f"{stream.index}->{index_dst}")

    return None


def _node_name(graph: networkx.MultiDiGraph, node: Node, *, _names: dict) -> str:
    """Find a nice new name to identify the new node in the graph.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The graph in which we want to add this new node.
    node : cutcutcodec.core.classes.node.Node
        The node that we want to name.

    Returns
    -------
    name : str
        A new name not yet used in the graph.
    """
    if (name := _names.get(id(node), None)) is not None:
        return name
    name = _node_name_base(graph, node.__class__.__name__)
    _names[id(node)] = name
    return name


def _node_name_base(graph: networkx.MultiDiGraph, node_cls_name: str) -> str:
    """Help for `_node_name`."""
    base = re.sub(r"(?!^)([A-Z]+)", r"_\1", node_cls_name).lower()  # camel to snake
    indexs = {int(n.split("_")[-1]) for n in graph.nodes if re.fullmatch(fr"{base}_\d+", n)}
    for index in range(1, len(indexs)+2):
        if index not in indexs:
            return f"{base}_{index}"
    raise RuntimeError


def new_node(graph: networkx.MultiDiGraph, node: Node) -> tuple[str, dict[str]]:
    """Compiles a node in an existing assembly graph context.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The graph on which we add the node.
    node : cutcutcodec.core.classes.node.Node
        The node that we want to name and extract properties.

    Returns
    -------
    name : str
        The name of the node, this name is not already present in the graph.
    attrs : dict[str]
        The attributes, the state of the node allowing to complete the graph.

    Notes
    -----
    The graph remains unchanged, it is only used for analysis.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph, new_node
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> node = GeneratorAudioNoise(0)
    >>> graph = tree_to_graph(ContainerOutput(node.out_streams))
    >>> pprint(new_node(graph, node))
    ('generator_audio_noise_2',
     {'class': <class 'cutcutcodec.core.generation.audio.noise.GeneratorAudioNoise'>,
      'state': {'layout': 'stereo', 'seed': 0.0}})
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(node, Node), node.__class__.__name__

    name = _node_name(graph, node, _names={})
    attrs = {"class": node.__class__, "state": node.getstate()}

    return name, attrs


def tree_to_graph(container_out: Node) -> networkx.MultiDiGraph:
    """Create the graph from an implicit dynamic tree.

    The generated assembly graph abstracts and simplifies the modification of the pipeline.
    Gives a representation of the assembly tree in the form of a manipulable graph.

    Parameters
    ----------
    container_out : cutcutcodec.core.classes.node.Node
        The output of the dynamic graph.

    Returns
    -------
    assembly_graph : networkx.MultiDiGraph
        The strictly equivalent assembly graph.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.filter.audio.cat import FilterAudioCat
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>>
    >>> (s_audio_0,) = FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 1, 2).out_streams
    >>> (s_audio_1,) = GeneratorAudioNoise(.5).out_streams
    >>> (s_chain_audio,) = FilterAudioCat([s_audio_0, s_audio_1]).out_streams
    >>> graph = tree_to_graph(ContainerOutput([s_chain_audio]))
    >>>
    >>> pprint(sorted(graph.nodes))
    ['container_output_1',
     'filter_audio_cat_1',
     'filter_audio_subclip_1',
     'generator_audio_noise_1',
     'generator_audio_noise_2']
    >>> pprint(sorted(graph.edges))
    [('filter_audio_cat_1', 'container_output_1', '0->0'),
     ('filter_audio_subclip_1', 'filter_audio_cat_1', '0->0'),
     ('generator_audio_noise_1', 'filter_audio_subclip_1', '0->0'),
     ('generator_audio_noise_2', 'filter_audio_cat_1', '0->1')]
    >>>
    """
    assert isinstance(container_out, Node), container_out.__class__.__name__

    graph = networkx.MultiDiGraph(title="assembly graph")
    _complete_graph(graph, container_out, _names={})

    return graph
