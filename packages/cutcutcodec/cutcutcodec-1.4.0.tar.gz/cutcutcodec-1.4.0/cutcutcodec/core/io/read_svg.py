#!/usr/bin/env python3

"""Decode the svg vectorial images based on `cairosvg` lib."""

from fractions import Fraction
import math
import pathlib
import typing
import xml

import cairosvg
import cv2
import numpy as np
import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.container import ContainerInput
from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.exceptions import DecodeError
from cutcutcodec.core.exceptions import OutOfTimeRange


class ContainerInputSVG(ContainerInput):
    """Decode an svg image to a matricial image of any dimension.

    Attributes
    ----------
    filename : pathlib.Path
        The path to the physical file that contains the svg data (readonly).

    Examples
    --------
    >>> from cutcutcodec.core.io.read_svg import ContainerInputSVG
    >>> from cutcutcodec.utils import get_project_root
    >>> (stream,) = ContainerInputSVG(get_project_root() / "examples" / "logo.svg").out_streams
    >>> stream.snapshot(0, (9, 9))[..., 3]
    tensor([[0.0000, 0.0627, 0.5529, 0.8275, 0.9608, 0.8275, 0.5529, 0.0627, 0.0000],
            [0.0745, 0.8471, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.8471, 0.0745],
            [0.5686, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.5647],
            [0.8863, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.8824],
            [0.9765, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.9765],
            [0.8863, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.8824],
            [0.5686, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.5647],
            [0.0745, 0.8471, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.8471, 0.0745],
            [0.0000, 0.0627, 0.5529, 0.8275, 0.9608, 0.8275, 0.5529, 0.0627, 0.0000]])
    >>>
    """

    def __init__(self, filename: pathlib.Path | str | bytes, *, unsafe=False):
        """Initialise and create the class.

        Parameters
        ----------
        filename : pathlike
            Path to the file to be decoded.
        unsafe : bool
            Transmitted to ``cairosvg.svg2png``.

        Raises
        ------
        cutcutcodec.core.exceptions.DecodeError
            If it fail to extract any multimedia stream from the provided file.
        """
        filename = pathlib.Path(filename).expanduser().resolve()
        assert filename.is_file(), filename
        assert isinstance(unsafe, bool), unsafe.__class__.__name__
        self._filename = filename
        self.unsafe = unsafe
        super().__init__([_StreamVideoSVG(self)])

    def __enter__(self):
        """Make the object compatible with a context manager."""
        return self

    def __exit__(self, *_):
        """Exit the context manager."""

    def _getstate(self) -> dict:
        return {
            "filename": str(self.filename),
            "unsafe": self.unsafe,
        }

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        keys = {"filename", "unsafe"}
        assert state.keys() == keys, set(state)-keys
        ContainerInputSVG.__init__(self, state["filename"], unsafe=state["unsafe"])

    @property
    def filename(self) -> pathlib.Path:
        """Return the path to the physical file that contains the svg data."""
        return self._filename


class _StreamVideoSVG(StreamVideo):
    """Read SVG as a video stream.

    Parameters
    ----------
    height : int
        The preconised dimension i (vertical) of the picture in pxl (readonly).
    width : int
        The preconised dimension j (horizontal) of the picture in pxl (readonly).
    """

    colorspace = Colorspace.from_default_target_rgb()

    def __init__(self, node: ContainerInputSVG):
        assert isinstance(node, ContainerInputSVG), node.__class__.__name__
        super().__init__(node)
        with open(node.filename, "rb") as raw:
            self._bytestring = raw.read()
        try:
            pngdata = cairosvg.svg2png(self._bytestring, unsafe=self.node.unsafe)
        except xml.etree.ElementTree.ParseError as err:
            raise DecodeError(f"failed to read the svg file {node.filename} with cairosvg") from err
        img = torch.from_numpy(cv2.imdecode(np.frombuffer(pngdata, np.uint8), cv2.IMREAD_UNCHANGED))
        self._height, self._width, _ = img.shape
        self._shape_and_img = ((self._height, self._width), img)

    def _get_img(self, shape: tuple[int, int]) -> torch.Tensor:
        """Cache the image."""
        if self._shape_and_img[0] != shape:
            self._shape_and_img = (
                shape,
                torch.from_numpy(
                    cv2.imdecode(
                        np.frombuffer(
                            cairosvg.svg2png(
                                self._bytestring,
                                unsafe=self.node.unsafe,
                                output_height=shape[0],
                                output_width=shape[1],
                            ),
                            np.uint8,
                        ),
                        cv2.IMREAD_UNCHANGED,
                    ),
                ).to(torch.float32) / 255.0,
            )
        return self._shape_and_img[1]

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no svg frame at timestamp {timestamp} (need >= 0)")
        return FrameVideo(timestamp, self._get_img(mask.shape).clone())

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> Fraction | float:
        return math.inf

    @property
    def height(self) -> int:
        """Return the preconised dimension i (vertical) of the picture in pxl."""
        return self._height

    @property
    def width(self) -> int:
        """Return the preconised dimension j (horizontal) of the picture in pxl."""
        return self._width
