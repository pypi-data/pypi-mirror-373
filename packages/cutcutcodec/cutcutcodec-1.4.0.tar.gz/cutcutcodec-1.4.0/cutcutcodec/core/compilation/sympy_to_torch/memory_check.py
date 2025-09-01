#!/usr/bin/env python3

"""Test some array memory caracteristiques."""


def overlap(strides: tuple[int], shapes: tuple[int]) -> bool:
    """Return True if all items are not memory independant.

    Parameters
    ----------
    strides : tuple[int]
        The step on each dimension.
    shapes : tuple[int]
        Each dimension lenght.

    Returns
    -------
    overlap : bool
        True if some data are overlapping, it may return True in some situation of non overlaping.
        When False, it is 100% shure it is memory safe!

    Examples
    --------
    >>> from cutcutcodec.core.compilation.sympy_to_torch.memory_check import overlap
    >>> overlap((0,), (10,))
    True
    >>> overlap((1,), (10,))  # c contiguous
    False
    >>> overlap((2,), (10,))
    False
    >>> overlap((10, 0), (100, 10))
    True
    >>> overlap((9, 1), (100, 10))
    True
    >>> overlap((10, 1), (100, 10))  # c contiguous
    False
    >>> overlap((10, 2), (100, 10))
    True
    >>> overlap((20, 2), (100, 10))
    False
    >>>
    """
    assert isinstance(strides, tuple), strides.__class__.__name__
    assert isinstance(shapes, tuple), shapes.__class__.__name__
    assert len(shapes) == len(strides)

    strides = tuple(abs(s) for s in strides)  # set all strides positive
    idx = sorted(range(len(strides)), key=strides.__getitem__)  # argsort
    itemsize = 1  # staring itemsize, then offset
    for i in idx:  # from the smallest strides to the biggest
        if itemsize > strides[i]:
            return True
        itemsize = shapes[i] * strides[i]
    return False
