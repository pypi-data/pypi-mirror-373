#!/usr/bin/env python3

"""Read an image with opencv."""

from fractions import Fraction
import math
import pathlib
import typing

import cv2
import numpy as np
import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.container import ContainerInput
from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.exceptions import DecodeError, MissingStreamError, OutOfTimeRange
from cutcutcodec.core.filter.video.resize import resize_keep_ratio
from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG


def _read_av(filename: pathlib.Path) -> tuple[np.ndarray, Colorspace]:
    """Read the image with the pyav module."""
    from cutcutcodec.core.analysis.stream.shape import optimal_shape_video
    container = ContainerInputFFMPEG(filename)
    streams = container.out_select("video")
    if not streams:
        raise DecodeError(f"no image stream found in {filename} with pyav")
    shapes = []
    err = None
    for stream in streams:
        try:
            shape = optimal_shape_video(stream)
        except MissingStreamError as err_:
            err = err_
        else:
            shapes.append((shape, stream))
    if not shapes:
        raise DecodeError(f"failed to decode image stream in {filename} with pyav") from err
    (shape, stream) = max(shapes, key=lambda s: s[0][0] * s[0][1])
    img = stream.snapshot(0, shape).numpy(force=True)
    return img, stream.colorspace


def _read_cv2(filename: pathlib.Path) -> tuple[np.ndarray, Colorspace]:
    """Read the image with opencv."""
    try:
        if (img_bgr := cv2.imread(filename, cv2.IMREAD_REDUCED_COLOR_8)) is None:
            raise DecodeError("failed to decode with cv2")
    except cv2.error as err:
        raise DecodeError("failed to decode with cv2") from err
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return img_rgb, Colorspace.from_default_target_rgb()


def read_image(filename: pathlib.Path | str | bytes) -> tuple[torch.Tensor, Colorspace]:
    """Read the image and make it compatible with Video Frame.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the image file.

    Returns
    -------
    image : torch.Tensor
        The image in float32 of shape (height, width, channels).
    colorspace : Colorspace
        The color space in which the image is defined. No conversion performed.

    Raises
    ------
    cutcutcodec.core.exceptions.DecodeError
        If it fails to read the image.

    Notes
    -----
    Does not care about colorspace, no conversions performed.

    Examples
    --------
    >>> from cutcutcodec.core.io.read_image import read_image
    >>> from cutcutcodec.utils import get_project_root
    >>> for file in sorted((get_project_root().parent / "media" / "image").glob("image.*")):
    ...     image, colorspace = read_image(file)
    ...     print(f"{file.name}: {image.shape}, {colorspace}")
    ...
    image.avif: torch.Size([64, 64, 3]), Colorspace("y'pbpr", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.bmp: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.exr: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'linear')
    image.heic: torch.Size([64, 64, 3]), Colorspace("y'pbpr", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.jp2: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.jpg: torch.Size([64, 64, 3]), Colorspace("y'pbpr", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.kra: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.pbm: torch.Size([64, 64, 1]), Colorspace("y'pbpr", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.pgm: torch.Size([64, 64, 1]), Colorspace("y'pbpr", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.png: torch.Size([64, 64, 4]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.pnm: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.ppm: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.psd: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.ras: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.sgi: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.tiff: torch.Size([64, 64, 3]), Colorspace("r'g'b'", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.webp: torch.Size([64, 64, 3]), Colorspace("y'pbpr", 'bt709', 'iec61966-2-1, iec61966_2_1')
    image.xbm: torch.Size([64, 64, 1]), Colorspace("y'pbpr", 'bt709', 'iec61966-2-1, iec61966_2_1')
    """
    filename = pathlib.Path(filename).expanduser().resolve()
    assert filename.is_file(), filename

    # try several decoders
    errs = []
    for decoder in (_read_av, _read_cv2):
        try:
            img_np, colorspace = decoder(filename)
            break
        except DecodeError as err:
            errs.append(err)
    else:
        raise DecodeError(f"failed to decode the image {filename}", errs) from errs[0]

    # convert in float32
    img = torch.from_numpy(img_np)
    if img.ndim == 2:  # (height, width) -> (height, width, 1)
        img = img[:, :, None]
    if not torch.is_floating_point(img):
        iinfo = torch.iinfo(img.dtype)
        img = img.to(torch.float32)
        img -= float(iinfo.min)
        img *= 1.0 / float(iinfo.max - iinfo.min)
    elif img.dtype != torch.float32:
        img = img.to(torch.float32)

    return img, colorspace


