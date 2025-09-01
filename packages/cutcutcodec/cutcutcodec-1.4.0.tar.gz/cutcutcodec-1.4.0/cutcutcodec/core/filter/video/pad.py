#!/usr/bin/env python3

"""Add padding to an image while keeping the proportions."""

import numbers

import numpy as np
import torch

from cutcutcodec.core.classes.frame_video import FrameVideo


def _pad(image: torch.Tensor, padding: tuple[int, int, int, int], copy: bool) -> torch.Tensor:
    """Add transparent borders to enlarge an image.

    Parameters
    ----------
    image : torch.Tensor
        The image to be padded, of shape (height, width, channels).
        The dtype is assumed to be float32.
    padding : tuple[int, int, int, int]
        The pixel size of borders top, bottom, left, right.
    copy : boolean
        If True, ensure that the returned tensor doesn't share the data of the input tensor.

    Returns
    -------
    padded_image : torch.Tensor
        The padded image.

    Notes
    -----
    * No verifications are performed for performance reason.
    * The output tensor can be a reference to the provided tensor if copy is False.
    """
    # optimization, avoid management of alpha channel
    if padding == (0, 0, 0, 0):
        return image.clone() if copy else image

    # preparation
    height, width, depth = image.shape
    top, bottom, left, right = padding

    # manage alpha channel
    channels = {1: 2, 2: 2, 3: 4, 4: 4}[depth]  # nbr of output channels
    padded_image = torch.empty(   # 1200 times faster than torch.zeros
        (height+top+padding[1], width+padding[2]+padding[3], channels),
        dtype=image.dtype, device=image.device
    )

    # make transparent borders (and black)
    if top:
        # padded_image[:top, :, -1] = 0.0  # transparent
        padded_image[:top, :, :] = 0.0  # transparent
    if bottom:
        # padded_image[height+top:, :, -1] = 0.0  # transparent
        padded_image[height+top:, :, :] = 0.0  # transparent
    if left:
        # padded_image[top:height+top, :left, -1] = 0.0  # transparent
        padded_image[top:height+top, :left, :] = 0.0  # transparent
    if right:
        # padded_image[top:height+top, width+left:, -1] = 0.0  # transparent
        padded_image[top:height+top, width+left:, :] = 0.0  # transparent

    # copy image content
    padded_image[top:height+top, left:width+left, :depth] = image
    if depth != channels:
        padded_image[top:height+top, left:width+left, -1] = 1.0  # blind
    return padded_image


def _pad_keep_ratio(image: torch.Tensor, shape: tuple[int, int], copy: bool) -> torch.Tensor:
    """Help ``pad_keep_ratio``.

    Notes
    -----
    * No verifications are performed for performance reason.
    * The output tensor can be a reference to the provided tensor if copy is False.
    """
    top, bottom = divmod(shape[0]-image.shape[0], 2)
    bottom += top
    left, right = divmod(shape[1]-image.shape[1], 2)
    right += left
    return _pad(image, (top, bottom, left, right), copy)


def pad_keep_ratio(
    image: FrameVideo | torch.Tensor | np.ndarray,
    shape: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
    copy: bool = True,
) -> FrameVideo | torch.Tensor | np.ndarray:
    """Pad the image with transparent borders.

    Parameters
    ----------
    image : cutcutcodec.core.classes.image_video.FrameVideo or torch.Tensor or numpy.ndarray
        The image to be padded. If a numpy array is provide, the format
        has to match with the video image specifications.
    shape : int and int
        The pixel dimensions of the returned image.
        Each dimension has to be larger or equal to the provided image.
        The convention adopted is the numpy convention (height, width).
    copy : boolean, default=True
        If True, ensure that the returned tensor doesn't share the data of the input tensor.

    Returns
    -------
    padded_image
        The padded image homogeneous with the input.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.classes.frame_video import FrameVideo
    >>> from cutcutcodec.core.filter.video.pad import pad_keep_ratio
    >>> ref = FrameVideo(0, torch.full((4, 6, 1), 0.5))
    >>> pad_keep_ratio(ref, (8, 6))[..., 1]  # alpha layer
    tensor([[0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0.],
            [1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1.],
            [0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0.]])
    >>> pad_keep_ratio(ref, (4, 7)).convert(1)[..., 0]  # as gray
    tensor([[0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000]])
    >>> pad_keep_ratio(ref, (6, 8)).convert(1)[..., 0]  # as gray
    tensor([[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000],
            [0.0000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000],
            [0.0000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000],
            [0.0000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])
    >>>
    """
    # case cast homogeneous
    if isinstance(image, FrameVideo):
        return FrameVideo(image.time, pad_keep_ratio(torch.Tensor(image), shape, copy=copy))
    if isinstance(image, np.ndarray):
        return pad_keep_ratio(torch.from_numpy(image), shape, copy=copy).numpy(force=True)

    # verif
    assert isinstance(image, torch.Tensor), image.__class__.__name__
    assert image.ndim == 3, image.shape
    assert image.shape[0] >= 1, image.shape
    assert image.shape[1] >= 1, image.shape
    assert image.shape[2] in {1, 2, 3, 4}, image.shape
    assert image.dtype == torch.uint8 or image.dtype.is_floating_point
    assert isinstance(shape, (tuple, list)), shape.__class__.__name__
    assert len(shape) == 2, len(shape)
    assert all(isinstance(s, numbers.Integral) for s in shape), shape
    shape = (int(shape[0]), int(shape[1]))
    assert shape >= image.shape[:2], f"no crop from {image.shape} to {shape}, only padding"
    assert isinstance(copy, bool), copy.__class__.__name__

    # pad
    return _pad_keep_ratio(image, shape, copy=copy)
