#!/usr/bin/env python3

"""Video Data Augmentations."""

import numbers
import pathlib
import random
import tempfile
import typing
import uuid

import av
import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.io.framecaster import from_yuv, to_yuv
from cutcutcodec.core.filter.video.resize import resize


class Transcoder:
    """Encode and Decode the video with lossly compression.

    Attributes
    ----------
    encoders : list[str]
        The encoders list (readonly).
    """

    def __init__(
        self,
        encoders: typing.Iterable[str] | str = None,
        quality: tuple[numbers.Real, numbers.Real] | numbers.Real = (0.5, 0.9),
    ):
        """Initialise a random transcoder.

        Parameters
        ----------
        encoders : list[str] or str, optional
            The encoders used, By default ['libx264', 'libx265', 'libvx-vp9', 'libsvtav1'].
            Only these encoders are supported.
        quality : tuple[float, float] of float
            The qualities bounds 0 lossless, 1 worse.
        """
        if encoders is None:
            encoders = ["libx264", "libx265", "libvpx-vp9", "libsvtav1"]
        else:
            if isinstance(encoders, str):
                encoders = [encoders]
            assert hasattr(encoders, "__iter__"), encoders.__class__.__name__
            encoders = list(encoders)
            assert all(isinstance(e, str) for e in encoders), encoders
            assert set(encoders).issubset({"libx264", "libx265", "libvpx-vp9", "libsvtav1"})
        if isinstance(quality, numbers.Real):
            quality = (quality, quality)
        else:
            quality = tuple(quality)
            assert len(quality) == 2, quality
            assert isinstance(quality[0], numbers.Real) and isinstance(quality[1], numbers.Real)
            assert 0 <= quality[0] <= 1 and 0 <= quality[1] <= 1, quality

        self._encoders = encoders
        self.quality = quality
        self.fromlin = (
            Colorspace.from_default_working()
            .to_function(Colorspace.from_default_target())
        )
        self.tolin = (
            Colorspace.from_default_target()
            .to_function(Colorspace.from_default_working())
        )

    def __call__(self, video: torch.Tensor) -> torch.Tensor:
        """Transcode the images.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.nn.dataaug.video import Transcoder
        >>> video = torch.rand(2, 3, 1080, 1920, 3*5)
        >>> transcoder = Transcoder("libx264")
        >>> transcoder(video).shape
        torch.Size([2, 3, 1080, 1920, 15])
        >>>
        """
        assert isinstance(video, torch.Tensor), video.__class__.__name__
        assert video.ndim >= 3, video.shape
        assert video.shape[2] % 3 == 0, video.shape

        # case recursive
        if video.ndim > 3:
            return torch.cat(
                [self(v) for v in video.reshape(-1, *video.shape[-3:])], dim=0
            ).reshape(*video.shape)

        # resize for even dimension, required by some encoders
        buff = resize(video, (2*(video.shape[0]//2), 2*(video.shape[1]//2)))

        # preparation
        file = pathlib.Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.mp4"
        yuv = self.fromlin(r=buff[:, :, 0::3], g=buff[:, :, 1::3], b=buff[:, :, 2::3])

        # encode
        with av.open(file, mode="w", format="mp4") as container:
            stream = container.add_stream(random.choice(self._encoders), rate=30)
            quality = random.random()
            quality = self.quality[0] * quality + self.quality[1] * (1.0 - quality)
            quality *= {
                "libx264": 51.0, "libx265": 51.0, "libvpx-vp9": 63.0, "libsvtav1": 63.0
            }[stream.name]
            quality = round(quality)
            stream.options = {"crf": str(quality)}
            stream.height, stream.width, _ = buff.shape
            for i in range(buff.shape[2]//3):
                container.mux(stream.encode(
                    av.video.frame.VideoFrame.from_ndarray(
                        to_yuv(
                            torch.cat([
                                yuv[0][:, :, i, None], yuv[1][:, :, i, None], yuv[2][:, :, i, None]
                            ], dim=2)
                            .numpy(force=True),
                        ),
                        format="yuv444p16le",  # tv range
                    ).reformat(format="yuv420p")
                ))
            container.mux(stream.encode(None))  # flush buffer

        # decode
        with av.open(file, mode="r", format="mp4") as container:
            buff = torch.cat(
                [
                    torch.from_numpy(
                        from_yuv(f.to_ndarray(channel_last=True, format="yuv444p"), True)
                    ).to(dtype=video.dtype, device=video.device)
                    for packet in container.demux(video=0) for f in packet.decode()
                ],
                dim=2,
            )
        file.unlink()
        buff = resize(buff, video.shape, copy=False)  # back to initial shape

        # convert colors
        buff[:, :, 0::3], buff[:, :, 1::3], buff[:, :, 2::3] = self.tolin(
            y=buff[:, :, 0::3], u=buff[:, :, 1::3], v=buff[:, :, 2::3]
        )
        return buff

    @property
    def encoders(self) -> list[str]:
        """Return the encoders useds."""
        return self._encoders


def interlace(video: torch.Tensor) -> torch.Tensor:
    """Simulate an interlaced video.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.nn.dataaug.video import interlace
    >>> video = torch.empty(5, 5, 12)
    >>> video[:, :, 0:3] = 1.0
    >>> video[:, :, 3:6] = 2.0
    >>> video[:, :, 6:9] = 3.0
    >>> video[:, :, 9:12] = 4.0
    >>> video = interlace(video)
    >>> video[:, :, 6]
    tensor([[3., 3., 3., 3., 3.],
            [2., 2., 2., 2., 2.],
            [3., 3., 3., 3., 3.],
            [2., 2., 2., 2., 2.],
            [3., 3., 3., 3., 3.]])
    >>>
    """
    assert isinstance(video, torch.Tensor), video.__class__.__name__
    assert video.ndim >= 3, video.shape
    assert video.shape[2] % 3 == 0, video.shape

    interlaced = torch.empty_like(video)
    interlaced[..., ::2, :, :3] = video[..., ::2, :, :3]
    interlaced[..., 1::2, :, :3] = interlaced[..., 0:-1:2, :, :3]
    for i in range(1, video.shape[2]//3):
        if i % 2 == 0:  # even
            interlaced[..., ::2, :, 3*i:3*i+3] = video[..., ::2, :, 3*i:3*i+3]
            interlaced[..., 1::2, :, 3*i:3*i+3] = video[..., 1::2, :, 3*i-3:3*i]
        else:  # odd
            interlaced[..., ::2, :, 3*i:3*i+3] = video[..., ::2, :, 3*i-3:3*i]
            interlaced[..., 1::2, :, 3*i:3*i+3] = video[..., 1::2, :, 3*i:3*i+3]
    return interlaced
