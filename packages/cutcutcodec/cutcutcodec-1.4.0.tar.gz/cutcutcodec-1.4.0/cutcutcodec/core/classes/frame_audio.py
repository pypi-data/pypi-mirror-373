#!/usr/bin/env python3

"""Defines the structure an audio frame."""

from fractions import Fraction
import numbers
import re
import typing

import numpy as np
import torch

from cutcutcodec.core.classes.frame import Frame
from cutcutcodec.core.classes.layout import Layout


class FrameAudio(Frame):
    """An audio sample packet with time information.

    Behaves like a torch tensor of shape (nb_channels, samples).
    The shape is consistent with pyav and torchaudio.
    Values are supposed to be between -1 and 1 but no verification is done.

    Attributes
    ----------
    channels : int
        The numbers of channels (readonly).
        For more informations about each channels, let see ``self.layout``.
    layout : cutcutcodec.core.classes.layout.Layout
        The signification of each channels (readonly).
    rate : int
        The frequency of the samples in Hz (readonly).
    samples : int
        The number of samples per channels (readonly).
    time : Fraction
        The time of the first sample of the frame in second (readonly).
    """

    def __new__(  # pylint: disable=W0222
        cls,
        time: Fraction | numbers.Real | str,
        rate: numbers.Integral,
        layout: Layout | str | numbers.Integral,
        data: torch.Tensor | np.ndarray | typing.Container,
        **kwargs,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        time : Fraction
            The time of the first sample of the frame in second.
        rate : int
            The frequency of the samples in Hz.
        layout : cutcutcodec.core.classes.layout.Layout or str or numbers.Integral
            The canonical name of the layout,
            let see ``cutcutcodec.core.classes.layout.Layout`` for the available layouts.
        data : arraylike
            Transmitted to ``cutcutcodec.core.classes.frame.Frame`` initialisator.
        **kwargs : dict
            Transmitted to ``cutcutcodec.core.classes.frame.Frame`` initialisator.
        """
        frame = super().__new__(cls, data, context=[time, rate, layout], **kwargs)
        frame.check_state()
        return frame

    def __repr__(self) -> str:
        """Compact and complete display of an evaluable version of the audio frame.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
        >>>
        >>> FrameAudio("2/4", 48000, "stereo", torch.zeros(2, 1024))
        FrameAudio('1/2', 48000, 'stereo', [[0., 0., 0., ..., 0., 0., 0.],
                                            [0., 0., 0., ..., 0., 0., 0.]])
        >>> _.to(torch.float16)
        FrameAudio('1/2', 48000, 'stereo', [[0., 0., 0., ..., 0., 0., 0.],
                                            [0., 0., 0., ..., 0., 0., 0.]],
                                           dtype=torch.float16)
        >>>
        """
        time_str = f"'{self.time}'" if int(self.time) != self.time else f"{self.time}"
        header = f"{self.__class__.__name__}({time_str}, {self.rate}, {repr(self.layout.name)}, "
        tensor_str = np.array2string(
            self.numpy(force=True), separator=", ", prefix=header, suffix=" "
        )
        if (infos := re.findall(r"\w+=[a-zA-Z0-9_\-.\"']+", repr(torch.Tensor(self)))):
            infos = "\n" + " "*len(header) + (",\n" + " "*len(header)).join(infos)
            return f"{header}{tensor_str},{infos})"
        return f"{header}{tensor_str})"

    def check_state(self) -> None:
        """Apply verifications.

        Raises
        ------
        AssertionError
            If something wrong in this frame.
        """
        assert isinstance(self.context[0], (Fraction, numbers.Real, str)), \
            self.context[0].__class__.__name__  # corresponds to time attribute
        self.context[0] = Fraction(self.context[0])
        assert isinstance(self.context[1], numbers.Integral), \
            self.context[1].__class__.__name__  # corresponds to rate attribute
        self.context[1] = int(self.context[1])
        assert self.context[1] > 0, self.context[1]  # corresponds to rate attribute
        assert isinstance(self.context[2], (Layout, str,  numbers.Integral)), \
            self.context[2].__class__.__name__  # corresponds to the layout
        if isinstance(self.context[2], (str, numbers.Integral)):
            self.context[2] = Layout(self.context[2])
        assert self.ndim == 2, self.shape
        assert self.shape[0] == len(self.context[2]), self.shape  # nb_channels
        assert self.dtype.is_floating_point, self.dtype

    @property
    def channels(self) -> int:
        """Return the number of channels.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, "stereo", torch.empty(2, 1024)).channels
        2
        >>>
        """
        return self.shape[0]

    @property
    def layout(self) -> Layout:
        """Return the signification of each channels.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, "stereo", torch.empty(2, 1024)).layout
        Layout('stereo')
        >>>
        """
        return self.context[2]

    @property
    def rate(self) -> int:
        """Return the frequency of the samples in Hz.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, "stereo", torch.empty(2, 1024)).rate
        48000
        >>>
        """
        return self.context[1]

    @property
    def samples(self) -> int:
        """Return the number of samples per channels.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, "stereo", torch.empty(2, 1024)).samples
        1024
        >>>
        """
        return self.shape[1]

    @property
    def time(self) -> Fraction:
        """Return the time of the first sample of the frame in second.

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, "stereo", torch.empty(2, 1024)).time
        Fraction(0, 1)
        >>>
        """
        return self.context[0]

    @property
    def timestamps(self) -> torch.Tensor:
        """Return the time value of each sample of the frame.

        The vector is cast on the same type than the samples and in the same device.
        The shape of the timestamps 1d vector is (self.samples,).

        Examples
        --------
        >>> import torch
        >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(1, 48000, "stereo", torch.empty(2, 1024)).timestamps
        tensor([1.0000, 1.0000, 1.0000,  ..., 1.0213, 1.0213, 1.0213])
        >>>
        """
        timestamps = torch.arange(self.samples, dtype=self.dtype, device=self.device)
        timestamps /= float(self.rate)
        timestamps += float(self.time)
        return timestamps
