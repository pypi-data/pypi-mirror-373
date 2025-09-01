#!/usr/bin/env python3

"""Help for deserialisation of a json representation of an assembly graph."""

import importlib
import inspect
import re

import networkx

from cutcutcodec.core.classes.node import Node


def _string_to_node_cls(string: str) -> Node:
    """Convert node string representation in Node class.

    Bijection with ``cutcutcodec.core.compilation.graph_to_json._node_cls_to_string`` function.

    Parameters
    ----------
    string : str
        The relative import path of the class.

    Returns
    -------
    cls : type
        The cutcutcodec.core.classes.node.Node subclass associate to the string.

    Examples
    --------
    >>> from cutcutcodec.core.compilation.json_to_graph import _string_to_node_cls
    >>> _string_to_node_cls('classes.node.Node')
    <class 'cutcutcodec.core.classes.node.Node'>
    >>>
    """
    assert isinstance(string, str), string.__class__.__name__
    mod = importlib.import_module("cutcutcodec.core." + ".".join(string.split(".")[:-1]))
    node_cls = dict(inspect.getmembers(mod))[string.split(".")[-1]]
    return node_cls


def json_to_graph(json_graph: dict[str]) -> networkx.MultiDiGraph:
    """Create the graph from a json dictionary.

    Reverse operation with ``cutcutcodec.core.compilation.graph_to_json.graph_to_json`` function.

    Parameters
    ----------
    json_graph : dict[str]
        The complete representation of the graph.

    Returns
    -------
    assembly_graph : networkx.MultiDiGraph
        The strictly equivalent assembly graph.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.compilation.json_to_graph import json_to_graph
    >>> json_graph = {
    ...     'edges': [['generator_audio_noise_1', 'container_output_1', '0->0']],
    ...     'nodes': {
    ...         'container_output_1': {
    ...             'class': 'classes.container.ContainerOutput',
    ...             'state': {},
    ...         },
    ...         'generator_audio_noise_1': {
    ...             'class': 'generation.audio.noise.GeneratorAudioNoise',
    ...             'display': {'position': [0, 0]},
    ...             'state': {'seed': 0.0},
    ...         },
    ...     },
    ... }
    >>> graph = json_to_graph(json_graph)
    >>> pprint(sorted(graph.nodes))
    ['container_output_1', 'generator_audio_noise_1']
    >>> pprint(sorted(graph.edges))
    [('generator_audio_noise_1', 'container_output_1', '0->0')]
    >>> pprint(graph.nodes["container_output_1"])
    {'class': <class 'cutcutcodec.core.classes.container.ContainerOutput'>,
     'state': {}}
    >>> pprint(graph.nodes["generator_audio_noise_1"])
    {'class': <class 'cutcutcodec.core.generation.audio.noise.GeneratorAudioNoise'>,
     'display': {'position': [0, 0]},
     'state': {'seed': 0.0}}
    >>>
    """
    assert isinstance(json_graph, dict), json_graph.__class__.__name__
    assert all(isinstance(key, str) for key in json_graph), json_graph
    assert json_graph.keys() == {"edges", "nodes"}, set(json_graph)
    assert isinstance(json_graph["edges"], list), json_graph["edges"].__class__.__name__
    assert isinstance(json_graph["nodes"], dict), json_graph["nodes"].__class__.__name__

    graph = networkx.MultiDiGraph(title="assembly graph")
    for node, data in json_graph["nodes"].items():
        assert isinstance(node, str), (node, node.__class__.__name__)
        assert isinstance(data, dict), (node, data)
        assert {"class", "state"}.issubset(data), (node, data)  # issubset(dict) <=> issubset(set)
        data["class"] = _string_to_node_cls(data["class"])
        graph.add_node(node, **data)
    for edge in json_graph["edges"]:
        assert isinstance(edge, list), (edge, edge.__class__.__name__)
        assert len(edge) == 3, edge
        src, dst, key = edge
        assert isinstance(src, str), (edge, src, src.__class__.__name__)
        assert isinstance(dst, str), (edge, dst, dst.__class__.__name__)
        assert src in json_graph["nodes"], (edge, src, sorted(json_graph["nodes"]))
        assert dst in json_graph["nodes"], (edge, dst, sorted(json_graph["nodes"]))
        assert isinstance(key, str), (edge, key, key.__class__.__name__)
        assert re.fullmatch(r"\d+->\d+", key), (edge, key)
        graph.add_edge(src, dst, key)

    return graph
