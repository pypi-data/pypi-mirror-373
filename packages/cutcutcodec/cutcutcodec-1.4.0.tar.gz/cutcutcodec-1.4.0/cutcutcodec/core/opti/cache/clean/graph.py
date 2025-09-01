#!/usr/bin/env python3

"""Allow to delete the obsolete node cache of the graph."""

import itertools

import networkx

from cutcutcodec.core.opti.cache.hashes.graph import compute_graph_items_hash


def clean_graph(graph: networkx.MultiDiGraph) -> networkx.MultiDiGraph:
    """Update inplace the `cache` attribute of each nodes of the graph.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph.

    Returns
    -------
    updated_graph : networkx.MultiDiGraph
        The same graph with the updated `cache` node attribute.
        The underground data are shared, operate in-place.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> from cutcutcodec.core.opti.cache.clean.graph import clean_graph
    >>> container_out = ContainerOutput(
    ...     FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 0, 1).out_streams
    ... )
    >>> graph = tree_to_graph(container_out)
    >>> pprint(dict(clean_graph(graph).nodes("cache")))
    {'container_output_1': ('099c022d457eb220c36ae22a75bf1998', {}),
     'filter_audio_subclip_1': ('10355c7ad764f111b15798bed884a821', {}),
     'generator_audio_noise_1': ('4dc3de85c734bfd23024c381599bfe3f', {})}
    >>> pprint(list(graph.edges(keys=True, data=True)))
    [('filter_audio_subclip_1',
      'container_output_1',
      '0->0',
      {'cache': ('10355c7ad764f111b15798bed884a821|0', {})}),
     ('generator_audio_noise_1',
      'filter_audio_subclip_1',
      '0->0',
      {'cache': ('4dc3de85c734bfd23024c381599bfe3f|0', {})})]
    >>> for _, data in graph.nodes(data=True):
    ...     data["cache"][1]["key"] = "value"
    ...
    >>> for *_, data in graph.edges(keys=True, data=True):
    ...     data["cache"][1]["key"] = "value"
    ...
    >>> graph.nodes["filter_audio_subclip_1"]["state"]["duration_max"] = "2"
    >>> pprint(dict(clean_graph(graph).nodes("cache")))
    {'container_output_1': ('8978fa1dc585c4d400fb36ad711ba95f', {}),
     'filter_audio_subclip_1': ('0c5c8e9591d25413c94a4251a3a14444', {}),
     'generator_audio_noise_1': ('4dc3de85c734bfd23024c381599bfe3f',
                                 {'key': 'value'})}
    >>> pprint(list(graph.edges(keys=True, data=True)))
    [('filter_audio_subclip_1',
      'container_output_1',
      '0->0',
      {'cache': ('0c5c8e9591d25413c94a4251a3a14444|0', {})}),
     ('generator_audio_noise_1',
      'filter_audio_subclip_1',
      '0->0',
      {'cache': ('4dc3de85c734bfd23024c381599bfe3f|0', {'key': 'value'})})]
    >>>
    """
    new_hashes = compute_graph_items_hash(graph)  # assertions are done here
    edges_iter = (((s, d, k), data) for s, d, k, data in graph.edges(keys=True, data=True))
    for item, data in itertools.chain(graph.nodes(data=True), edges_iter):
        new_hash = new_hashes[item]
        if "cache" not in data or data["cache"][0] != new_hash:
            data["cache"] = (new_hashes[item], {})
    return graph
