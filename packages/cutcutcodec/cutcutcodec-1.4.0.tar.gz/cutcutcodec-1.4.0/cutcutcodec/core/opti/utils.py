#!/usr/bin/env python3

"""Little tools used by some functions of graph optimization."""

import functools

import networkx


def node_selector(criteria: callable) -> callable:
    """Decorate for selecting and appening the `node` kwargs to the decorated function.

    Parameters
    ----------
    criteria : callable
        A function that take in argument
        the graph (`networkx.networkx.MultiDiGraph`) and the node name (`str`).
        It returns True if the node can be selected, False otherwise.
    """
    assert callable(criteria), criteria.__class__.__name__

    def decorator(func: callable) -> callable:
        @functools.wraps(func)
        def decorated(graph: networkx.MultiDiGraph, *args, **kwargs):
            while True:
                for node in graph:
                    if criteria(graph, node):
                        func(graph, *args, node=node, **kwargs)
                        break
                else:
                    break
        return decorated

    return decorator
