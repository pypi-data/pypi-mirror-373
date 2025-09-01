#!/usr/bin/env python3

"""Allow to filter independentely each audio and video samples by any equation."""

from fractions import Fraction
import math
import numbers
import re
import typing

from sympy.core.basic import Basic
from sympy.core.containers import Tuple
from sympy.core.numbers import Zero
from sympy.core.symbol import Symbol
import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.compilation.parse import parse_to_sympy
from cutcutcodec.core.compilation.sympy_to_torch import Lambdify
from cutcutcodec.core.exceptions import OutOfTimeRange


class FilterVideoEquation(Filter):
    """Apply any equation on each pixels.

    The relation is only between the pixel at the same timestamp at the same position.

    Attributes
    ----------
    colors : list[sympy.core.expr.Expr]
        The luminosity expression of the differents channels (readonly).

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.filter.video.equation import FilterVideoEquation
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>> (stream_in,) = GeneratorVideoNoise(0).out_streams
    >>> (stream_out,) = FilterVideoEquation([stream_in], "r0", "(r0+g0+b0)/3", 0).out_streams
    >>> torch.round(stream_in.snapshot(0, (2, 2)), decimals=4)
    FrameVideo(0, [[[0.4976, 0.3948, 0.9274],
                    [0.1507, 0.224 , 0.9958]],
    <BLANKLINE>
                   [[0.7209, 0.3724, 0.4915],
                    [0.921 , 0.0118, 0.8138]]])
    >>> torch.round(stream_out.snapshot(0, (2, 2)), decimals=4)
    FrameVideo(0, [[[0.4976, 0.6066, 0.    ],
                    [0.1507, 0.4568, 0.    ]],
    <BLANKLINE>
                   [[0.7209, 0.5283, 0.    ],
                    [0.921 , 0.5822, 0.    ]]])
    >>>
    """

    def __init__(
        self,
        in_streams: typing.Iterable[StreamVideo],
        *colors: Basic | numbers.Real | str,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        *colors : str or sympy.Basic
            The brightness of the color channels.
            The channels are interpreted like is describe in
            ``cutcutcodec.core.classes.frame_video.FrameVideo``.
            The value is 0 for min brightness and 1 for the max.
            If the expression gives a complex, the module is taken.
            The variables that can be used in these functions are the following:

                * i : The relative position along the vertical axis (numpy convention).
                    This value evolves between -1 and 1.
                * j : The relative position along the horizontal axis (numpy convention).
                    This value evolves between -1 and 1.
                * t : The time in seconds since the beginning of the video.
                * ri: The red channel of the stream index i, i starts from 0 included.
                    This value evolves between 0 (dark) and 1 (light).
                * gi: The green channel of the stream index i, i starts from 0 included.
                    This value evolves between 0 (dark) and 1 (light).
                * bi: The blue channel of the stream index i, i starts from 0 included.
                    This value evolves between 0 (dark) and 1 (light).
                * ai: The alpha channel of the stream index i, i starts from 0 included.
                    This value evolves between 0 (transparent) and 1 (blind).
        """
        # check
        assert isinstance(in_streams, typing.Iterable), in_streams.__class__.__name__
        in_streams = tuple(in_streams)
        assert all(isinstance(s, StreamVideo) for s in in_streams), in_streams
        assert all(isinstance(c, (Basic, numbers.Real, str)) for c in colors), colors
        assert len(colors) <= 4, len(colors)

        # initialisation
        self._colors = [
            parse_to_sympy(
                c,
                symbols={
                    "t": Symbol("t", real=True, positive=True),
                    "i": Symbol("i", real=True),
                    "j": Symbol("j", real=True),
                }
            )
            for c in colors
        ]
        Filter.__init__(self, in_streams, in_streams)
        if not self.in_streams and not self._colors:
            self._free_symbs = set()
            return
        self._colors = self._colors or [Zero()]
        self._free_symbs = set.union(*(c.free_symbols for c in self._colors))

        # check
        if excess := (
            {s for s in self._free_symbs if re.fullmatch(r"i|j|t|[rgba]\d+", str(s)) is None}
        ):
            raise ValueError(f"only i, j, t, ri, gi, bi and ai symbols are allowed, not {excess}")
        if excess := (
            {
                s for s in self._free_symbs
                if re.fullmatch(r"[rgba]\d+", str(s)) is not None
                and int(str(s)[1:]) >= len(self.in_streams)
            }
        ):
            raise ValueError(f"only {len(self.in_streams)} input stream, {excess} is not reachable")

        Filter.__init__(self, self.in_streams, [_StreamVideoEquation(self)])

    def _getstate(self) -> dict:
        return {"colors": [str(c) for c in self.colors]}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"colors"}, set(state)
        FilterVideoEquation.__init__(self, in_streams, *state["colors"])

    @property
    def colors(self) -> list[Basic]:
        """Return the luminosity expression of the differents channels."""
        return self._colors.copy()

    @property
    def free_symbols(self) -> set[Symbol]:
        """Return the set of the diferents used symbols."""
        return self._free_symbs.copy()


class _StreamVideoEquation(StreamVideo):
    """Color field parameterized by time, position and incoming pixels."""

    colorspace = Colorspace.from_default_working()

    def __init__(self, node: FilterVideoEquation):
        assert isinstance(node, FilterVideoEquation), node.__class__.__name__
        super().__init__(node)
        self._colors_func = None  # cache
        self._fields = None  # cache

    def _get_colors_func(self) -> callable:
        """Allow to "compile" equations at the last moment."""
        if self._colors_func is None:
            free_symbs = Tuple(*self.node.colors).free_symbols
            cst_args = {s for s in free_symbs if str(s) in {"i, j"}}
            shapes = {frozenset(s for s in free_symbs if str(s) != "t")}
            self._colors_func = Lambdify(
                self.node.colors, cst_args=cst_args, shapes=shapes
            )
        return self._colors_func

    def _get_fields(self, mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Return the i and j field, minimising realloc by cache.

        Returns a new copy each time.
        """
        height, width = mask.shape
        if self._fields is None or self._fields[0].shape != (height, width):
            self._fields = torch.meshgrid(
                torch.linspace(-1.0, 1.0, height, device=mask.device),
                torch.linspace(-1.0, 1.0, width, device=mask.device),
                indexing="ij",
            )
        return self._fields

    def _get_inputs(
        self, timestamp: Fraction, mask: torch.Tensor
    ) -> dict[str, float | torch.Tensor]:
        """Help for getting input vars."""
        symbs = {}
        in_frames = {}  # cache
        for symb in self.node.free_symbols:
            symb = str(symb)
            if (func := {
                "i": lambda: self._get_fields(mask)[0],
                "j": lambda: self._get_fields(mask)[1],
                "t": lambda: torch.tensor(timestamp, dtype=torch.float32),
            }.get(symb, None)) is not None:
                symbs[symb] = func()
                continue
            stream_index = int(symb[1:])
            if stream_index not in in_frames:
                in_frames[stream_index] = (
                    self.node.in_streams[stream_index]  # pylint: disable=W0212
                    ._snapshot(timestamp, mask)
                )
            frame = in_frames[stream_index]
            if symb[0] in {"r", "g", "b"}:
                if frame.shape[2] in {1, 2}:
                    symbs[symb] = frame[..., 0]
                else:
                    symbs[symb] = frame[..., {"r": 0, "g": 1, "b": 2}[symb[0]]]
            elif symb[0] == "a":
                if frame.shape[2] in {2, 4}:
                    symbs[symb] = frame[..., -1]
                else:
                    symbs[symb] = torch.tensor(1.0, dtype=torch.float32)
            else:
                raise NotImplementedError(f"only i, j, t, r, g, b and are allowed, not {symb}")
        return symbs

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        # verif
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no video frame at timestamp {timestamp} (need >= 0)")

        # calculation
        colors = self._get_colors_func()(**self._get_inputs(timestamp, mask))

        # correction
        # next code if twice faster than
        # torch.cat([(c.abs() if c.dtype.is_complex else c)[:, :, None] for c in colors], dim=2)
        frame = torch.empty((*mask.shape, len(self.node.colors)))
        for i, col in enumerate(colors):
            if col.dtype.is_complex:
                col = torch.abs(col)
            frame[:, :, i] = col

        return frame

    @property
    def beginning(self) -> Fraction:
        index = (
            {int(str(s)[1:]) for s in self.node.free_symbols if re.fullmatch(r"[rgba]\d+", str(s))}
        )
        return min((self.node.in_streams[i].beginning for i in index), default=Fraction(0))

    @property
    def duration(self) -> Fraction | float:
        index = (
            {int(str(s)[1:]) for s in self.node.free_symbols if re.fullmatch(r"[rgba]\d+", str(s))}
        )
        streams = (self.node.in_streams[i] for i in index)
        end = max((s.beginning + s.duration for s in streams), default=math.inf)
        return end - self.beginning
