#!/usr/bin/env python3

"""The not sofisticated cache decorators."""

import functools

from .hashable import hashable


def basic_cache(func: callable) -> callable:
    """Cache for hashable args.

    Examples
    --------
    >>> from cutcutcodec.core.opti.cache.basic import basic_cache
    >>> i = 0
    >>> @basic_cache
    ... def f(x):
    ...     global i
    ...     i += x
    ...     return i
    ...
    >>> f(1)
    1
    >>> f(1)
    1
    >>>
    """
    @functools.wraps(func)
    def cached_func(*args, **kwargs) -> callable:
        signature = hashable((args, tuple((k, kwargs[k]) for k in sorted(kwargs))))
        func.__cache__ = getattr(func, "__cache__", {})
        if signature not in func.__cache__:
            func.__cache__[signature] = func(*args, **kwargs)
        return func.__cache__[signature]

    return cached_func


def method_cache(meth: callable) -> callable:
    """Cache a class method.

    Examples
    --------
    >>> from cutcutcodec.core.opti.cache.basic import method_cache
    >>> i = 0
    >>> class Foo:
    ...     @method_cache
    ...     def f(self, x):
    ...         global i
    ...         i += x
    ...         return i
    ...
    >>> foo = Foo()
    >>> foo.f(1)
    1
    >>> foo.f(1)
    1
    >>>
    """
    @functools.wraps(meth)
    def cached_meth(self, *args, **kwargs) -> callable:
        signature = hashable((args, tuple((k, kwargs[k]) for k in sorted(kwargs))))
        self.__cache__ = getattr(self, "__cache__", {})
        if signature not in self.__cache__:
            self.__cache__[signature] = meth(self, *args, **kwargs)
        return self.__cache__[signature]

    return cached_meth
