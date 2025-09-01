#!/usr/bin/env python3

"""Defines the structure a video frame."""

from fractions import Fraction
import numbers
import re
import typing

import numpy as np
import torch

from cutcutcodec.core.classes.frame import Frame
from cutcutcodec.core.filter.mix.video_cast import to_gray, to_gray_alpha, to_rgb, to_rgb_alpha


class FrameVideo(Frame):
    """An image with time information for video context.

    Behaves like a torch tensor of shape (height, width, channels).
    The shape is consistent with pyav and cv2.
    The dtype is always float32.

    Attributes
    ----------
    channels : int
        The numbers of layers (readonly):

            * 1 -> grayscale
            * 2 -> grayscale, alpha
            * 3 -> red, green, blue
            * 4 -> red, green, blue, alpha
    height : int
        The dimension i (vertical) of the image in pxl (readonly).
    time : Fraction
        The time of the frame inside the video stream in second (readonly).
    width : int
        The dimension j (horizontal) of the image in pxl (readonly).
    """

    def __new__(  # pylint: disable=W0222
        cls,
        time: Fraction | numbers.Real | str,
        data: torch.Tensor | np.ndarray | typing.Container,
        **kwargs,
    ):
        """Construct a video frame and normalize the type.

        Parameters
        ----------
        time : Fraction
            The time of the frame inside the video stream in second
        data : arraylike
            Transmitted to ``cutcutcodec.core.classes.frame.Frame`` initialisator.
        **kwargs : dict
            Transmitted to ``cutcutcodec.core.classes.frame.Frame`` initialisator.
        """
        # create frame
        frame = super().__new__(cls, data, context=time, **kwargs)

        # cast shape
        if frame.ndim == 2:  # give flexibility for grayscale images
            frame = frame.unsqueeze(2)

        # verifications
        frame.check_state()
        return frame

    def __repr__(self) -> str:
        """Compact and complete display of an evaluable version of the video frame.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_video import FrameVideo
        >>> FrameVideo("2/4", torch.zeros((480, 720, 3)))  # doctest: +ELLIPSIS
        FrameVideo('1/2', [[[0., 0., 0.],
                            ...
                            [0., 0., 0.]]])
        >>>
        """
        time_str = f"'{self.time}'" if int(self.time) != self.time else f"{self.time}"
        header = f"{self.__class__.__name__}({time_str}, "
        tensor_str = np.array2string(
            self.numpy(force=True), separator=", ", prefix=header, suffix=" "
        )
        if (infos := re.findall(r"\w+=[a-zA-Z0-9_\-.\"']+", torch.Tensor.__repr__(self))):
            infos = [inf for inf in infos if inf != "dtype=torch.uint8"]
        if infos:
            infos = "\n" + " "*len(header) + (",\n" + " "*len(header)).join(infos)
            return f"{header}{tensor_str},{infos})"
        return f"{header}{tensor_str})"

    @property
    def channels(self) -> int:
        """Return the numbers of layers.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_video import FrameVideo
        >>> FrameVideo(0, torch.empty(480, 720, 3)).channels
        3
        >>>
        """
        return self.shape[2]

    def check_state(self) -> None:
        """Apply verifications.

        Raises
        ------
        AssertionError
            If something wrong in this frame.
        """
        context = getattr(self, "context", None)
        assert context is not None
        assert isinstance(context, (Fraction, numbers.Real, str)), context.__class__.__name__
        setattr(self, "context", Fraction(context))
        assert self.ndim == 3, self.shape
        assert self.shape[0] > 0, self.shape
        assert self.shape[1] > 0, self.shape
        assert self.shape[2] in {1, 2, 3, 4}, self.shape
        assert self.dtype == torch.float32, self.dtype

    def convert(self, channels: int) -> typing.Self:
        """Change the numbers of channels of the frame.

        Returns
        -------
        frame : cutcutcodec.core.classes.frame_video.FrameVideo
            The new frame, be carfull, undergroud data can be shared.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_video import FrameVideo
        >>> _ = torch.manual_seed(0)
        >>> ref_gray = FrameVideo(0, torch.rand((480, 720, 1)))
        >>> ref_gray_alpha = FrameVideo(0, torch.rand((480, 720, 2)))
        >>> ref_rgb = FrameVideo(0, torch.rand((480, 720, 3)))
        >>> ref_rgb_alpha = FrameVideo(0, torch.rand((480, 720, 4)))
        >>>
        >>> # case 1 -> 2, 3, 4
        >>> gray_alpha = ref_gray.convert(2)
        >>> gray_alpha.channels
        2
        >>> torch.equal(gray_alpha[..., 0], ref_gray[..., 0])
        True
        >>> torch.eq(gray_alpha[..., 1], 1.0).all()
        tensor(True)
        >>> rgb = ref_gray.convert(3)
        >>> rgb.channels
        3
        >>> torch.equal(rgb[..., 0], ref_gray[..., 0])
        True
        >>> torch.equal(rgb[..., 1], ref_gray[..., 0])
        True
        >>> torch.equal(rgb[..., 2], ref_gray[..., 0])
        True
        >>> rgb_alpha = ref_gray.convert(4)
        >>> rgb_alpha.channels
        4
        >>> torch.equal(rgb_alpha[..., 0], ref_gray[..., 0])
        True
        >>> torch.equal(rgb_alpha[..., 1], ref_gray[..., 0])
        True
        >>> torch.equal(rgb_alpha[..., 2], ref_gray[..., 0])
        True
        >>> torch.eq(rgb_alpha[..., 3], 1.0).all()
        tensor(True)
        >>>
        >>> # case 2 -> 1, 3, 4
        >>> gray = ref_gray_alpha.convert(1)
        >>> gray.channels
        1
        >>> torch.equal(gray[..., 0],
        ...     torch.where(torch.eq(ref_gray_alpha[..., 1], 0.), 0., ref_gray_alpha[..., 0]))
        True
        >>> rgb = ref_gray_alpha.convert(3)
        >>> rgb.channels
        3
        >>> torch.equal(rgb[..., 0],
        ...     torch.where(torch.eq(ref_gray_alpha[..., 1], 0.), 0., ref_gray_alpha[..., 0]))
        True
        >>> torch.equal(rgb[..., 1],
        ...     torch.where(torch.eq(ref_gray_alpha[..., 1], 0.), 0., ref_gray_alpha[..., 0]))
        True
        >>> torch.equal(rgb[..., 2],
        ...     torch.where(torch.eq(ref_gray_alpha[..., 1], 0.), 0., ref_gray_alpha[..., 0]))
        True
        >>> rgb_alpha = ref_gray_alpha.convert(4)
        >>> rgb_alpha.channels
        4
        >>> torch.equal(rgb_alpha[..., 0], ref_gray_alpha[..., 0])
        True
        >>> torch.equal(rgb_alpha[..., 1], ref_gray_alpha[..., 0])
        True
        >>> torch.equal(rgb_alpha[..., 2], ref_gray_alpha[..., 0])
        True
        >>> torch.equal(rgb_alpha[..., 3], ref_gray_alpha[..., 1])
        True
        >>>
        >>> # case 3 -> 1, 2, 4
        >>> gray = ref_rgb.convert(1)
        >>> gray.channels
        1
        >>> gray_alpha = ref_rgb.convert(2)
        >>> gray_alpha.channels
        2
        >>> torch.eq(gray_alpha[..., 1], 1.0).all()
        tensor(True)
        >>> rgb_alpha = ref_rgb.convert(4)
        >>> rgb_alpha.channels
        4
        >>> torch.equal(rgb_alpha[..., 0], ref_rgb[..., 0])
        True
        >>> torch.equal(rgb_alpha[..., 1], ref_rgb[..., 1])
        True
        >>> torch.equal(rgb_alpha[..., 2], ref_rgb[..., 2])
        True
        >>> torch.eq(rgb_alpha[..., 3], 1.0).all()
        tensor(True)
        >>>
        >>> # case 4 -> 1, 2, 3
        >>> gray = ref_rgb_alpha.convert(1)
        >>> gray.channels
        1
        >>> gray_alpha = ref_rgb_alpha.convert(2)
        >>> gray_alpha.channels
        2
        >>> torch.equal(gray_alpha[..., 1], ref_rgb_alpha[..., 3])
        True
        >>> rgb = ref_rgb_alpha.convert(3)
        >>> rgb.channels
        3
        >>> torch.equal(rgb[..., 0],
        ...     torch.where(torch.eq(ref_rgb_alpha[..., 3], 0.), 0., ref_rgb_alpha[..., 0]))
        True
        >>> torch.equal(rgb[..., 1],
        ...     torch.where(torch.eq(ref_rgb_alpha[..., 3], 0.), 0., ref_rgb_alpha[..., 1]))
        True
        >>> torch.equal(rgb[..., 2],
        ...     torch.where(torch.eq(ref_rgb_alpha[..., 3], 0.), 0., ref_rgb_alpha[..., 2]))
        True
        >>>
        """
        assert isinstance(channels, int), channels.__class__.__name__
        assert 1 <= channels <= 4, f"channels can only be 1, 2, 3, or 4, not {channels}"
        converter = {1: to_gray, 2: to_gray_alpha, 3: to_rgb, 4: to_rgb_alpha}[channels]
        return self.__class__(self.time, converter(self))

    @property
    def height(self) -> int:
        """Return the dimension i (vertical) of the image in pxl.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_video import FrameVideo
        >>> FrameVideo(0, torch.empty(480, 720, 3)).height
        480
        >>>
        """
        return self.shape[0]

    @property
    def time(self) -> Fraction:
        """Return the time of the frame inside the video stream in second.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_video import FrameVideo
        >>> FrameVideo(0, torch.empty(480, 720, 3)).time
        Fraction(0, 1)
        >>>
        """
        return self.context

    @time.setter
    def time(self, time: numbers.Real):
        """Set a new time."""
        setattr(self, "context", time)
        self.check_state()  # convert time

    def to_numpy_uint8(self) -> np.ndarray[np.uint8]:
        """Convert the frame into a numpy uint8 image.

        Notes
        -----
        The colorspace is not changed, please apply
        :py:class:`cutcutcodec.core.filter.video.colorspace.FilterVideoColorspace`
        to the video stream, then call this method.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_video import FrameVideo
        >>>
        >>> frame = FrameVideo(0, torch.zeros(480, 720, 3)).to_numpy_uint8()  # classical rgb
        >>> type(frame), frame.shape, frame.dtype
        (<class 'numpy.ndarray'>, (480, 720, 3), dtype('uint8'))
        >>> frame = FrameVideo(0, torch.zeros(480, 720, 3)).to_numpy_uint8()  # grayscale
        >>> type(frame), frame.shape, frame.dtype
        (<class 'numpy.ndarray'>, (480, 720, 3), dtype('uint8'))
        >>> frame = FrameVideo(0, torch.zeros(480, 720, 3)).to_numpy_uint8()  # alpha channel
        >>> type(frame), frame.shape, frame.dtype
        (<class 'numpy.ndarray'>, (480, 720, 3), dtype('uint8'))
        >>>
        """
        from cutcutcodec.core.io.framecaster import to_rgb as to_rgb_
        return to_rgb_(self.numpy(force=True), False)  # full range conversion

    @property
    def width(self) -> int:
        """Return the dimension j (horizontal) of the image in pxl.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_video import FrameVideo
        >>> FrameVideo(0, torch.empty(480, 720, 3)).width
        720
        >>>
        """
        return self.shape[1]
