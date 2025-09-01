#!/usr/bin/env python3

"""Parse the ffmpeg vmaf metric."""

import json
import pathlib
import subprocess
import tempfile
import typing
import uuid

import numpy as np
import torch

from cutcutcodec.core.opti.parallel.threading import get_num_threads
from .utils import batched_comparative_frames


def _to_yuv(frame: torch.Tensor) -> bytes:
    """Help ``to_yuvfile`` function."""
    yuv = frame.clone()  # to avoid inplace modifications
    yuv[:, :, 1:] += 0.5  # [-1/2, 1/2] -> [0, 1]
    yuv *= 65535.0
    yuv = yuv.movedim(2, 0)  # (height, width, 3) -> (3, height, width)
    yuv_numpy = yuv.numpy(force=True).astype(np.uint16)
    yuv_data = yuv_numpy.tobytes("C")
    return yuv_data


def to_yuvfile(frames: torch.Tensor | typing.Iterable[torch.Tensor]) -> pathlib.Path:
    r"""Write the frame into a standard full range ``.yuv`` file in ``yuv444p16le`` pixel format.

    Parameters
    ----------
    frames : list[torch.Tensor]
        A (or several) video frame, assumed to be in yuv (YpPbPr) format, with
        :math:`(y', p_b, p_r) \in [0, 1] \times \left[-\frac{1}{2}, \frac{1}{2}\right]^2`.

    Returns
    -------
    filename : pathlib.Path
        The filename to the yuv file.

    Examples
    --------
    >>> import pathlib
    >>> import subprocess
    >>> import torch
    >>> from cutcutcodec.core.analysis.video.metric.vmaf import to_yuvfile
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> frame = torch.rand((720, 1080, 3))
    >>> frame[:, :, 1:] -= 0.5
    >>> yuvfile = to_yuvfile(frame)
    >>> _ = subprocess.run(
    ...     [
    ...         "ffmpeg", "-y", "-f", "rawvideo",
    ...         "-s", "1080x720", "-pix_fmt", "yuv444p16le", "-color_range", "pc",
    ...         "-i", str(yuvfile),
    ...         "-c:v", "libaom-av1", "-crf", "0",
    ...         "/tmp/tmp.avif",
    ...     ],
    ...     check=True, capture_output=True
    ... )
    >>> yuvfile.unlink()
    >>> with ContainerInputFFMPEG("/tmp/tmp.avif") as container:
    ...     frame_bis = container.out_streams[0].snapshot(0, (720, 1080))
    ...
    >>> pathlib.Path("/tmp/tmp.avif").unlink()
    >>> assert torch.allclose(frame, frame_bis, atol=1e-3)
    >>>
    """
    if isinstance(frames, torch.Tensor):
        frames = [frames]
    assert isinstance(frames, typing.Iterable), frames.__class__.__name__
    filename = pathlib.Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.yuv"
    shape = None
    with open(filename, "wb") as raw:
        for frame in frames:
            if shape is None:
                shape = frame.shape
                assert frame.ndim == 3, \
                    f"frame must be of shape (height, widht, 3), got {frame.shape}"
                assert frame.shape[2] == 3, f"the frame requires only 3 channels, got {frame.shape}"
            assert frame.shape == shape, \
                f"all frames must have the same shape: {shape} vs {frame.shape}"
            raw.write(_to_yuv(frame))
    return filename


@batched_comparative_frames
def vmaf(ref: torch.Tensor, dis: torch.Tensor, threads: int = 0) -> torch.Tensor:
    """Call the Netflix vmaf metric on the frames.

    Parameters
    ----------
    ref : arraylike
        The reference video frames, transmitted to ``to_yuvfile``,
        shape ([*batch], height, width, 3).
    dis : arraylike
        The distorted video frames, transmitted to ``to_yuvfile``,
        shape ([*batch], height, width, 3).
    threads : int, optional
        Defines the number of threads.
        The value -1 means that the function uses as many calculation threads as there are cores.
        The default value (0) allows the same behavior as (-1) if the function
        is called in the main thread, otherwise (1) to avoid nested threads.
        Any other positive value corresponds to the number of threads used.

    Returns
    -------
    vmaf : arraylike
        All the vmaf values for the pairwise frames.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.metric import vmaf
    >>> np.random.seed(0)
    >>> ref = np.random.random((720, 1080, 3))  # It could also be a torch array list...
    >>> ref[:, :, 1:] -= 0.5  # yuv format
    >>> dis = ref.copy()
    >>> dis[:, :, 0] = 0.8 * dis[:, :, 0] + 0.2 * np.random.random((720, 1080))
    >>> vmaf(ref, dis).round(1)
    np.float64(33.7)
    >>>
    """
    threads = get_num_threads(threads)

    # create reference files
    if len(ref) == 0:
        return torch.asarray([], dtype=ref.dtype)
    yuv_ref = to_yuvfile(list(ref))
    yuv_dis = to_yuvfile(list(dis))
    (height, width, _) = ref[0].shape

    # run vmaf
    log_file = pathlib.Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.json"
    try:
        subprocess.run([
            "vmaf", "-r", str(yuv_ref), "-d", str(yuv_dis),
            "-h", str(height), "-w",  str(width), "-p", "444", "-b", "16",
            "--threads", str(threads),
            "--json", "-o", str(log_file)
        ], check=True, capture_output=True)
    except FileNotFoundError as err:
        raise ImportError(
            "'vmaf' does not appear to be installed, please follow the full installation guide: "
            "https://cutcutcodec.readthedocs.io/latest/developer_guide/installation.html"
            "#vmaf-optional"
        ) from err
    finally:
        yuv_ref.unlink()
        yuv_dis.unlink()

    # parse vmaf result
    with open(log_file, "r", encoding="utf-8") as raw:
        data = json.load(raw)
    log_file.unlink()
    return torch.asarray(
        [frame_info["metrics"]["vmaf"] for frame_info in data["frames"]], dtype=ref.dtype
    )
