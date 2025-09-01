#!/usr/bin/env python3

"""Resize an image."""

from fractions import Fraction
import math
import numbers
import typing

import numpy as np
import torch

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideoWrapper
from .pad import pad_keep_ratio


def _resize_last_dim_area(image: torch.Tensor, size: int) -> torch.Tensor:
    """Resize the last dimension using the area transform.

    It is equivalent to the cv2 resize method with cv2.INTER_AREA interpolation

    .. code-block:: python

        import numpy as np
        import torch

        def _resize_last_dim_area(image: torch.Tensor, size: int) -> torch.Tensor:
            folded_img = image.reshape(-1, image.shape[-1])
            return torch.from_numpy(
                cv2.resize(
                    np.ascontiguousarray(  # cv2 needs it
                        folded_img.numpy(force=True)
                    ),
                    (size, folded_img.shape[0]),  # (width, height)
                    interpolation=cv2.INTER_AREA,
                )
            ).reshape(*image.shape[:-1], size)

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.video.resize import _resize_last_dim_area
    >>>
    >>> _resize_last_dim_area(torch.arange(6, dtype=torch.float32), 8)  # nearest
    tensor([0., 1., 1., 2., 3., 4., 4., 5.])
    >>> _resize_last_dim_area(torch.arange(8, dtype=torch.float32), 6)  # general
    tensor([0.2500, 1.5000, 2.7500, 4.2500, 5.5000, 6.7500])
    >>> _resize_last_dim_area(torch.arange(8, dtype=torch.float32), 4)  # conv
    tensor([0.5000, 2.5000, 4.5000, 6.5000])
    >>>
    >>> img = torch.empty(8, requires_grad=True)
    >>> _resize_last_dim_area(img, 6).sum().backward()
    >>> img.grad
    tensor([0.7500, 0.7500, 0.7500, 0.7500, 0.7500, 0.7500, 0.7500, 0.7500])
    >>>
    """
    # shortcut case where stride is integral
    if image.shape[-1] % size == 0:
        stride = image.shape[-1] // size
        return torch.nn.functional.conv1d(
            image.reshape(-1, 1, image.shape[-1]),
            torch.full((1, 1, stride), 1.0/stride, dtype=image.dtype, device=image.device),
            stride=stride,
        ).reshape(*image.shape[:-1], size)

    # find the pixels boundaries
    bounds = torch.linspace(
        0.0,
        image.shape[-1],
        size + 1,
        dtype=image.dtype,
        device=image.device,
    )

    # shortcuts case nearest
    if size >= image.shape[-1]:
        return image[..., torch.floor(0.5*(bounds[:-1]+bounds[1:])).to(torch.int64)]

    # general case
    out = torch.empty((*image.shape[:-1], size), dtype=image.dtype, device=image.device)
    for i, (bmin, bmax) in enumerate(zip(bounds[:-1].tolist(), bounds[1:].tolist())):
        slices: list[torch.Tensor] = []
        # lower bound
        bound = math.ceil(bmin)
        if factor := bound - bmin:
            slices.append(image[..., bound-1] * factor)
        bmin = bound
        # higher bound
        bound = math.floor(bmax)
        if factor := bmax - bound:
            slices.append(image[..., bound] * factor)
        bmax = bound
        # middle
        if bmax != bmin:
            # slices.append(image[..., range(bmin, bmax)].sum(dim=-1))
            slices.append(image[..., bmin:bmax].sum(dim=-1))
        # final sum
        out[..., i] = sum(slices)
    out *= float(size) / float(image.shape[-1])
    return out


