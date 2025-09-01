#!/usr/bin/env python3

"""Image metrics."""

from fractions import Fraction
import math
import numbers
import pathlib
import typing

import numpy as np
import torch
import tqdm

from cutcutcodec.core.analysis.stream.rate_video import optimal_rate_video
from cutcutcodec.core.analysis.stream.shape import optimal_shape_video
from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.io import read
from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
from cutcutcodec.core.opti.parallel import map as threaded_map, starmap
from .utils import batched_comparative_frames, batched_single_frames
from .vmaf import vmaf


__all__ = ["lpips", "psnr", "ssim", "uvq", "vmaf"]


def _batch_frames(frames: typing.Iterable[tuple]) -> tuple:
    """Gather frames in 128 MB batches."""
    nb_pix = 0  # the number of pixel in one frame
    batch_ref, batch_dis = [], []
    for frame_ref, frame_dis in frames:
        if not nb_pix:
            nb_pix = frame_ref.shape[0] * frame_ref.shape[1]
        batch_ref.append(frame_ref.unsqueeze(0))
        batch_dis.append(frame_dis.unsqueeze(0))
        # 128e6 (MB) / 3 (channels) / 4 (bytes per float32) / 2 (batches)
        if len(batch_ref) >= math.ceil(5.33e6 / nb_pix):
            yield torch.cat(batch_ref, dim=0), torch.cat(batch_dis, dim=0)
            batch_ref, batch_dis = [], []
    if batch_ref:
        yield torch.cat(batch_ref, dim=0), torch.cat(batch_dis, dim=0)


def _compare(batch_ref: torch.Tensor, batch_dis: torch.Tensor, kwargs: dict) -> dict:
    """Compare the 2 batches with the different metrics."""
    res = {}

    def to4(data: list[float]) -> list[float]:
        return [round(e, 4) for e in data]

    if kwargs.get("lpips_alex", False) or kwargs.get("lpips_vgg", False):
        # values comes from cutcutcodec.convert("y'pbpr_srgb", "r'g'b'_srgb")
        yuv2rgb = torch.asarray(
            [[1.0, 0.0, 1.57470437321727],
             [1.0, -0.187265223648174, -0.468214772280861],
             [1.0, 1.85565392184996, 0.0]],
            dtype=batch_ref.dtype,
            device=batch_ref.device,
        )
        ref_rgb = (yuv2rgb @ batch_ref.unsqueeze(-1)).squeeze(-1)
        dis_rgb = (yuv2rgb @ batch_dis.unsqueeze(-1)).squeeze(-1)
        if kwargs.get("lpips_alex", False):
            res["lpips_alex"] = to4(lpips(ref_rgb, dis_rgb, net=kwargs["lpips_alex_net"]).tolist())
        if kwargs.get("lpips_vgg", False):
            res["lpips_vgg"] = to4(lpips(ref_rgb, dis_rgb, net=kwargs["lpips_vgg_net"]).tolist())
    if kwargs.get("psnr", False):
        # the factors comes from https://github.com/fraunhoferhhi/vvenc/wiki/Encoder-Performance
        res["psnr"] = to4(psnr(batch_ref, batch_dis, weights=(6, 1, 1)).tolist())
    if kwargs.get("ssim", False):
        # the factors comes from https://github.com/fraunhoferhhi/vvenc/wiki/Encoder-Performance
        res["ssim"] = to4(ssim(batch_ref, batch_dis, weights=(6, 1, 1), data_range=1.0).tolist())
    if kwargs.get("vmaf", False):
        res["vmaf"] = to4(vmaf(batch_ref, batch_dis).tolist())
    return res


