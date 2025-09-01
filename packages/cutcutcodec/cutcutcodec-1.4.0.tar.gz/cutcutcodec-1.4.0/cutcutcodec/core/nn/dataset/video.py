#!/usr/bin/env python3

"""A video dataset."""

import math
import numbers
import pathlib
import random
import typing

import torch

from cutcutcodec.core.analysis.stream import optimal_rate_video, optimal_shape_video
from cutcutcodec.core.io import read
from cutcutcodec.core.io.cst import VIDEO_SUFFIXES
from .base import Dataset


class VideoDataset(Dataset):
    """A specific dataset to manage sub videos."""

    def __init__(
        self,
        root: pathlib.Path | str | bytes,
        shape: typing.Optional[tuple[numbers.Integral, numbers.Integral]] = None,
        *,
        dataaug: typing.Optional[typing.Callable[[torch.Tensor], torch.Tensor]] = None,
        **kwargs,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        root : pathlike
            Transmitted to ``Dataset`` initialisator.
        shape : tuple[int, int], optional
            If given, the video will be truncated and reshape at the shape (height, width).
            If not provided, the returned shape is the shape of the original video.
        dataaug : callable, optional
            If provided, the function is called for each brut readed frames batch (h, w, 3*n).
        n_min : int, default = 1
            The minimum number of frames
        n_max : int, default = 1024
            The maximum number of frames
        size : int, default = 104857600
            The targeted video size in bytes. By default 100 Mio.
        **kwargs : dict
            Transmitted to ``Datset`` initialisator.
        """
        assert dataaug is None or callable(dataaug), dataaug.__class__.__name__

        if shape is not None:
            shape = tuple(shape)
            assert len(shape) == 2, shape
            assert isinstance(shape[0], numbers.Integral) and isinstance(shape[1], numbers.Integral)
            assert shape > (0, 0)

        def _selector(file: pathlib.Path) -> bool:
            if file.suffix.lower() not in VIDEO_SUFFIXES:
                return False
            return kwargs.get("selector", lambda p: True)(file)

        self.shape = shape
        self.dataaug = dataaug
        self.n_min, self.n_max = kwargs.pop("n_min", 1), kwargs.pop("n_max", 1024)
        assert isinstance(self.n_min, numbers.Integral), self.n_min.__class__.__name__
        assert isinstance(self.n_max, numbers.Integral), self.n_max.__class__.__name__
        assert 0 < self.n_min <= self.n_max, (self.n_min, self.n_max)
        self.size = kwargs.pop("size", 104857600)
        assert isinstance(self.size, numbers.Integral), self.size.__class__.__name__
        assert self.size >= 0, self.size
        self.metadata: dict[pathlib.Path] = {}
        super().__init__(root, **kwargs, selector=_selector)

    def __getitem__(self, idx: int) -> torch.Tensor:
        """Read a random sequence in the video.

        Examples
        --------
        >>> from cutcutcodec.core.nn.dataset.video import VideoDataset
        >>> from cutcutcodec.utils import get_project_root
        >>> dataset = VideoDataset(get_project_root().parent / "media")
        >>> len(dataset)
        2
        >>> dis, ref = dataset[0]
        >>> dis.shape, ref.shape
        (torch.Size([64, 64, 3]), torch.Size([64, 64, 3]))
        >>>
        """
        file = super().__getitem__(idx)

        with read(file) as container:
            stream = container.out_select("video")[0]
            if file not in self.metadata:
                shape = self.shape or optimal_shape_video(stream)
                self.metadata[file] = (
                    optimal_rate_video(stream),
                    stream.duration,
                    shape,
                    max(shape, optimal_shape_video(stream)),
                )
            rate, duration, shape, shape_m = self.metadata[file]
            n_frames = round(self.size / (12 * shape[0] * shape[1]))
            n_frames = min(math.floor(duration * rate), self.n_max, max(self.n_min, n_frames))
            t_start = random.random() * (duration - n_frames / rate)
            crop = (random.randint(0, shape_m[0]-shape[0]), random.randint(0, shape_m[1]-shape[1]))
            ref = [
                stream.snapshot(t_start + i/rate, shape_m).convert(3)
                [crop[0]:crop[0]+shape[0], crop[1]:crop[1]+shape[1], :]
                for i in range(n_frames)
            ]
        while len(ref) < self.n_min:
            ref.append(ref[-1])
        ref = torch.cat(ref, dim=2)

        if self.dataaug is not None:
            dis = self.dataaug(ref)
        else:
            dis = ref

        return dis, ref