def _resize_last_dim_cubic(image: torch.Tensor, size: int) -> torch.Tensor:
    """Resize the last dimension with a cubic filter.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.video.resize import _resize_last_dim_cubic
    >>>
    >>> _resize_last_dim_cubic(torch.arange(6, dtype=torch.float32), 8)
    tensor([-0.0479,  0.5811,  1.3750,  2.1250,  2.8750,  3.6250,  4.4189,  5.0479])
    >>> _resize_last_dim_cubic(torch.arange(8, dtype=torch.float32), 6)  # general
    tensor([0.1088, 1.5000, 2.8333, 4.1667, 5.5000, 6.8912])
    >>>
    >>> img = torch.empty(8, requires_grad=True)
    >>> _resize_last_dim_cubic(img, 6).sum().backward()
    >>> img.grad
    tensor([0.8171, 0.6829, 0.6829, 0.8171, 0.8171, 0.6829, 0.6829, 0.8171])
    >>>
    """
    # searching for the position of neighboring pixels
    half_stride = 0.5 * float(image.shape[-1]) / float(size)
    middle = torch.linspace(
        half_stride,
        image.shape[-1] - half_stride,
        size,
        dtype=image.dtype,
        device=image.device,

    )
    middle_floor = torch.floor(middle)

    # extracts the pixels concerned
    middle_floor_int = middle_floor.to(torch.int64)[:, None]
    neighborhood = image[  # shape (..., size, 5)
        ...,
        torch.cat(
            [
                middle_floor_int - 2,
                middle_floor_int - 1,
                middle_floor_int,
                middle_floor_int + 1,
                middle_floor_int + 2,
            ],
            dim=-1,
        ).clamp(0, image.shape[-1]-1),
    ]
    middle = ((middle_floor + 0.5) - middle)[:, None]
    middle = torch.cat(  # relative position of neighbors
        [
            middle - 2.0,
            middle - 1.0,
            middle,
            middle + 1.0,
            middle + 2.0,
        ],
        dim=-1,
    )

    # searching for coeficients
    def _sub_window(pos: torch.Tensor, interval: str) -> torch.Tensor:
        alpha = -0.5
        match interval:
            case "x<=1":
                pos2 = pos * pos
                return (alpha + 2.0)*pos2*pos - (alpha+3.0)*pos2 + 1.0
            case "1<x<2":
                pos2 = pos * pos
                return alpha*pos2*pos - 5.0*alpha*pos2 + 8.0*alpha*pos - 4.0*alpha
            case _:
                return 0.0
    weights = abs(middle)
    cond_a = weights <= 1.0
    cond_b = (~cond_a) & (weights < 2.0)
    cond_c = weights >= 2.0
    weights[cond_a] = _sub_window(weights[cond_a], "x<=1")
    weights[cond_b] = _sub_window(weights[cond_b], "1<x<2")
    weights[cond_c] = _sub_window(weights[cond_c], "x>=2")

    # apply convolution
    return (neighborhood * weights).sum(dim=-1)


