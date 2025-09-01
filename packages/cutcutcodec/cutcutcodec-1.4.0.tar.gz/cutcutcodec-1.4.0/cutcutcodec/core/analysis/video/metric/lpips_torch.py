#!/usr/bin/env python3

"""Compute a differenciable batched torch lpips."""

import os
import threading

import torch

from cutcutcodec.core.opti.parallel.threading import TorchThreads


LOCK = threading.Lock()


def _get_lpips_model(net: str):
    from lpips import LPIPS  # pip install lpips
    return LPIPS(net=net, verbose=False)


def lpips_torch(
    im1: torch.Tensor, im2: torch.Tensor, net: str | torch.nn.Module = "alex", threads: int = 0
) -> torch.Tensor:
    """Pure torch implementation of :py:func:`cutcutcodec.core.analysis.video.metric.lpips`.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.analysis.video.metric.lpips_torch import lpips_torch
    >>> _ = torch.manual_seed(0)
    >>> im1 = torch.rand(2, 4, 720, 1080, 3)
    >>> im2 = 0.8 * im1 + 0.2 * torch.rand(2, 4, 720, 1080, 3)
    >>> lpips_torch(im1[0, 0], im1[0, 0])
    tensor(0.)
    >>> lpips_torch(im1, im2)
    tensor([[0.0492, 0.0443, 0.0468, 0.0469],
            [0.0444, 0.0445, 0.0470, 0.0446]])
    >>>
    """
    assert isinstance(im1, torch.Tensor), im1.__class__.__name__
    assert isinstance(im2, torch.Tensor), im2.__class__.__name__
    assert im1.ndim == im2.ndim >= 3, (im1.shape, im2.shape)
    assert im1.shape == im2.shape, (im1.shape, im2.shape)
    assert im1.shape[-1] == 3, im1.shape
    assert isinstance(net, str | torch.nn.Module), net.__class__.__name__

    if isinstance(net, str):
        model = _get_lpips_model(net)
    else:
        model = net
    *batch, height, width, _ = im1.shape
    im1, im2 = im1.reshape(-1, height, width, 3), im2.reshape(-1, height, width, 3)  # (n, h, w, 3)
    im1, im2 = im1.movedim(3, 1), im2.movedim(3, 1)  # (n, 3, h, w)

    if threads <= 0:
        threads = max(2, os.cpu_count()//2)  # nested threads are created because they are locked

    with TorchThreads(threads), LOCK:
        im1, im2 = im1*2.0 - 1.0, im2*2.0 - 1.0  # from [0, 1] to [-1, 1]
        if im1.requires_grad or im2.requires_grad:
            loss = model(im1, im2)
        else:
            with torch.no_grad():  # by default, a gradient is append
                loss = model(im1, im2)
    loss = loss.reshape(batch)
    return loss
