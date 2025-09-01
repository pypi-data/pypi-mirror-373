#!/usr/bin/env python3

"""Basic linear casts between different audio layouts.

For coefficient downmixing, based on https://www.rfc-editor.org/rfc/rfc7845#section-5.1.1.5
and http://www.atsc.org/wp-content/uploads/2015/03/A52-201212-17.pdf p96
"""

import numbers

from sympy.core.basic import Basic
from sympy.core.symbol import Symbol
import networkx
import numpy as np
import torch

from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.layout import AllLayouts, Layout


class LinearAudioConvertor:
    """Convertion of a specific layout thanks the transition matrix.

    Parameters
    ----------
    in_layout : cutcutcodec.core.classes.layout.Layout
        The layout of the input frames (readonly).
    out_layout : cutcutcodec.core.classes.layout.Layout
        The layout of the converted frames (readonly).
    """

    def __init__(self, in_layout: Layout, out_layout: Layout, matrix: np.ndarray[np.float64]):
        """Initialise and create the class.

        Parameters
        ----------
        in_layout : cutcutcodec.core.classes.layout.Layout
            The layout of the input frames.
        out_layout : cutcutcodec.core.classes.layout.Layout
            The layout of the converted frames.
        matrix : array
            The linear transformation matrix.
        """
        assert isinstance(in_layout, Layout), in_layout.__class__.__name__
        assert isinstance(out_layout, Layout), out_layout.__class__.__name__
        assert isinstance(matrix, np.ndarray), matrix.__class__.__name__
        assert matrix.shape == (len(out_layout), len(in_layout))
        self._in_layout = in_layout
        self._out_layout = out_layout
        self._matrix = torch.from_numpy(matrix)

    def __call__(self, frame: FrameAudio) -> FrameAudio:
        """Apply the conversion of the audio frame.

        Parameters
        ----------
        frame : cutcutcodec.core.classes.frame_audio.FrameAudio
            The input frame audio with the layout ``in_layout``.

        Returns
        -------
        cutcutcodec.core.classes.frame_audio.FrameAudio
            The input ``frame`` converted in the layout ``out_layout``.
        """
        assert isinstance(frame, FrameAudio), frame.__class__.__name__
        assert frame.layout == self._in_layout, (frame.layout, self._in_layout)
        out_frame = self._matrix.to(device=frame.device, dtype=frame.dtype) @ torch.Tensor(frame)
        out_frame = FrameAudio(frame.time, frame.rate, self._out_layout, out_frame)
        return out_frame

    @property
    def equations(self) -> dict[Symbol, Basic]:
        """To each output channel, associate the equation.

        The symbols are the real cannonocal name of each channels.
        """
        in_vars = [Symbol(v, real=True) for v, _ in self._in_layout.channels]
        out_vars = [Symbol(v, real=True) for v, _ in self._out_layout.channels]
        eqs = self._matrix.numpy(force=True) @ np.array([in_vars], dtype=object).transpose()
        return dict(zip(out_vars, eqs[:, 0]))

    @property
    def in_layout(self) -> Layout:
        """Return the layout of the input frames."""
        return self._in_layout

    @property
    def out_layout(self) -> Layout:
        """Return the layout of the converted frames."""
        return self._out_layout


