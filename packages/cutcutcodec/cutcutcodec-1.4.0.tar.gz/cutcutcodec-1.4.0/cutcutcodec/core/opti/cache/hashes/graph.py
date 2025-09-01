#!/usr/bin/env python3

"""Allow to summarize the state of each node of the graph.

This allows a finer management of the cache by a fine tracking of the unchanged elements.
"""

import hashlib

import networkx


def compute_graph_items_hash(graph: networkx.MultiDiGraph) -> dict[str | tuple[str, str, str], str]:
    """Compute a signature for each node and edge, which reflects its state in the graph.

    This is mean to detecting a change of attributes in one of the upstream elements.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph.

    Returns
    -------
    hashes : dict[str | tuple[str, str, str], str]
        To each node and edge name, associate its state as a string.

    Notes
    -----
    The graph must not contain any cycles because the function would never returns.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.classes.container import ContainerOutput
    >>> from cutcutcodec.core.compilation.tree_to_graph import tree_to_graph
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> from cutcutcodec.core.opti.cache.hashes.graph import compute_graph_items_hash
    >>> container_out = ContainerOutput(
    ...     FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 0, 1).out_streams
    ... )
    >>> graph = tree_to_graph(container_out)
    >>> pprint(compute_graph_items_hash(graph))  # doctest: +ELLIPSIS
    {'container_output_1': '099c022d457eb220c36ae22a75bf1998',
     'filter_audio_subclip_1': '10355c7ad764f111b15798bed884a821',
     'generator_audio_noise_1': '4dc3de85c734bfd23024c381599bfe3f',
     ('filter_audio_subclip_1', 'container_output_1', '0->0'): '10355c7ad764f111b15798bed884a821|0',
     ('generator_audio_noise_1', '...subclip_1', '0->0'): '4dc3de85c734bfd23024c381599bfe3f|0'}
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__

    def complete(hashes, graph, node_name) -> str:
        if node_name not in hashes:
            node_attr = graph.nodes[node_name]
            local_node_signature = (
                f"{node_attr['class'].__name__}-"
                f"{'-'.join(str(node_attr['state'][k]) for k in sorted(node_attr['state']))}"
            )
            in_edges = sorted(  # the name of the edges in order of arrival on the node
                graph.in_edges(node_name, data=False, keys=True),
                key=lambda src_dst_key: int(src_dst_key[2].split("->")[1])
            )
            local_edges_signature = "-".join(k.split("->")[0] for _, _, k in in_edges)
            parents_signature = "-".join(complete(hashes, graph, n) for n, _, _ in in_edges)
            signature = hashlib.md5(  # md5 is the fastest
                f"{parents_signature}|{local_edges_signature}|{local_node_signature}".encode()
            ).hexdigest()
            hashes[node_name] = signature
            for _, dst, key in graph.out_edges(node_name, keys=True):
                hashes[(node_name, dst, key)] = f"{signature}|{int(key.split('->')[0])}"
        return hashes[node_name]

    hashes = {}
    for node_name in graph:
        complete(hashes, graph, node_name)
    return hashes