def _resize_last_dim_spectral(image: torch.Tensor, size: int) -> torch.Tensor:
    """Resize the last dimension using the fourier transform."""
    fft = torch.fft.rfft(image, dim=-1, norm="forward")
    fft = fft[..., :size//2+1]  # shrink
    win = torch.hann_window(
        2*fft.shape[-1]-1, periodic=False, dtype=image.dtype, device=image.device
    )[fft.shape[-1]-1:]
    fft *= win  # on last dim
    return torch.fft.irfft(fft, size, dim=-1, norm="forward")  # enlarge


def _resize_last_dim(image: torch.Tensor, size: int, method: None | str) -> torch.Tensor:
    """Resize the last dimension of the image."""
    if method is None:
        method = "area" if size < image.shape[-1] else "cubic"
    match method:
        case "area":
            image = _resize_last_dim_area(image, size)
        case "cubic":
            image = _resize_last_dim_cubic(image, size)
        case "spectral":
            image = _resize_last_dim_spectral(image, size)
        case _:
            raise ValueError(f"unknowned method {method}")
    return image


def _resize(
    image: torch.Tensor, shape: tuple[int, ...], copy: bool, method: None | str
) -> torch.Tensor:
    """Kernel of ``resize``.

    Parameters
    ----------
    image : torch.Tensor
        A floating point torch tensor of n dimension.
    shape : tuple[int]
        The final shape, requires the same number of dimension than ``image``.
    copy : boolean
        If True, ensure the input image is keep intact.
    method : None or str
        Transmitted to ``_resize_last_dim``.

    Returns
    -------
    resized : torch.Tensor
        The resized image with the new shape ``shape``.

    Notes
    -----
    * No verifications are performed for performance reason.
    * Not compared to torch.nn.functional.interpolate
    * The returned tensor can be a reference of the provided tensor if copy is False.
    * This function is torch differentiable
    * The reshape is performed independently on each axis (separable transformations).
    """
    is_resized = False
    items = [  # the final volume for each dim
        np.prod((*image.shape[:i-1], s, *image.shape[i+1:]))
        for i, s in enumerate(shape)
    ]
    for dim in sorted(range(len(shape)), key=items.__getitem__):  # strong reduction first
        if image.shape[dim] != shape[dim]:
            is_resized = True
            image = _resize_last_dim(
                image.movedim(dim, -1), shape[dim], method
            ).movedim(-1, dim)
    if copy and not is_resized:
        image = image.clone()
    return image


def resize(
    image: FrameVideo | torch.Tensor | np.ndarray,
    shape: tuple[numbers.Integral, ...] | list[numbers.Integral],
    copy: bool = True,
    method: typing.Optional[str] = None,
) -> FrameVideo | torch.Tensor | np.ndarray:
    """Reshape the image, can introduce a deformation.

    Parameters
    ----------
    image : cutcutcodec.core.classes.image_video.FrameVideo or torch.Tensor or numpy.ndarray
        The image to be resized, of any shape.
        It has to match with the video image specifications.
    shape : list[int]
        The pixel dimensions of the returned image.
        As this function is separable, it works in n dimensions.
        Batch dimensions are considered at the end so as to be consistent with images.
        The special value None, means we consider this dimension as a batch dimension.
    copy : boolean, default=True
        If True, ensure that the returned tensor doesn't share the data of the input tensor.
    method : str, optional
        Can be ``spectral``, ``area`` or ``cubic``.
        By default, the choice is made for each dimension depending on if it is enlarged or reduced.

    Returns
    -------
    resized_image : arraylike
        The resized image homogeneous with the input.
        The underground data are not shared with the input. A safe copy is done.

    Notes
    -----
    * Thanks to its 100% torch implementation, this function is differentiable.
    * Unless you force the ``cubic`` filter for big downscaling ratio,
      this function does not generate aliasing (moire).

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.video.resize import resize
    >>> image = torch.empty(480, 720, 3)
    >>> resize(image, (720, 1080)).shape  # upscaling
    torch.Size([720, 1080, 3])
    >>> resize(image, (480, 360)).shape  # downscaling
    torch.Size([480, 360, 3])
    >>>
    """
    # case cast homogeneous
    if isinstance(image, FrameVideo):
        return FrameVideo(
            image.time, resize(torch.Tensor(image), shape, copy=copy, method=method)
        )
    if isinstance(image, np.ndarray):
        return resize(
            torch.from_numpy(image), shape, copy=copy, method=method
        ).numpy(force=True)

    # case integer input
    assert isinstance(image, torch.Tensor), image.__class__.__name__
    if not torch.is_floating_point(image):
        return resize(
            image.to(torch.float32), shape, copy=False, method=method
        ).round().to(image.dtype)

    # pad shape
    assert isinstance(shape, (tuple, list)), shape.__class__.__name__
    assert len(shape) <= image.ndim, (shape, image.shape)
    assert all(s is None or isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape
    full_shape = list(image.shape)
    for i, s in enumerate(shape):
        if s is not None:
            full_shape[i] = s

    # last verifications
    assert isinstance(copy, bool), copy.__class__.__name__
    assert image.dtype in {torch.float32, torch.float64}
    assert isinstance(method, (None | str)), method.__class__.__name__

    # resize
    return _resize(image, shape, copy=copy, method=method)


def resize_pad(
    image: FrameVideo | torch.Tensor | np.ndarray,
    shape: tuple[numbers.Integral, ...] | list[numbers.Integral],
    copy: bool = True,
    method: typing.Optional[str] = None,
) -> FrameVideo | torch.Tensor | np.ndarray:
    """Reshape the image, keep the ratio and pad with 0.

    Parameters
    ----------
    image, shape, copy, method
        Transmitted to :py:func`resize`.

    Returns
    -------
    resized_image : arraylike
        The zeropadded resize image from :py:func`resize`.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.video.resize import resize_pad
    >>> image = torch.ones((4, 8))
    >>> resize_pad(image, (8, 9)).round(decimals=1)  # upscale
    tensor([[0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0.]])
    >>> resize_pad(image, (4, 4)).round(decimals=1)  # downscale
    tensor([[0., 0., 0., 0.],
            [1., 1., 1., 1.],
            [1., 1., 1., 1.],
            [0., 0., 0., 0.]])
    >>> resize_pad(image, (6, 6)).round(decimals=1)  # mix
    tensor([[0., 0., 0., 0., 0., 0.],
            [1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1.],
            [0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0.]])
    >>>
    """
    # case cast homogeneous
    if isinstance(image, FrameVideo):
        return FrameVideo(
            image.time, resize_pad(torch.Tensor(image), shape, copy=copy, method=method)
        )
    if isinstance(image, np.ndarray):
        return resize_pad(
            torch.from_numpy(image), shape, copy=copy, method=method
        ).numpy(force=True)

    # case integer input
    assert isinstance(image, torch.Tensor), image.__class__.__name__
    if not torch.is_floating_point(image):
        return resize_pad(
            image.to(torch.float32), shape, copy=False, method=method
        ).round().to(image.dtype)

    # pad shape
    assert isinstance(shape, (tuple, list)), shape.__class__.__name__
    assert len(shape) <= image.ndim, (shape, image.shape)
    assert all(s is None or isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape
    full_shape = list(image.shape)
    for i, s in enumerate(shape):
        if s is not None:
            full_shape[i] = s

    # search for the optimum undersize for distortion-free reshaping
    zoom = min(
        final / original
        for final, original
        in zip(shape, image.shape)
        if final is not None
    ) if any(s is not None for s in shape) else 1
    shape = shape + (None,) * (len(full_shape) - len(shape))
    sub_shape = [  # sub_shape <= full_shape
        round(o*zoom) if s is not None else o for o, s in zip(image.shape, shape)
    ]

    # resize
    sub_image = resize(image, sub_shape, copy, method)

    # pad
    if full_shape == sub_shape:
        return sub_image
    image = torch.zeros(*full_shape, dtype=image.dtype, device=image.device)
    image[tuple(slice((f-s)//2, (f-s)//2 + s) for f, s in zip(full_shape, sub_shape))] = sub_image

    return image


def resize_keep_ratio(
    image: FrameVideo | torch.Tensor | np.ndarray,
    shape: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
    copy: bool = True,
) -> FrameVideo | torch.Tensor | np.ndarray:
    """Reshape the image, keep the aspact ratio and pad with transparent pixels.

    Parameters
    ----------
    image : cutcutcodec.core.classes.image_video.FrameVideo or torch.Tensor or numpy.ndarray
        Transmitted to ``cutcutcodec.core.filter.video.resize.resize``.
    shape : int and int
        Transmitted to ``cutcutcodec.core.filter.video.resize.resize``.
    copy : boolean, default=True
        Transmitted to ``cutcutcodec.core.filter.video.resize.resize``.

    Returns
    -------
    resized_image
        The resized (and padded) image homogeneous with the input.
        The underground data are not shared with the input. A safe copy is done.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.classes.frame_video import FrameVideo
    >>> from cutcutcodec.core.filter.video.resize import resize_keep_ratio
    >>> ref = FrameVideo(0, torch.full((4, 8, 1), 0.5))
    >>>
    >>> # upscale
    >>> resize_keep_ratio(ref, (8, 9))[..., 1]  # alpha layer
    tensor([[0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1., 1., 1., 1.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0., 0., 0., 0.]])
    >>> resize_keep_ratio(ref, (8, 9)).convert(1)[..., 0]  # as gray
    tensor([[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])
    >>>
    >>> # downscale
    >>> resize_keep_ratio(ref, (4, 4))[..., 1]  # alpha layer
    tensor([[0., 0., 0., 0.],
            [1., 1., 1., 1.],
            [1., 1., 1., 1.],
            [0., 0., 0., 0.]])
    >>> resize_keep_ratio(ref, (4, 4)).convert(1)[..., 0]  # as gray
    tensor([[0.0000, 0.0000, 0.0000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000],
            [0.5000, 0.5000, 0.5000, 0.5000],
            [0.0000, 0.0000, 0.0000, 0.0000]])
    >>>
    >>> # mix
    >>> resize_keep_ratio(ref, (6, 6))[..., 1]  # alpha layer
    tensor([[0., 0., 0., 0., 0., 0.],
            [1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1., 1.],
            [0., 0., 0., 0., 0., 0.],
            [0., 0., 0., 0., 0., 0.]])
    >>> resize_keep_ratio(ref, (6, 6)).convert(1)[..., 0]  # as gray
    tensor([[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.5000, 0.5000, 0.5000, 0.5000, 0.5000, 0.5000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])
    >>>
    """
    # minimalist verifications
    assert isinstance(image, (FrameVideo, torch.Tensor, np.ndarray)), image.__class__.__name__
    assert image.ndim >= 2, image.shape
    assert image.shape[0] >= 1, image.shape
    assert image.shape[1] >= 1, image.shape
    assert isinstance(shape, (tuple, list)), shape.__class__.__name__
    assert len(shape) == 2, len(shape)
    assert all(isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape

    # find the shape for keeping proportion
    dw_sh, dh_sw = shape[1]*image.shape[0], shape[0]*image.shape[1]
    if dw_sh < dh_sw:  # need vertical padding
        height, width = (round(dw_sh/image.shape[1]), shape[1])  # keep width unchanged
    elif dw_sh > dh_sw:  # need horizontal padding
        height, width = (shape[0], round(dh_sw/image.shape[0]))  # keep height unchanged
    else:  # if the proportion is the same
        return resize(image, shape, copy=copy)

    # resize and pad
    image = resize(image, (height, width), copy=copy)
    image = pad_keep_ratio(image, shape, copy=False)
    return image


class FilterVideoResize(Filter):
    """Frozen the shape of the input stream.

    Attributes
    ----------
    keep_ratio : boolean
        True if the aspect ratio is keep, False otherwise (readonly).
    shape : tuple[int, int]
        The pixel dimensions of the incoming frames (readonly).
        The convention adopted is the numpy convention (height, width).

    Examples
    --------
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>> from cutcutcodec.core.filter.video.resize import FilterVideoResize
    >>> (stream_in,) = GeneratorVideoNoise(0).out_streams
    >>>
    >>> # keep ratio
    >>> (stream_out,) = FilterVideoResize([stream_in], (4, 6), keep_ratio=True).out_streams
    >>> stream_out.snapshot(0, (8, 9)).convert(1)[..., 0]
    tensor([[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.5015, 0.3601, 0.2768, 0.4685, 0.4546, 0.3331, 0.1891, 0.1735, 0.2044],
            [0.4523, 0.5208, 0.5630, 0.4766, 0.4537, 0.4693, 0.5037, 0.4720, 0.4302],
            [0.4456, 0.6390, 0.7626, 0.5313, 0.5097, 0.6107, 0.7642, 0.7114, 0.6111],
            [0.5774, 0.4947, 0.4757, 0.6791, 0.6862, 0.6147, 0.5743, 0.5051, 0.4508],
            [0.7587, 0.4848, 0.2671, 0.4603, 0.6309, 0.6531, 0.3800, 0.4586, 0.6211],
            [0.8938, 0.5200, 0.1532, 0.2005, 0.5209, 0.6884, 0.2492, 0.4770, 0.8364],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])
    >>> stream_out.snapshot(0, (4, 3)).convert(1)[..., 0]
    tensor([[0.0000, 0.0000, 0.0000],
            [0.5060, 0.4730, 0.4557],
            [0.5078, 0.5852, 0.4931],
            [0.0000, 0.0000, 0.0000]])
    >>> stream_out.snapshot(0, (6, 5)).convert(1)[..., 0]
    tensor([[0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.4672, 0.4393, 0.4528, 0.3705, 0.3279],
            [0.5374, 0.5901, 0.5939, 0.6267, 0.5536],
            [0.6929, 0.2912, 0.5406, 0.4344, 0.6335],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])
    >>>
    >>> # deformation
    >>> (stream_out,) = FilterVideoResize([stream_in], (4, 6), keep_ratio=False).out_streams
    >>> stream_out.snapshot(0, (8, 9))[..., 0]
    tensor([[0.5146, 0.2584, 0.1589, 0.6604, 0.9134, 0.8677, 0.4371, 0.5266, 0.7497],
            [0.5348, 0.3804, 0.3074, 0.5675, 0.8136, 0.8771, 0.5687, 0.5198, 0.5689],
            [0.5773, 0.6446, 0.6297, 0.3658, 0.5970, 0.8972, 0.8539, 0.5059, 0.1791],
            [0.4754, 0.6997, 0.7720, 0.2800, 0.4951, 0.8862, 0.9495, 0.5726, 0.1836],
            [0.2292, 0.5456, 0.7344, 0.3101, 0.5080, 0.8442, 0.8555, 0.7199, 0.5824],
            [0.3240, 0.5421, 0.6590, 0.3248, 0.5113, 0.7935, 0.7588, 0.7522, 0.7550],
            [0.7597, 0.6892, 0.5460, 0.3241, 0.5050, 0.7342, 0.6594, 0.6693, 0.7013],
            [0.9610, 0.7573, 0.4940, 0.3237, 0.5022, 0.7071, 0.6138, 0.6307, 0.6755]])
    >>> stream_out.snapshot(0, (4, 3))[..., 0]
    tensor([[0.3241, 0.8210, 0.5574],
            [0.6841, 0.5580, 0.5189],
            [0.4824, 0.5418, 0.7596],
            [0.7261, 0.5123, 0.6448]])
    >>> stream_out.snapshot(0, (6, 5))[..., 0]
    tensor([[0.4299, 0.3247, 0.8362, 0.5725, 0.6687],
            [0.5435, 0.4817, 0.6905, 0.7399, 0.4282],
            [0.5791, 0.6316, 0.5412, 0.8879, 0.3034],
            [0.3243, 0.5981, 0.5424, 0.8160, 0.6793],
            [0.5586, 0.5305, 0.5261, 0.7136, 0.7296],
            [0.8669, 0.4743, 0.5106, 0.6358, 0.6608]])
    >>>
    """

    def __init__(
        self,
        in_streams: typing.Iterable[Stream],
        shape: tuple[numbers.Integral, numbers.Integral] | list[numbers.Integral],
        keep_ratio: bool = False,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        shape : tuple[int, int]
            The pixel dimensions of the incoming frames.
            The convention adopted is the numpy convention (height, width).
        keep_ratio : boolean, default=False
            If True, the returned frame is padded to keep the proportion of the incoming frame.
        """
        assert isinstance(shape, (tuple, list)), shape.__class__.__name__
        assert len(shape) == 2, len(shape)
        assert all(isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape
        assert isinstance(keep_ratio, bool), keep_ratio.__class__.__name__
        self._shape = (int(shape[0]), int(shape[1]))
        self._keep_ratio = keep_ratio

        super().__init__(in_streams, in_streams)
        super().__init__(
            in_streams, [_StreamVideoResize(self, index) for index in range(len(in_streams))]
        )

    def _getstate(self) -> dict:
        return {
            "keep_ratio": self.keep_ratio,
            "shape": list(self.shape),
        }

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"keep_ratio", "shape"}, set(state)
        FilterVideoResize.__init__(self, in_streams, state["shape"], keep_ratio=state["keep_ratio"])

    @property
    def keep_ratio(self) -> bool:
        """Return True if the aspect ratio is keep, False otherwise."""
        return self._keep_ratio

    @property
    def shape(self) -> tuple[int, int]:
        """Return The pixel dimensions of the incoming frames."""
        return self._shape


class _StreamVideoResize(StreamVideoWrapper):
    """Translate a video stream from a certain delay."""

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        in_mask = torch.full(self.node.shape, True, dtype=bool)
        src = self.stream._snapshot(timestamp, in_mask)  # pylint: disable=W0212
        dst = (
            resize_keep_ratio(src, mask.shape)
            if self.node.keep_ratio else
            resize(src, mask.shape)
        )
        return dst