class AudioConvertor(LinearAudioConvertor):
    """Combine the matrix in order to find the complete transformation chain.

    Examples
    --------
    >>> import torch
    >>> _ = torch.manual_seed(0)
    >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
    >>> from cutcutcodec.core.filter.mix.audio_cast import AudioConvertor
    >>> frame_in = FrameAudio(0, 1, "5.1", torch.randn((6, 1024)))
    >>> (conv := AudioConvertor("5.1", "mono"))
    AudioConvertor('5.1', 'mono')
    >>> torch.round(conv(frame_in), decimals=3)
    FrameAudio(0, 1, 'mono', [[-0.296,  0.279, -0.775, ..., -2.045, -2.013,
                               -0.316]])
    >>> torch.round(
    ...     AudioConvertor("stereo", "mono")(AudioConvertor("5.1", "stereo")(frame_in)), decimals=3
    ... )
    FrameAudio(0, 1, 'mono', [[-0.296,  0.279, -0.775, ..., -2.045, -2.013,
                               -0.316]])
    >>>
    """

    def __init__(
        self,
        in_layout: Layout | str | numbers.Integral,
        out_layout: Layout | str | numbers.Integral,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_layout : cutcutcodec.core.classes.layout.Layout
            Casted and transmitted to
            ``cutcutcodec.core.filter.mix.audio_cast.LinearAudioConvert`` initialisator.
        out_layout : cutcutcodec.core.classes.layout.Layout
            Casted and transmitted to
            ``cutcutcodec.core.filter.mix.audio_cast.LinearAudioConvert`` initialisator.
        """
        in_layout, out_layout = Layout(in_layout), Layout(out_layout)

        # search the path
        graph = networkx.from_edgelist(
            (
                (p_in, p_out, {"matrix": matrix, "weight": 1.0})
                for (p_in, p_out), matrix in self.all_layouts().items()
            ),
            create_using=networkx.DiGraph,
        )
        try:
            path = networkx.dijkstra_path(graph, in_layout.name, out_layout.name, weight="weight")
        except ValueError as err:
            raise NotImplementedError(
                f"impossible conversion from {in_layout.name} to {out_layout.name}"
            ) from err

        # compute the matrix
        if len(path) == 1:  # case identity
            path = [path[0], path[0]]
        matrix = np.array(graph.get_edge_data(path[0], path[1])["matrix"])
        for p_in, p_out in zip(path[1:-1], path[2:]):
            matrix = np.array(graph.get_edge_data(p_in, p_out)["matrix"]) @ matrix

        super().__init__(in_layout, out_layout, matrix)

    def __repr__(self):
        """Print a better representation of the object for debug."""
        return (
            f"{self.__class__.__name__}"
            f"({repr(self._in_layout.name)}, {repr(self._out_layout.name)})"
        )

    @staticmethod
    def all_layouts() -> dict[tuple[str, str], list[list[float]]]:
        """To each layouts, associate the conversion matrix."""
        downmixing = {
            ("stereo", "mono"): (  # 'fl', 'fr'
                [[0.500000, 0.500000]]  # be carefull of phase inversion
            ),
            ("3.0", "stereo"): (  # 'fl', 'fr', 'fc'
                [[0.585786, 0.000000, 0.414214],
                 [0.000000, 0.585786, 0.414214]]
            ),
            ("quad", "stereo"): (  # 'fl', 'fr', 'bl', 'br'
                [[0.422650, 0.000000, 0.366025, 0.211325],
                 [0.000000, 0.422650, 0.211325, 0.366025]]
            ),
            ("5.0", "stereo"): (  # 'fl', 'fr', 'fc', 'bl', 'br'
                [[0.650802, 0.000000, 0.460186, 0.563611, 0.325401],
                 [0.000000, 0.650802, 0.460186, 0.325401, 0.563611]]
            ),
            ("5.1", "stereo"): (  # 'fl', 'fr', 'fc', 'lfe', 'bl', 'br'
                [[0.529067, 0.000000, 0.374107, 0.374107, 0.458186, 0.264534],
                 [0.000000, 0.529067, 0.374107, 0.374107, 0.264534, 0.458186]]
            ),
            ("6.1", "stereo"): (  # 'fl', 'fr', 'fc', 'lfe', 'bc', 'sl', 'sr'
                [[0.455310, 0.000000, 0.321953, 0.321953, 0.278819, 0.394310, 0.227655],
                 [0.000000, 0.455310, 0.321953, 0.321953, 0.278819, 0.227655, 0.394310]]
            ),
            ("7.1", "stereo"): (  # 'fl', 'fr', 'fc', 'lfe', 'bl', 'br', 'sl', 'sr'
                [[0.388631, 0.000000, 0.274804, 0.274804, 0.336565, 0.194316, 0.336565, 0.194316],
                 [0.000000, 0.388631, 0.274804, 0.274804, 0.194316, 0.336565, 0.194316, 0.336565]]
            ),
        }
        upmixing = {
            ("mono", "stereo"): (  # 'fc'
                [[1.000000],
                 [1.000000]]
            ),
        }
        identity = {
            (c, c): [[1.0 if d2 == d1 else 0.0 for d2 in d] for d1 in d]
            for c, d in AllLayouts().layouts.items()
        }
        return downmixing | upmixing | identity
