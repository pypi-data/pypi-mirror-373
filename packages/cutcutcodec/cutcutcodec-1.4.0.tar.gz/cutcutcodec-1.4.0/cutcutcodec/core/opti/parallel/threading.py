#!/usr/bin/env python3

"""Thread utils."""

import numbers
import os
import threading

import torch


def get_num_threads(threads: numbers.Integral) -> int:
    """Return the number of threads."""
    assert isinstance(threads, numbers.Integral), threads.__class__.__name__
    if threads == 0:
        return max(2, os.cpu_count()//2) if threading.current_thread().name == "MainThread" else 1
    if threads < 0:
        return max(2, os.cpu_count()//2)
    return int(threads)


class TorchThreads:
    """Context manager to set the number of torch threads.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.opti.parallel.threading import TorchThreads
    >>> (t := torch.get_num_threads()) != 1
    True
    >>> with TorchThreads(1):
    ...     torch.get_num_threads()
    ...
    1
    >>> torch.get_num_threads() == t
    True
    >>>
    """

    def __init__(self, threads: numbers.Integral):
        """Initialise the thread setter.

        Parameters
        ----------
        threads : int
            The number of threads, same as ``get_num_threads``.
        """
        self.threads = get_num_threads(threads)
        self.torch_threads = None
        # self.torch_interop_threads = None

    def __enter__(self) -> int:
        """Set the threading torch context."""
        self.torch_threads = torch.get_num_threads()
        # self.torch_interop_threads = torch.get_num_interop_threads()
        torch.set_num_threads(self.threads)
        # torch.set_num_interop_threads(self.threads)
        return self.threads

    def __exit__(self, *_):
        """Reset the previous threads."""
        torch.set_num_threads(self.torch_threads)
        # torch.set_num_interop_threads(self.torch_interop_threads)