def _yield_frames(ref: pathlib.Path, dis: pathlib.Path) -> tuple:
    """Read frames 2 by 2."""
    # find colorspace
    with ContainerInputFFMPEG(ref) as cont_ref:
        stream_ref = cont_ref.out_select("video")[0]
        colorspace = stream_ref.colorspace
    colorspace = Colorspace("y'pbpr", colorspace.primaries, colorspace.transfer)
    with (
        read(ref, colorspace=colorspace) as cont_ref,
        read(dis, colorspace=colorspace) as cont_dis,
    ):
        stream_ref = cont_ref.out_select("video")[0]
        stream_dis = cont_dis.out_select("video")[0]
        rate = optimal_rate_video(stream_ref) or Fraction(3000, 1001)
        shape = optimal_shape_video(stream_ref) or (720, 1080)
        duration = min(stream_ref.duration, stream_dis.duration)
        times = (
            [0] if math.isinf(duration) else
            np.arange(0.5/rate, float(duration), 1.0/rate).tolist()
        )
        if len(times) == 1:
            yield stream_ref.snapshot(times[0], shape), stream_dis.snapshot(times[0], shape)
        else:
            yield from tqdm.tqdm(
                threaded_map(
                    lambda t: (stream_ref.snapshot(t, shape), stream_dis.snapshot(t, shape)),
                    times,
                ),
                desc="compare",
                total=len(times),
                unit="img",
            )


def _yield_frames_uvq(video: pathlib.Path) -> torch.Tensor:
    """Read the video at 5 fps in sRGB of shape 1280x720."""
    rate = 5
    with read(video, colorspace=Colorspace("r'g'b'", "srgb", "srgb")) as cont:
        stream = cont.out_select("video")[0]
        duration = stream.duration
        times = (
            [0] if math.isinf(duration) else
            np.arange(0.0, float(duration), 1.0/rate).tolist()
        )
        batch = []
        for frame in tqdm.tqdm(
            threaded_map(lambda t: stream.snapshot(t, (720, 1280)).convert(3), times),
            desc="uvq",
            total=len(times),
            unit="img",
        ):
            batch.append(frame)
            if len(batch) == rate:
                yield torch.cat([torch.Tensor(f)[None, :, :, :] for f in batch], dim=0)
                batch = []
        if batch:
            while len(batch) < rate:
                batch.append(batch[-1])
            yield torch.cat([torch.Tensor(f)[None, :, :, :] for f in batch], dim=0)


def compare(
    ref: pathlib.Path | str | bytes, dis: pathlib.Path | str | bytes, **kwargs
) -> dict[str, list[float]]:
    """Compare 2 video files with differents metrics.

    Parameters
    ----------
    ref : pathlike
        The reference video file.
    dis : pathlike
        The distorted video.
    lpips_alex : boolean, default=False
        If True, compute the lpips with alex (medium).
    lpips_vgg : boolean, default=False
        If True, compute the lpips with vgg (slow).
    psnr : boolean, dafault=False
        If True, compute the psnr (very fast).
    ssim : boolean, default=False
        If True, compute the ssim (slow).
    uvq : boolean, default=False
        If True, compute the uvq on the `dis` video (very slow).
        It returns only one value per second.
        If you want to compute this metric only, give ``None`` to `ref`.
    vmaf : boolean, default=False
        If True, compute the vmaf (medium).

    Returns
    -------
    metrics : dict[str, list[float]]
        Each metric name is associated with the scalar value of each frame.
        All the numbers are rounded to 4 decimals number.

    Notes
    -----
    Frames are converted to yuv if not already converted,
    then the distorted video is converted to the color space of the reference video.

    Examples
    --------
    >>> import pprint
    >>> from cutcutcodec.core.analysis.video.metric import compare
    >>> res = compare("media/video/intro.webm", "media/video/intro.webm", psnr=True, ssim=True)
    >>> pprint.pprint(res)  # doctest: +ELLIPSIS
    {'psnr': [100.0,
              100.0,
              ...,
              100.0,
              100.0],
     'ssim': [1.0,
              1.0,
              ...,
              1.0,
              1.0]}
    >>>
    """
    dis = pathlib.Path(dis).expanduser()
    metrics = {}
    if any(kwargs.get(m, False) for m in ["lpips_alex", "lpips_vgg", "psnr", "ssim", "vmaf"]):
        ref = pathlib.Path(ref).expanduser()
        if kwargs.get("lpips_alex", False):
            from .lpips_torch import _get_lpips_model
            kwargs["lpips_alex_net"] = _get_lpips_model("alex")
        if kwargs.get("lpips_vgg", False):
            from .lpips_torch import _get_lpips_model
            kwargs["lpips_vgg_net"] = _get_lpips_model("vgg")
        for batch_metrics in starmap(
            _compare,
            ((r, d, kwargs) for r, d in _batch_frames(_yield_frames(ref, dis))),
        ):
            if not metrics:
                metrics = batch_metrics
            else:
                for key, metric in metrics.items():
                    metric.extend(batch_metrics[key])
    if kwargs.get("uvq", False):
        from .uvq_google.inference import UVQInference
        model = UVQInference()
        metrics["uvq"] = []
        for batch in _yield_frames_uvq(dis):
            metrics["uvq"].append(round(float(uvq(batch, _model=model)), 4))
    return metrics


