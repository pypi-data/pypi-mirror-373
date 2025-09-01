#!/usr/bin/env python3

"""Crop an image."""

import numbers

import numpy as np
import torch

from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.filter.video.pad import _pad


def _patch(
    image: torch.Tensor, anchor: tuple[int, int], shape: tuple[int, int], copy: bool
) -> torch.Tensor:
    """Help ``patch``.

    Notes
    -----
    * No verifications are performed for performance reason.
    * The output tensor can be a reference to the provided tensor if copy is False.
    """
    bottom_right = (anchor[0] + shape[0], anchor[1] + shape[1])

    # case no padding
    if anchor >= (0, 0) and bottom_right <= image.shape[:2]:
        patch_img = image[anchor[0]:bottom_right[0], anchor[1]:bottom_right[1]]
        return patch_img.clone() if copy else patch_img

    padding = (
        max(0, -anchor[0]),  # top
        max(0, bottom_right[0]-image.shape[0]),  # bottom
        max(0, -anchor[1]),  # left
        max(0, bottom_right[1]-image.shape[1]),  # right
    )
    shape = (
        max(min(
            bottom_right[0] if anchor[0] <= 0 else image.shape[0]-anchor[0],
            image.shape[0], shape[0]), 0),
        max(min(
            bottom_right[1] if anchor[1] <= 0 else image.shape[1]-anchor[1],
            image.shape[1], shape[1]), 0),
    )
    anchor = (max(0, min(image.shape[0], anchor[0])), max(0, min(image.shape[1], anchor[1])))
    patch_img = _patch(image, anchor, shape, False)
    return _pad(patch_img, padding, False)


def patch(
    image: FrameVideo | torch.Tensor | np.ndarray,
    anchor: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
    shape: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
    copy: bool = True,
) -> FrameVideo | torch.Tensor | np.ndarray:
    """Extract part of the image seen through a window.

    If the window protrudes from the image, it is padded with transparent layer.

    Parameters
    ----------
    image : cutcutcodec.core.classes.image_video.FrameVideo or torch.Tensor or numpy.ndarray
        The image to be patch. If a numpy array is provide, the format
        has to match with the video image specifications.
    anchor : int and int
        The position of the top left corner of the window.
        The convention adopted is the numpy convention (height, width).
    shape : int and int
        The pixel dimensions of the returned image.
        The convention adopted is the numpy convention (height, width).
    copy : boolean, default=True
        If True, ensure that the returned tensor doesn't share the data of the input tensor.

    Returns
    -------
    patched_image
        The patched view image homogeneous with the input.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.classes.frame_video import FrameVideo
    >>> from cutcutcodec.core.filter.video.patch import patch
    >>> ref = FrameVideo(0, torch.full((4, 8, 1), 0.5))
    >>> patch(ref, (-2, -2), (7, 11))[..., 1]  # alpha layer
    tensor([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0.],
            [0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0.],
            [0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0.],
            [0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]])
    >>> patch(ref, (1, 1), (2, 6)).convert(1)[..., 0]  # as gray
    tensor([[0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000]])
    >>> patch(ref, (-1, -2), (4, 8)).convert(1)[..., 0]  # as gray
    tensor([[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.0000, 0.0000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.0000, 0.0000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000]])
    >>> patch(ref, (1, 2), (4, 8)).convert(1)[..., 0]  # as gray
    tensor([[0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])
    >>> patch(ref, (-2, -2), (4, 2)).convert(1)[..., 0]  # as gray
    tensor([[0., 0.],
            [0., 0.],
            [0., 0.],
            [0., 0.]])
    >>> patch(ref, (-2, 6), (2, 4)).convert(1)[..., 0]  # as gray
    tensor([[0., 0., 0., 0.],
            [0., 0., 0., 0.]])
    >>>
    """
    # case cast homogeneous
    if isinstance(image, FrameVideo):
        return FrameVideo(image.time, patch(torch.Tensor(image), anchor, shape, copy=copy))
    if isinstance(image, np.ndarray):
        return patch(torch.from_numpy(image), anchor, shape, copy=copy).numpy(force=True)

    # verif case np.ndarray
    assert isinstance(image, torch.Tensor), image.__class__.__name__
    assert image.ndim == 3, image.shape
    assert image.shape[0] >= 1, image.shape
    assert image.shape[1] >= 1, image.shape
    assert image.shape[2] in {1, 2, 3, 4}, image.shape
    assert image.dtype == torch.uint8 or image.dtype.is_floating_point
    assert isinstance(anchor, (tuple, list)), anchor.__class__.__name__
    assert len(anchor) == 2, len(anchor)
    assert all(isinstance(s, numbers.Integral) for s in anchor), anchor
    anchor = (int(anchor[0]), int(anchor[1]))
    assert isinstance(shape, (tuple, list)), shape.__class__.__name__
    assert len(shape) == 2, len(shape)
    assert all(isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape
    shape = (int(shape[0]), int(shape[1]))
    assert isinstance(copy, bool), copy.__class__.__name__

    # pad
    return _patch(image, anchor, shape, copy=copy)
