#!/usr/bin/env python3

"""Allow to generate sound from mathematical functions."""

import numbers

from sympy.core.basic import Basic

from cutcutcodec.core.classes.container import ContainerInput
from cutcutcodec.core.classes.layout import Layout
from cutcutcodec.core.filter.audio.equation import FilterAudioEquation


class GeneratorAudioEquation(FilterAudioEquation, ContainerInput):
    """Generate an audio stream whose channels are defened by any equations.

    It is a particular case of ``cutcutcodec.core.filter.equation.FilterAudioEquation``.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.generation.audio.equation import GeneratorAudioEquation
    >>> (stream,) = GeneratorAudioEquation("sin(2*pi*440*t)").out_streams
    >>> torch.round(stream.snapshot(0, 3520, 8), decimals=3)
    FrameAudio(0, 3520, 'mono', [[ 0.   ,  0.707,  1.   ,  0.707,  0.   ,
                                  -0.707, -1.   , -0.707]])
    >>>
    """

    def __init__(
        self,
        *signals: Basic | numbers.Real | str,
        layout: Layout | str | numbers.Integral = None,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        *signals : str or sympy.Basic
            Transmitted to the
            ``cutcutcodec.core.filter.audio.equation.FilterAudioEquation`` initialisator.
            But the only available vars is `t`.
        layout : cutcutcodec.core.classes.layout.Layout or str or int, optional
            Transmitted to the
            ``cutcutcodec.core.filter.audio.equation.FilterAudioEquation`` initialisator.
        """
        FilterAudioEquation.__init__(self, [], *signals, layout=layout)
        ContainerInput.__init__(self, self.out_streams)
        if excess := set(map(str, self._free_symbs)) - {"t"}:
            raise ValueError(f"only t symbol is allowed, not {excess}")
