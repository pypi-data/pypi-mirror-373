#!/usr/bin/env python3

"""Buffer management in threading loop."""

import numbers
import queue
import threading
import typing

from .threading import get_num_threads


class _FuncEvalThread(threading.Thread):
    """Manage exception and autostart."""

    def __init__(self, *args, func=None, arg=None, res_buff=None, **kwargs):
        self.func = func
        self.arg = arg
        self.res_buff = res_buff

        self.result = None
        self.exception = False

        super().__init__(*args, **kwargs)
        self.start()

    def run(self):
        try:
            self.result = self.func(*self.arg)
        except Exception as err:  # pylint: disable=W0718
            self.exception = True
            self.result = err
        if self.res_buff is not None:
            self.res_buff.put(self)

    def get(self):
        """Return or throw the result."""
        self.join()
        if self.exception:
            raise self.result
        return self.result


def _check_input(func: callable, args: typing.Iterable, maxsize: numbers.Integral = 0):
    """Perform test on the inputs."""
    assert callable(func), func.__class__.__name__
    assert isinstance(args, typing.Iterable), args.__class__.__name__
    assert isinstance(maxsize, numbers.Integral), maxsize.__class__.__name__


def imap(func: callable, args: typing.Iterable, maxsize: numbers.Integral = 0):
    """Like :py:func:`cutcutcodec.core.opti.parallel.starimap` with one argument.

    Examples
    --------
    >>> import time
    >>> from cutcutcodec.core.opti.parallel.buffer import imap
    >>> def foo(t):
    ...     time.sleep(t)
    ...     return t
    ...
    >>> list(imap(foo, [1.0, 0.5, 0.0], maxsize=3))  # yield fastest first
    [0.0, 0.5, 1.0]
    >>>
    """
    assert isinstance(args, typing.Iterable), args.__class__.__name__
    yield from starimap(func, ((a,) for a in args), maxsize)


def map(
    func: callable, args: typing.Iterable, maxsize: numbers.Integral = 0
):  # pylint: disable=W0622
    """Like :py:func:`cutcutcodec.core.opti.parallel.starmap` with one argument.

    Examples
    --------
    >>> import time
    >>> from cutcutcodec.core.opti.parallel.buffer import map
    >>> def foo(t):
    ...     time.sleep(t)
    ...     return t
    ...
    >>> list(map(foo, [1.0, 0.5, 0.0]))  # keep order
    [1.0, 0.5, 0.0]
    >>>
    """
    assert isinstance(args, typing.Iterable), args.__class__.__name__
    yield from starmap(func, ((a,) for a in args), maxsize)


def starimap(func: callable, args: typing.Iterable, maxsize: numbers.Integral = 0):
    """Like ``multiprocessing.pool.ThreadPool.imap`` but with limited buffer and stared args.

    Parameters
    ----------
    func : callable
        The function to evaluate in an over thread.
    args : iterable
        The parameters to give a the function.
    maxsize : int, default=max(2, os.cpu_count()//2)
        The size of the buffer.

    Notes
    -----
    * Contrary to multiprocessing functions, ``args`` is iterated in the main thread.
    * If an exception is raised in one of the threads, it is propagated to this function.

    Examples
    --------
    >>> import itertools
    >>> from cutcutcodec.core.opti.parallel.buffer import starimap
    >>> def foo(x, y):
    ...     return x + y
    ...
    >>> sorted(starimap(foo, itertools.product(["a", "b", "c"], ["1", "2", "3"])))
    ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']
    >>>
    """
    _check_input(func, args, maxsize)
    maxsize = get_num_threads(maxsize)

    buff, buff_size = queue.Queue(), 0
    for star_arg in args:
        _FuncEvalThread(func=func, arg=star_arg, res_buff=buff, daemon=True)
        buff_size += 1
        if buff_size < maxsize:
            continue
        yield buff.get().get()
        buff_size -= 1
    yield from (buff.get().get() for _ in range(buff_size))


def starmap(func: callable, args: typing.Iterable, maxsize: numbers.Integral = 0):
    """Like ``multiprocessing.pool.ThreadPool.map`` but with limited buffer and stared args.

    Parameters
    ----------
    func : callable
        The function to evaluate in an over thread.
    args : iterable
        The parameters to give a the function.
    maxsize : int, default=max(2, os.cpu_count()//2)
        The size of the buffer.

    Notes
    -----
    * Contrary to multiprocessing functions, ``args`` is iterated in the main thread.
    * If an exception is raised in one of the threads, it is propagated to this function.

    Examples
    --------
    >>> import itertools
    >>> from cutcutcodec.core.opti.parallel.buffer import starmap
    >>> def foo(x, y):
    ...     return x + y
    ...
    >>> list(starmap(foo, itertools.product(["a", "b", "c"], ["1", "2", "3"])))
    ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']
    >>>
    """
    _check_input(func, args, maxsize)
    maxsize = get_num_threads(maxsize)

    buff, buff_size = queue.Queue(), 0
    for star_arg in args:
        buff.put(_FuncEvalThread(func=func, arg=star_arg, daemon=True))
        buff_size += 1
        if buff_size < maxsize:
            continue
        yield buff.get().get()
        buff_size -= 1
    yield from (buff.get().get() for _ in range(buff_size))
