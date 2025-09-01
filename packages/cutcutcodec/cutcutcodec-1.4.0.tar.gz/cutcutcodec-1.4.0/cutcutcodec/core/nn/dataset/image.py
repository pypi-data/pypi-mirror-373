#!/usr/bin/env python3

"""An image dataset."""

import numbers
import pathlib
import typing

import torch

from cutcutcodec.core.analysis.stream import optimal_shape_video
from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.io import read
from cutcutcodec.core.io.cst import IMAGE_SUFFIXES
from .base import Dataset


class ImageDataset(Dataset):
    """A specific dataset for managing images."""

    def __init__(
        self,
        root: pathlib.Path | str | bytes,
        shape: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
        *,
        dataaug: typing.Optional[typing.Callable[[FrameVideo], FrameVideo]] = None,
        **kwargs,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        root : pathlike
            Transmitted to ``Dataset`` initialisator.
        shape : int and int
            The pixel dimensions of the returned image.
            The image will be random reshaped and random cropped to reach this final shape.
            The convention adopted is the numpy convention (height, width).
        dataaug : callable, optional
            If provided, the function is called for each brut readed image before normalization.
        **kwargs : dict
            Transmitted to ``Datset`` initialisator.
        """
        assert isinstance(shape, (tuple, list)), shape.__class__.__name__
        assert len(shape) == 2, len(shape)
        assert all(isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape
        assert dataaug is None or callable(dataaug), dataaug.__class__.__name__

        def _selector(file: pathlib.Path) -> bool:
            if file.suffix.lower() not in IMAGE_SUFFIXES:
                return False
            return kwargs.get("selector", lambda p: True)(file)

        super().__init__(root, **kwargs, selector=_selector)
        self.shape = (int(shape[0]), int(shape[1]))
        self.dataaug = dataaug

    def __getitem__(self, idx: int) -> torch.Tensor:
        """Read the image of index ``idx``.

        Parameters
        ----------
        idx : int
            Transmitted to ``Datset.__getitem__``.

        Returns
        -------
        image : torch.Tensor
            The readed augmented and converted throw the method ``ImageDataset.normalize``.
        """
        file = super().__getitem__(idx)
        with read(file) as container:
            stream = container.out_select("video")[0]
            img = stream.snapshot(0, self.shape or optimal_shape_video(stream))
        if self.dataaug is not None:
            img = self.dataaug(img)
        return img