@batched_comparative_frames
def lpips(ref: torch.Tensor, dis: torch.Tensor, *args, **kwargs) -> torch.Tensor:
    """Compute the Learned Perceptual Image Patch Similarity.

    It uses the module ``pip install lpips`` in backend, based on torch.

    Parameters
    ----------
    ref, dis : arraylike
        The 2 images to be compared, of shape ([*batch], height, width, channels).
        The frames are assumed to be in RGB in range [0, 1].
        Gamut and EOTF must be standard rgb.
    net : str, default="alex"
        The neuronal network used, "alex" or "vgg".
    threads : int, optional
        Defines the number of threads.
        The value -1 means that the function uses as many calculation threads as there are cores.
        The default value (0) allows the same behavior as (-1) if the function
        is called in the main thread, otherwise (1) to avoid nested threads.
        Any other positive value corresponds to the number of threads used.

    Returns
    -------
    lpips : arraylike
        The learned perceptual image patch similarity of each layers.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.metric import lpips
    >>> np.random.seed(0)
    >>> ref = np.random.random((720, 1080, 3))  # It could also be a torch array list...
    >>> dis = 0.8 * ref + 0.2 * np.random.random((720, 1080, 3))
    >>> lpips(ref, dis).round(1)
    np.float64(0.0)
    >>>
    """
    from .lpips_torch import lpips_torch
    dtype = ref.dtype
    ref, dis = ref.to(torch.float32), dis.to(torch.float32)
    return lpips_torch(ref, dis, *args, **kwargs).to(dtype)


@batched_comparative_frames
def psnr(ref: torch.Tensor, dis: torch.Tensor, *args, **kwargs) -> torch.Tensor:
    """Compute the peak signal to noise ratio of 2 images.

    Parameters
    ----------
    ref, dis : arraylike
        The 2 images to be compared, of shape ([*batch], height, width, channels).
        Supported types are float32 and float64.
    weights : iterable[float], optional
        The relative weight of each channel. By default, all channels have the same weight.
    threads : int, optional
        Defines the number of threads.
        The value -1 means that the function uses as many calculation threads as there are cores.
        The default value (0) allows the same behavior as (-1) if the function
        is called in the main thread, otherwise (1) to avoid nested threads.
        Any other positive value corresponds to the number of threads used.

    Returns
    -------
    psnr : arraylike
        The global peak signal to noise ratio,
        as a ponderation of the mean square error of each channel.
        It is batched and clamped in [0, 100] db.

    Notes
    -----
    * It is optimized for C contiguous tensors.
    * If device is cpu and gradient is not required, a fast C code is used instead of torch code.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.metric import psnr
    >>> np.random.seed(0)
    >>> ref = np.random.random((720, 1080, 3))  # It could also be a torch array list...
    >>> dis = 0.8 * ref + 0.2 * np.random.random((720, 1080, 3))
    >>> psnr(ref, dis).round(1)
    np.float64(21.8)
    >>>
    """
    if (
        ref.requires_grad or dis.requires_grad
        or ref.device.type != "cpu" or dis.device.type != "cpu"
    ):
        from .psnr_torch import psnr_torch
        return psnr_torch(ref, dis, *args, **kwargs)
    from .metric import psnr as psnr_c
    return torch.asarray(
        [psnr_c(r, d, *args, **kwargs) for r, d in zip(ref.numpy(), dis.numpy())],
        dtype=ref.dtype,
    )


