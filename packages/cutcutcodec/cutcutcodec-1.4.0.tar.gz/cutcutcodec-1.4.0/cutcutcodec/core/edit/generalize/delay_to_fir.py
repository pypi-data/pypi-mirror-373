#!/usr/bin/env python3

"""Convert a filter delay into a convlolution."""

from fractions import Fraction

import networkx
import torch

from cutcutcodec.core.compilation.graph_to_tree import update_trees
from cutcutcodec.core.compilation.tree_to_graph import _node_name_base
from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
from cutcutcodec.core.filter.audio.fir import FilterAudioFIR
from cutcutcodec.core.opti.utils import node_selector


def _criteria(graph: networkx.MultiDiGraph, node: str) -> bool:
    """Return True if the node can be converted."""
    data = graph.nodes[node]
    if not issubclass(data["class"], FilterAudioDelay):
        return False
    if Fraction(data["state"]["delay"]) < 0:
        return False
    if len(in_edges := list(graph.in_edges(node, keys=True))) != 1:
        return False
    in_edge = in_edges.pop()
    update_trees(graph)
    stream = graph.edges[in_edge]["cache"][1]["tree"]
    if stream.type != "audio":
        return False
    return True


@node_selector(_criteria)
def delay_to_fir(graph: networkx.MultiDiGraph, *, node: str):
    """Replace the properties of the delay node by the properties of a conv node.

    Works only for audio streams.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.edit.generalize.delay_to_fir import delay_to_fir
    >>> from cutcutcodec.core.filter.audio.delay import FilterAudioDelay
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> out = ContainerOutput(FilterAudioDelay(GeneratorAudioNoise(0).out_streams, 1).out_streams)
    >>> graph = tree_to_graph(out)
    >>>
    >>> pprint(dict(graph.nodes("state")))
    {'container_output_1': {},
     'filter_audio_delay_1': {'delay': '1'},
     'generator_audio_noise_1': {'layout': 'stereo', 'seed': 0.0}}
    >>> pprint(list(graph.edges))
    [('filter_audio_delay_1', 'container_output_1', '0->0'),
     ('generator_audio_noise_1', 'filter_audio_delay_1', '0->0')]
    >>> delay_to_fir(graph)
    >>> pprint(dict(graph.nodes("state")))  # doctest: +ELLIPSIS
    {'container_output_1': {},
     'filter_audio_fir_1': {'fir_encoded': 'XQAAAAT//////////wAAb/3//6O3/0c+SBVyOWFRuJIo5qOGB/n...',
                            'fir_rate': 48000},
     'generator_audio_noise_1': {'layout': 'stereo', 'seed': 0.0}}
    >>> pprint(list(graph.edges))
    [('generator_audio_noise_1', 'filter_audio_fir_1', '0->0'),
     ('filter_audio_fir_1', 'container_output_1', '0->0')]
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__
    assert isinstance(node, str), node.__class__.__name__
    assert node in graph
    assert _criteria(graph, node)  # useless because of the decorator

    # name_cut = _node_name_base(graph, FilterCut.__name__)
    name_fir = _node_name_base(graph, FilterAudioFIR.__name__)

    delay = Fraction(graph.nodes[node]["state"]["delay"])

    networkx.relabel_nodes(graph, {node: name_fir}, copy=False)
    graph.nodes[name_fir]["class"] = FilterAudioFIR
    rate = 48000
    fir = torch.zeros(round(delay*rate)+1, dtype=torch.float16)
    fir[-1] = 1.0
    graph.nodes[name_fir]["state"] = (
        {"fir_encoded": FilterAudioFIR.encode_fir(fir), "fir_rate": rate}
    )
    # the filter cut has to be appened
