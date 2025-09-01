#!/usr/bin/env python3

"""Manage the input/output layer."""

import logging
import pathlib
import typing

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.node import Node
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.exceptions import DecodeError
from .cst import AUDIO_SUFFIXES, VIDEO_SUFFIXES, IMAGE_SUFFIXES
from .read_color import filter_video_colorspace
from .read_ffmpeg import ContainerInputFFMPEG
from .read_image import ContainerInputImage
from .read_svg import ContainerInputSVG
from .write_ffmpeg import ContainerOutputFFMPEG


__all__ = ["read", "write", "AUDIO_SUFFIXES", "IMAGE_SUFFIXES", "VIDEO_SUFFIXES"]


def read(
    filename: pathlib.Path | str | bytes,
    colorspace: typing.Optional[Colorspace | str] = None,
    **kwargs,
) -> Node:
    """Open the media file with the appropriate reader.

    Parameters
    ----------
    filename : pathlike
        The path to the file to be decoded.
    colorspace : str or Colorspace, optional
        Transmitted to :py:class:`cutcutcodec.core.filter.video.colorspace.FilterVideoColorspace`.
    **kwargs : dict
        Transmitted to :py:class:`cutcutcodec.core.io.read_ffmpeg.ContainerInputFFMPEG`
        or :py:class:`cutcutcodec.core.io.read_image.ContainerInputImage`
        or :py:class:`cutcutcodec.core.io.read_svg.ContainerInputSVG`.

    Returns
    -------
    container : cutcutcodec.core.classes.container.ContainerInput
        The appropriated instanciated container, according to the nature of the file.

    Raises
    ------
    cutcutcodec.core.exceptions.DecodeError
        If the file can not be decoded by any reader.
    """
    extension = pathlib.Path(filename).suffix.lower()

    # simple case where extension is knowned
    if extension in VIDEO_SUFFIXES | AUDIO_SUFFIXES:
        return filter_video_colorspace(ContainerInputFFMPEG(filename, **kwargs), colorspace)
    if extension in IMAGE_SUFFIXES:
        return filter_video_colorspace(ContainerInputImage(filename, **kwargs), colorspace)
    if extension in {".svg"}:
        return filter_video_colorspace(ContainerInputSVG(filename, **kwargs), colorspace)

    # case we have to try
    logging.warning("unknown extension %s, try several readers", extension)
    try:
        return filter_video_colorspace(ContainerInputSVG(filename, **kwargs), colorspace)
    except DecodeError:
        try:
            return filter_video_colorspace(ContainerInputFFMPEG(filename, **kwargs), colorspace)
        except DecodeError:
            return filter_video_colorspace(ContainerInputImage(filename, **kwargs), colorspace)


def write(
    streams: typing.Iterable[Stream],
    filename: pathlib.Path | str | bytes,
    colorspace: typing.Optional[Colorspace | str] = None,
    **kwargs,
):
    """Create, write and encode the multimedia file.

    This is a high-level version of the ``write`` method
    of the :py:class:`cutcutcodec.core.io.write_ffmpeg.ContainerOutputFFMPEG` class.

    Parameters
    ----------
    streams : iterable[Stream]
        These are all the audio and video streams that will be present in the final container.
    filename : pathlike
        The path to the media file to be encoded.
    colorspace : str or Colorspace, optional
        The encoded colorspace, by default, it is
        :py:meth:`cutcutcodec.core.classes.colorspace.Colorspace.from_default_target`.
        Transmitted to :py:class:`cutcutcodec.core.filter.video.colorspace.FilterVideoColorspace`.
    """
    if colorspace is None:
        colorspace = Colorspace.from_default_target()
    else:
        colorspace = Colorspace(colorspace)
    streams = [s.apply_video_colorspace(colorspace) if s.type == "video" else s for s in streams]
    ContainerOutputFFMPEG(streams, filename, **kwargs).write()
