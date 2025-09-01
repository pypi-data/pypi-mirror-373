#!/usr/bin/env python3

"""Compute a differenciable batched torch ssim."""

import numbers
import typing

import torch

from cutcutcodec.core.opti.cache.basic import basic_cache
from cutcutcodec.core.opti.parallel.threading import TorchThreads


@basic_cache
def _gauss(sigma: float, dtype: torch.dtype) -> torch.Tensor:
    """Compute a gaussian window."""
    radius = int(3.5 * sigma + 0.5)  # same as skimage.metrics.structural_similarity
    gauss = torch.arange(-radius, radius+1, dtype=dtype)
    gauss = torch.exp(-gauss**2 / (2.0 * sigma**2))
    gauss_i, gauss_j = torch.meshgrid(gauss, gauss, indexing="ij")
    gauss = gauss_i * gauss_j
    gauss /= gauss.sum()
    return gauss


@basic_cache
def _gauss_fft(sigma: float, height: int, width: int, dtype: torch.dtype) -> torch.Tensor:
    """Compute the fourier transform of a gaussian window."""
    gauss = _gauss(sigma, dtype)
    pad_height, pad_width = height - gauss.shape[0], width - gauss.shape[1]
    gauss = torch.nn.functional.pad(
        gauss,
        (
            pad_width//2, pad_width-pad_width//2,
            pad_height//2, pad_height-pad_height//2,
        ),
        value=0.0,
    )
    gauss_fft = torch.fft.rfft2(gauss, dim=(1, 0))[:, :, None]
    return gauss_fft


def ssim_conv_torch(
    im1: torch.Tensor,
    im2: torch.Tensor,
    data_range: numbers.Real = 1.0,
    weights: typing.Iterable[float] = None,
    sigma: numbers.Real = 1.5,
    **kwargs,
) -> float:
    """Pure torch implementation of :py:func:`cutcutcodec.core.analysis.video.metric.ssim`.

    It is based on a native torch convolution.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.analysis.video.metric.ssim_torch import ssim_conv_torch
    >>> _ = torch.manual_seed(0)
    >>> im1 = torch.rand(2, 4, 720, 1080, 3)
    >>> im2 = 0.8 * im1 + 0.2 * torch.rand(2, 4, 720, 1080, 3)
    >>> ssim_conv_torch(im1[0, 0], im1[0, 0])
    tensor(1.)
    >>> ssim_conv_torch(im1, im2)
    tensor([[0.9511, 0.9512, 0.9511, 0.9511],
            [0.9512, 0.9512, 0.9511, 0.9512]])
    >>>
    """
    assert isinstance(im1, torch.Tensor), im1.__class__.__name__
    assert isinstance(im2, torch.Tensor), im2.__class__.__name__
    assert im1.ndim == im2.ndim >= 3, (im1.shape, im2.shape)
    assert im1.shape == im2.shape, (im1.shape, im2.shape)
    assert isinstance(data_range, numbers.Real), data_range.__class__.__name__
    data_range = float(data_range)
    assert data_range > 0, data_range
    assert isinstance(sigma, numbers.Real), sigma.__class__.__name__
    sigma = float(sigma)
    assert sigma > 0, sigma
    radius = int(3.5 * sigma + 0.5)  # same as skimage.metrics.structural_similarity
    assert 2*radius + 1 <= im1.shape[-3] and 2*radius + 1 <= im1.shape[-2], \
        "sigma is to big for the image size"

    # cast and normalise weights
    if weights is None:
        weights = [1.0 for _ in range(im1.shape[-1])]
    else:
        weights = [float(w) for w in weights]
        assert len(weights) == im1.shape[-1], (len(weights), im1.shape)
    weights = torch.asarray(weights, dtype=im1.dtype, device=im1.device)
    weights /= weights.sum()

    with TorchThreads(kwargs.get("threads", 0)):
        # convolution kernel
        gauss = _gauss(sigma, im1.dtype).to(im1.device)

        # compute statistics for all patches
        gauss = gauss[None, None, :, :]  # (1, 1, hk, wk)
        shape = im1.shape  # (..., h, w, n)
        im1 = im1.movedim(-1, -3).reshape((-1, 1, shape[-3], shape[-2]))  # (... * n, 1, h, w)
        im2 = im2.movedim(-1, -3).reshape((-1, 1, shape[-3], shape[-2]))  # (... * n, 1, h, w)

        stride = kwargs.get("stride", 1)
        stats = {
            "mu1": torch.nn.functional.conv2d(im1, gauss, stride=stride),
            "mu2": torch.nn.functional.conv2d(im2, gauss, stride=stride),
        }
        stats |= {
            "mu11": stats["mu1"] * stats["mu1"],
            "mu22": stats["mu2"] * stats["mu2"],
            "mu12": stats["mu1"] * stats["mu2"],
        }
        del stats["mu1"], stats["mu2"]
        stats |= {
            "s11": torch.nn.functional.conv2d(im1 * im1, gauss, stride=stride) - stats["mu11"],
            "s22": torch.nn.functional.conv2d(im2 * im2, gauss, stride=stride) - stats["mu22"],
            "s12": torch.nn.functional.conv2d(im1 * im2, gauss, stride=stride) - stats["mu12"],
        }
        # ssim formula
        cst = [(0.01 * data_range)**2, (0.03 * data_range)**2]
        ssim = (
            (2.0*stats["mu12"] + cst[0]) * (2.0*stats["s12"] + cst[1])
        ) / (
            (stats["mu11"] + stats["mu22"] + cst[0]) * (stats["s11"] + stats["s22"] + cst[1])
        )
        ssim = ssim.mean(dim=(-1, -2))  # mean of each layers

        # average
        ssim = ssim.reshape((*shape[:-3], shape[-1]))  # (..., n)
        ssim = (ssim * weights).sum(dim=-1)
        return ssim


