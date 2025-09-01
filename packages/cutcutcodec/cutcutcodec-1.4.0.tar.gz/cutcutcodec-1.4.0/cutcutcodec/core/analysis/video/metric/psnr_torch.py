#!/usr/bin/env python3

"""Compute a differenciable batched torch psnr."""

import typing

import torch

from cutcutcodec.core.opti.parallel.threading import TorchThreads


def psnr_torch(
    im1: torch.Tensor, im2: torch.Tensor, weights: typing.Iterable[float] = None, threads: int = 0
) -> torch.Tensor:
    """Pure torch implementation of :py:func:`cutcutcodec.core.analysis.video.metric.psnr`.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.analysis.video.metric.psnr_torch import psnr_torch
    >>> _ = torch.manual_seed(0)
    >>> im1 = torch.rand(2, 4, 720, 1080, 3)
    >>> im2 = 0.8 * im1 + 0.2 * torch.rand(2, 4, 720, 1080, 3)
    >>> psnr_torch(im1[0, 0], im1[0, 0])
    tensor(100.)
    >>> psnr_torch(im1, im2)
    tensor([[21.7520, 21.7600, 21.7583, 21.7554],
            [21.7615, 21.7583, 21.7569, 21.7648]])
    >>>
    """
    assert isinstance(im1, torch.Tensor), im1.__class__.__name__
    assert isinstance(im2, torch.Tensor), im2.__class__.__name__
    assert im1.ndim == im2.ndim >= 3, (im1.shape, im2.shape)
    assert im1.shape == im2.shape, (im1.shape, im2.shape)

    # cast and normalise weights
    if weights is None:
        weights = [1.0 for _ in range(im1.shape[-1])]
    else:
        weights = [float(w) for w in weights]
        assert len(weights) == im1.shape[-1], (len(weights), im1.shape)
    weights = torch.asarray(weights, dtype=im1.dtype, device=im1.device)
    weights /= weights.sum()

    # compute psnr
    with TorchThreads(threads):
        layers_mse = ((im1 - im2)**2).mean(dim=(-2, -3))
        mse = (layers_mse * weights).sum(dim=-1)
        mse = mse.clamp_min(1e-10)
        psnr = -10.0*torch.log10(mse)

    return psnr
