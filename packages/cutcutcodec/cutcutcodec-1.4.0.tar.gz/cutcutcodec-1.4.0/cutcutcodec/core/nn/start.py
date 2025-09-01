#!/usr/bin/env python3

"""Help to store and load the weights."""

import hashlib
import io
import logging
import lzma
import pathlib
import tempfile
import typing
import urllib

import torch
import tqdm

from cutcutcodec.utils import get_project_root


def download(stem: str) -> pathlib.Path:
    """Attempt to recover network weight on internet.

    Parameters
    ----------
    stem : str
        The hexadecimal hash of the model weights.

    Returns
    -------
    weights : pathlib.Path
        The path of the downloded weights.

    Raises
    ------
    FileNotFoundError
        If the weights doese not exists on the gitlab.
    ConnectionError
        If the connection to internet is missing or broken.

    Examples
    --------
    >>> from cutcutcodec.core.nn.start import download
    >>> download("631ac8be291fd6c627e6b3b54ce37fdd")
    PosixPath('/tmp/631ac8be291fd6c627e6b3b54ce37fdd.pt.xz')
    >>>
    """
    url = (
        "https://framagit.org/robinechuca/cutcutcodec/"
        f"-/raw/main/cutcutcodec/models/{stem}.pt.xz"
    )
    try:
        with urllib.request.urlopen(url) as req:
            if req.status != 200:
                raise ConnectionError(
                    f"please check your internet connection, failed to get {stem}"
                )
            filename = pathlib.Path(tempfile.gettempdir()) / f"{stem}.pt.xz"
            with open(filename, "wb") as raw:
                progress = tqdm.tqdm(desc="download", total=req.length)
                while data := req.read(1024):
                    raw.write(data)
                    progress.update(len(data))
    except urllib.error.HTTPError as err:
        raise FileNotFoundError(f"the weights {stem} are not existing online") from err
    return filename


def load(model: torch.nn.Module, weights: typing.Optional[pathlib.Path | str | bytes] = None):
    """Load the pretrained weights.

    Parameters
    ----------
    model : torch.nn.Module
        The model to be loaded.
    weights : pathlike, optional
        The path to the loading weight file with the suffix .pt or .pt.xz
    """
    assert isinstance(model, torch.nn.Module), model.__class__.__name__

    # get weights
    if weights is None:
        root = pathlib.Path.home() / ".cache" / "cutcutcodec" / "models"
        root.mkdir(parents=True, exist_ok=True)
        stem = hashlib.md5(str(model).encode(), usedforsecurity=False).hexdigest()
        weights = root / f"{stem}.pt"
        if not weights.exists():  # need to be extracted
            comp = get_project_root() / "models" / f"{stem}.pt.xz"
            if not comp.exists():
                try:
                    comp = download(stem)
                except FileNotFoundError:
                    logging.warning("%s weights not found locally or online", comp)
                    return
            with lzma.open(comp, "rb") as src, open(weights, "wb") as dst:
                dst.write(src.read())
    else:
        weights = pathlib.Path(weights).expanduser()
    if not weights.exists():
        logging.warning("the weights %s were not founded", comp)
        return

    # load weights
    model.load_state_dict(torch.load(weights, weights_only=True))


def save(
    model: torch.nn.Module, weights: typing.Optional[pathlib.Path | str | bytes] = None
) -> pathlib.Path:
    """Load the pretrained weights.

    Parameters
    ----------
    model : torch.nn.Module
        The model to be loaded.
    weights : pathlib, optional
        The path of the recorded file, with the extention .pt.xz

    Returns
    -------
    weights : pathlib.Path
        The recorded file.

    Examples
    --------
    >>> import pathlib, tempfile
    >>> import torch
    >>> from cutcutcodec.core.nn.start import save
    >>> weights = pathlib.Path(tempfile.gettempdir()) / "tmp.pt.xz"
    >>> class Model(torch.nn.Module):
    ...     def __init__(self):
    ...         super().__init__()
    ...         self.layer = torch.nn.Conv2d(3, 3, kernel_size=3)
    ...
    >>> model = Model()
    >>> save(model, weights)
    PosixPath('/tmp/tmp.pt.xz')
    >>> weights.unlink()
    >>>
    """
    assert isinstance(model, torch.nn.Module), model.__class__.__name__

    # save model
    model.to("cpu")  # to avoid loading cuda data on cpu only environement
    buffer = io.BytesIO()
    torch.save(model.state_dict(), buffer, _use_new_zipfile_serialization=False)
    buffer.seek(0)

    # get record file
    if weights is None:
        stem = hashlib.md5(str(model).encode(), usedforsecurity=False).hexdigest()
        weights = get_project_root() / "models" / f"{stem}.pt.xz"
    else:
        weights = pathlib.Path(weights).expanduser()
        assert weights.suffixes == [".pt", ".xz"], weights

    # compress
    with lzma.open(weights, "wb", preset=lzma.PRESET_EXTREME) as file:
        file.write(buffer.read())

    return weights
