#!/usr/bin/env python3

"""Image Data Augmentations."""

import math
import numbers
import random
import typing

from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.filter.video.patch import patch
from cutcutcodec.core.filter.video.resize import resize


class RandomResizedCrop:
    """Resize and Crop an image to reach a final size.

    It consists in random rescale and random cropping.
    It conserve the proportion of the input image.

    Attributes
    ----------
    shape : tuple[int, int]
        The output shape (readonly).

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.classes.frame_video import FrameVideo
    >>> from cutcutcodec.core.nn.dataaug.image import RandomResizedCrop
    >>> image = FrameVideo(0, torch.rand((480, 720, 3)))
    >>> dataaug = RandomResizedCrop((16, 16))
    >>> dataaug(image).shape
    (16, 16, 3)
    >>>
    """

    def __init__(
        self,
        shape: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
        win_area: typing.Optional[
            tuple[numbers.Real, numbers.Real] | list[numbers.Real]
        ] = (1.0, 9.0),
    ):
        """Initialise and create the class.

        Parameters
        ----------
        shape : int and int
            The pixel dimensions of the final image.
            The convention adopted is the numpy convention (height, width).
        win_area : float and float
            The max and min ratio of the total surface by the window surface.
        """
        assert isinstance(shape, (tuple, list)), shape.__class__.__name__
        assert len(shape) == 2, len(shape)
        assert all(isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape
        assert isinstance(win_area, (tuple, list)), shape.__class__.__name__
        assert len(win_area) == 2, len(win_area)
        assert all(isinstance(a, numbers.Real) and a >= 1.0 for a in win_area), win_area

        self._shape = (int(shape[0]), int(shape[1]))
        self._win_area = (float(win_area[0]), float(win_area[1]))

    def __call__(self, image: FrameVideo) -> FrameVideo:
        """Apply the transformation.

        Parameters
        ----------
        image : cutcutcodec.core.classes.frame_video.FrameVideo
            The input brut image of any shape, channels and dtype.

        Returns
        -------
        cutcutcodec.core.classes.frame_video.FrameVideo
            The rescaled and cropped image.
            This will be a new view object if possible; otherwise, it will be a copy.
        """
        assert isinstance(image, FrameVideo), image.__class__.__name__

        # rescale
        zoom_min = max(  # minimum zoom to be shure cropping, not padding
            self._shape[0]/image.shape[0], self._shape[1]/image.shape[1]
        )
        brut_area_factor = (self._shape[0]*self._shape[1]) / (image.shape[0]*image.shape[1])
        zoom_area_0 = math.sqrt(self._win_area[0] * brut_area_factor)
        zoom_area_1 = math.sqrt(self._win_area[1] * brut_area_factor)
        zoom = random.uniform(max(zoom_min, zoom_area_0), max(zoom_min, zoom_area_1))
        shape = (round(image.shape[0]*zoom), round(image.shape[1]*zoom))
        image = resize(image, shape, copy=False)

        # crop
        anchor = (
            random.randint(0, image.shape[0]-self._shape[0]),
            random.randint(0, image.shape[1]-self._shape[1]),
        )
        image = patch(image, anchor, self._shape, copy=False)

        return image

    @property
    def shape(self) -> tuple[int, int]:
        """Return the output shape."""
        return self._shape