class ContainerInputImage(ContainerInput):
    """Decode an image.

    Attributes
    ----------
    filename : pathlib.Path
        The path to the physical file that contains the extracted image stream (readonly).

    Examples
    --------
    >>> from cutcutcodec.core.io.read_image import ContainerInputImage
    >>> from cutcutcodec.utils import get_project_root
    >>> (stream,) = ContainerInputImage(get_project_root() / "examples" / "logo.png").out_streams
    >>> stream.snapshot(0, (9, 9))[..., 3]  # alpha layer
    tensor([[0.0000, 0.0415, 0.5152, 0.8748, 0.9872, 0.8744, 0.5164, 0.0422, 0.0000],
            [0.0418, 0.7853, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.7851, 0.0420],
            [0.5156, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.5141],
            [0.8749, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.8732],
            [0.9871, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.9861],
            [0.8745, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.8727],
            [0.5150, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.5137],
            [0.0417, 0.7838, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.7842, 0.0413],
            [0.0000, 0.0411, 0.5139, 0.8732, 0.9865, 0.8729, 0.5144, 0.0417, 0.0000]])
    >>>
    """

    def __init__(self, filename: pathlib.Path | str | bytes):
        """Initialise and create the class.

        Parameters
        ----------
        filename : pathlike
            Path to the file to be decoded.

        Raises
        ------
        cutcutcodec.core.exceptions.DecodeError
            If it fail to extract any multimedia stream from the provided file.
        """
        filename = pathlib.Path(filename).expanduser().resolve()
        assert filename.is_file(), filename
        self._filename = filename
        super().__init__([_StreamVideoImage(self)])

    def _getstate(self) -> dict:
        return {"filename": str(self.filename)}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        keys = {"filename"}
        assert state.keys() == keys, set(state)-keys
        ContainerInputImage.__init__(self, state["filename"])

    @property
    def filename(self) -> pathlib.Path:
        """Return the path to the physical file that contains the extracted image stream."""
        return self._filename


class _StreamVideoImage(StreamVideo):
    """Read an image as a video stream.

    Parameters
    ----------
    height : int
        The dimension i (vertical) of the encoded frames in pxl (readonly).
    width : int
        The dimension j (horizontal) of the encoded frames in pxl (readonly).
    """

    def __init__(self, node: ContainerInputImage):
        assert isinstance(node, ContainerInputImage), node.__class__.__name__
        super().__init__(node)
        self._img, self._colorspace = read_image(node.filename)
        self._height, self._width, *_ = self._img.shape
        self._resized_img = FrameVideo(0, self._img)  # not from_numpy for casting shape and type

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no image frame at timestamp {timestamp} (need >= 0)")

        # reshape if needed
        if self._resized_img.shape[:2] != mask.shape:
            self._resized_img = resize_keep_ratio(self._img, mask.shape, copy=False)

        return FrameVideo(timestamp, self._resized_img.clone())

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def colorspace(self) -> Colorspace:
        return self._colorspace

    @property
    def duration(self) -> Fraction | float:
        return math.inf

    @property
    def has_alpha(self) -> bool:
        """Return True if the stream has alpha layer."""
        return self._img.shape[2] in {2, 4}

    @property
    def height(self) -> int:
        """Return the preconised dimension i (vertical) of the picture in pxl."""
        return self._height

    @property
    def width(self) -> int:
        """Return the preconised dimension j (horizontal) of the picture in pxl."""
        return self._width