@batched_comparative_frames
def ssim(ref: torch.Tensor, dis: torch.Tensor, *args, stride: int = 1, **kwargs) -> torch.Tensor:
    """Compute the Structural similarity index measure of 2 images.

    Parameters
    ----------
    ref, dis : arraylike
        The 2 images to be compared, of shape ([*batch], height, width, channels).
        Supported types are float32 and float64.
    data_range : float, default=1.0
        The data range of the input image (difference between maximum and minimum possible values).
    weights : iterable[float], optional
        The relative weight of each channel. By default, all channels have the same weight.
    sigma : float, default=1.5
        The standard deviation of the gaussian. It has to be strictely positive.
    stride : int, default=1
        The stride of the convolving kernel.
    threads : int, optional
        Defines the number of threads.
        The value -1 means that the function uses as many calculation threads as there are cores.
        The default value (0) allows the same behavior as (-1) if the function
        is called in the main thread, otherwise (1) to avoid nested threads.
        Any other positive value corresponds to the number of threads used.

    Returns
    -------
    ssim : arraylike
        The ponderated structural similarity index measure of each layers.

    Notes
    -----
    * It is optimized for C contiguous tensors.
    * If device is cpu, gradient is not required and stride != 1, a fast C code is used.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.metric import ssim
    >>> np.random.seed(0)
    >>> ref = np.random.random((720, 1080, 3))  # It could also be a torch array list...
    >>> dis = 0.8 * ref + 0.2 * np.random.random((720, 1080, 3))
    >>> ssim(ref, dis).round(2)
    np.float64(0.95)
    >>>
    """
    assert isinstance(stride, numbers.Integral), stride.__class__.__name__
    if stride == 1:
        from .ssim_torch import ssim_fft_torch
        return ssim_fft_torch(ref, dis, *args, **kwargs)
    if (
        ref.requires_grad or dis.requires_grad
        or ref.device.type != "cpu" or dis.device.type != "cpu"
    ):
        from .ssim_torch import ssim_conv_torch
        return ssim_conv_torch(ref, dis, *args, stride=stride, **kwargs)
    from .metric import ssim as ssim_c
    return torch.asarray(
        [ssim_c(r, d, *args, stride=stride, **kwargs) for r, d in zip(ref.numpy(), dis.numpy())],
        dtype=ref.dtype,
    )


@batched_single_frames
def uvq(dis: torch.Tensor, _model=None) -> torch.Tensor:
    """Compute the Perceptual Video Quality.

    Parameters
    ----------
    dis : arraylike
        The frames to be evaluated, of shape ([*batch], fps=5, height, width, channels=3).
        The framerate is assumed to be 5 Hz.
        The frames are assumed to be in RGB in range [0, 1].
        Gamut and EOTF must be standard rgb.

    Returns
    -------
    uvq : arraylike
        The perceptual video quality measure for each group of 5 images.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.metric import uvq
    >>> np.random.seed(0)
    >>> dis = np.random.random((5, 720, 1080, 3))  # It could also be a torch array list...
    >>> uvq(dis).round(1)
    np.float32(3.3)
    >>>
    """
    if _model is None:
        from .uvq_google.inference import UVQInference
        _model = UVQInference()
    return _model.forward(dis)
