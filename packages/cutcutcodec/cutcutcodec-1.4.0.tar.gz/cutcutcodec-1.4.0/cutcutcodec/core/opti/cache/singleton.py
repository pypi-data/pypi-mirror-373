#!/usr/bin/env python3

"""Allow to create only one instance of an object."""

from .hashable import hashable


class MetaSingleton(type):
    """For share memory inside the current session.

    Notes
    -----
    The arguments needs to be hashable.

    Examples
    --------
    >>> from cutcutcodec.core.opti.cache.singleton import MetaSingleton
    >>> class A:
    ...     pass
    ...
    >>> class B(metaclass=MetaSingleton):
    ...     pass
    ...
    >>> class C(metaclass=MetaSingleton):
    ...     def __init__(self, *args, **kwargs):
    ...         self.args = args
    ...         self.kwargs = kwargs
    ...
    >>> A() is A()
    False
    >>> B() is B()
    True
    >>> C(0) is C(0)
    True
    >>> C(0) is C(1)
    False
    >>>
    """

    instances: dict = {}

    def __call__(cls, *args, **kwargs):
        """Create a new class only if it is not already instanciated."""
        signature = (cls, hashable(args), hashable(tuple((k, kwargs[k]) for k in sorted(kwargs))))
        if signature not in MetaSingleton.instances:
            instance = cls.__new__(cls)
            instance.__init__(*args, **kwargs)
            MetaSingleton.instances[signature] = instance
        return MetaSingleton.instances[signature]