def ssim_fft_torch(
    im1: torch.Tensor,
    im2: torch.Tensor,
    data_range: numbers.Real = 1.0,
    weights: typing.Iterable[float] = None,
    sigma: numbers.Real = 1.5,
    **kwargs,
) -> float:
    """Pure torch implementation of :py:func:`cutcutcodec.core.analysis.video.metric.ssim`.

    It is based on fast fft convolution.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.analysis.video.metric.ssim_torch import ssim_conv_torch
    >>> _ = torch.manual_seed(0)
    >>> im1 = torch.rand(2, 4, 720, 1080, 3)
    >>> im2 = 0.8 * im1 + 0.2 * torch.rand(2, 4, 720, 1080, 3)
    >>> ssim_conv_torch(im1[0, 0], im1[0, 0])
    tensor(1.)
    >>> ssim_conv_torch(im1, im2)
    tensor([[0.9511, 0.9512, 0.9511, 0.9511],
            [0.9512, 0.9512, 0.9511, 0.9512]])
    >>>
    """
    assert isinstance(im1, torch.Tensor), im1.__class__.__name__
    assert isinstance(im2, torch.Tensor), im2.__class__.__name__
    assert im1.ndim == im2.ndim >= 3, (im1.shape, im2.shape)
    assert im1.shape == im2.shape, (im1.shape, im2.shape)
    assert isinstance(data_range, numbers.Real), data_range.__class__.__name__
    data_range = float(data_range)
    assert data_range > 0, data_range
    assert isinstance(sigma, numbers.Real), sigma.__class__.__name__
    sigma = float(sigma)
    assert sigma > 0, sigma
    radius = int(3.5 * sigma + 0.5)  # same as skimage.metrics.structural_similarity
    assert 2*radius + 1 <= im1.shape[-3] and 2*radius + 1 <= im1.shape[-2], \
        "sigma is to big for the image size"

    # cast and normalise weights
    if weights is None:
        weights = [1.0 for _ in range(im1.shape[-1])]
    else:
        weights = [float(w) for w in weights]
        assert len(weights) == im1.shape[-1], (len(weights), im1.shape)
    weights = torch.asarray(weights, dtype=im1.dtype, device=im1.device)
    weights /= weights.sum()

    # get gaussian kernel
    g_fft = _gauss_fft(sigma, im1.shape[-3], im1.shape[-2], im1.dtype).to(im1.device)

    with TorchThreads(kwargs.get("threads", 0)):
        # statistic convolutions and crop patches
        stats = {
            "mu1": torch.fft.irfft2(
                g_fft * torch.fft.rfft2(im1, dim=(-2, -3)), dim=(-2, -3)
            )[..., radius:-radius, radius:-radius, :],  # crop patches
            "mu2": torch.fft.irfft2(
                g_fft * torch.fft.rfft2(im2, dim=(-2, -3)), dim=(-2, -3)
            )[..., radius:-radius, radius:-radius, :],  # crop patches
        }
        stats |= {
            "mu11": stats["mu1"] * stats["mu1"],
            "mu22": stats["mu2"] * stats["mu2"],
            "mu12": stats["mu1"] * stats["mu2"],
        }
        del stats["mu1"], stats["mu2"]
        stats |= {
            "s11": torch.fft.irfft2(
                g_fft * torch.fft.rfft2(im1*im1, dim=(-2, -3)), dim=(-2, -3)
            )[..., radius:-radius, radius:-radius, :] - stats["mu11"],
            "s22": torch.fft.irfft2(
                g_fft * torch.fft.rfft2(im2*im2, dim=(-2, -3)), dim=(-2, -3)
            )[..., radius:-radius, radius:-radius, :] - stats["mu22"],
            "s12": torch.fft.irfft2(
                g_fft * torch.fft.rfft2(im1*im2, dim=(-2, -3)), dim=(-2, -3)
            )[..., radius:-radius, radius:-radius, :] - stats["mu12"],
        }

        # ssim formula
        cst = [(0.01 * data_range)**2, (0.03 * data_range)**2]
        ssim = (
            (2.0*stats["mu12"] + cst[0]) * (2.0*stats["s12"] + cst[1])
        ) / (
            (stats["mu11"] + stats["mu22"] + cst[0]) * (stats["s11"] + stats["s22"] + cst[1])
        )
        ssim = ssim.mean(dim=(-2, -3))  # mean of each layers

        # average
        ssim = (ssim * weights).sum(dim=-1)
        return ssim
