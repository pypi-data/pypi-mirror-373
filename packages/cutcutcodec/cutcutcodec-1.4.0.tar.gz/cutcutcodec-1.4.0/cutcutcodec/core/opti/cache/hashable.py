#!/usr/bin/env python3

"""Makes the signature hashable."""

import pickle


def hashable(signature: object) -> object:
    """Return an hashable object."""
    try:
        hash(signature)
    except TypeError:
        return pickle.dumps(signature)
    return signature
