#!/usr/bin/env python3

"""Allow the pooling of information from several estimation functions.

The function removes the redundancy of the analyses performed by ffmpeg, ffprobe and cv2.
"""

import collections
import numbers
import pathlib
import typing

from cutcutcodec.core.exceptions import MissingStreamError, MissingInformation


def _check_pathexists_index(filename: pathlib.Path | str | bytes, index: int) -> None:
    assert pathlib.Path(filename).exists(), filename
    assert isinstance(index, numbers.Integral), index.__class__.__name__
    assert index >= 0, index


def _mix_and_check(
    backend: typing.Optional[str], accurate: bool, args: tuple, funcs: collections.OrderedDict
) -> typing.Any:

    # checks
    available_backends = {p["backend"] for p in funcs.values()}
    assert backend is None or backend in available_backends, \
        f"{backend} not in {available_backends}"
    assert isinstance(accurate, bool), accurate.__class__.__name__

    # declarations
    list_funcs = list(funcs)
    err = MissingStreamError("there are no estimators satisfying this request")

    # selection
    if accurate:
        for func, prop in funcs.items():
            if not prop["accurate"]:
                list_funcs.remove(func)
    if backend is not None:
        for func, prop in funcs.items():
            if prop["backend"] != backend and func in list_funcs:
                list_funcs.remove(func)

    # execution
    for func in list_funcs:
        try:
            return func(*args)
        except (MissingStreamError, MissingInformation) as err_:
            err = err_
    raise err
