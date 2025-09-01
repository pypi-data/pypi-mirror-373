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

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.layout import AllLayouts
from cutcutcodec.core.classes.layout import Layout
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.compilation.parse import parse_to_sympy
from cutcutcodec.core.compilation.sympy_to_torch import Lambdify
from cutcutcodec.core.exceptions import OutOfTimeRange


class FilterAudioEquation(Filter):
    """Apply any equation on each channels.

    The relation can not mix differents timestamps (no convolution).

    Attributes
    ----------
    layout : cutcutcodec.core.classes.layout.Layout
        The signification of each channels (readonly).
    signals : list[sympy.core.expr.Expr]
        The amplitude expression of the differents channels (readonly).

    Examples
    --------
    >>> from cutcutcodec.core.filter.audio.equation import FilterAudioEquation
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> (stream_in,) = GeneratorAudioNoise(0).out_streams
    >>> stream_in.snapshot(0, 48000, 4)
    FrameAudio(0, 48000, 'stereo', [[ 0.44649088,  0.8031031 , -0.25397146,
                                     -0.1199106 ],
                                    [-0.8036704 ,  0.72772765,  0.17409873,
                                      0.42185044]])
    >>> (stream_out,) = FilterAudioEquation([stream_in], "fl_0 + t", "fl_0 + fr_0").out_streams
    >>> stream_out.snapshot(0, 48000, 4)
    FrameAudio(0, 48000, 'stereo', [[ 0.44649088,  0.80312395, -0.2539298 ,
                                     -0.11984809],
                                    [-0.35717952,  1.        , -0.07987273,
                                      0.30193985]])
    >>>
    """

    def __init__(
        self,
        in_streams: typing.Iterable[StreamAudio],
        *signals: Basic | numbers.Real | str,
        layout: Layout | str | numbers.Integral = None,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        *signals : str or sympy.Basic
            The amplitude function of each channel respectively.
            The channels are interpreted like is describe in
            ``cutcutcodec.core.classes.frame_audio.FrameAudio``.
            The number of expressions correspond to the number of channels.
            The return values will be cliped to stay in the range [-1, 1].
            If the expression gives a complex, the real part is taken.
            The variables that can be used in these functions are the following:

                * t : The time in seconds since the beginning of the audio.
                * x_i : With `x` any channels available
                    for ``cutcutcodec.core.classes.layout.Layout.channels``
                    and `i` the stream index, i starts from 0 included.
                    examples: `fl_0` for front left of the stream 0.
        layout: cutcutcodec.core.classes.layout.Layout or str or int, optional
            The audio layout to associate to each equation,
            let see ``cutcutcodec.core.classes.layout.Layout`` for more details.
            By default, the layout is automaticaly detected from the number of equations.
        """
        # check
        assert isinstance(in_streams, typing.Iterable), in_streams.__class__.__name__
        in_streams = tuple(in_streams)
        assert all(isinstance(s, StreamAudio) for s in in_streams), in_streams
        assert all(isinstance(s, (Basic, numbers.Real, str)) for s in signals), signals
        assert layout is None or isinstance(layout, (Layout, str,  numbers.Integral)), \
            layout.__class__.__name__

        # initialisation
        self._signals = [
            parse_to_sympy(s, symbols={"t": Symbol("t", real=True, positive=True)})
            for s in signals
        ]
        super().__init__(in_streams, in_streams)

        if not self.in_streams and not self._signals:
            self._free_symbs = set()
            self._layout = None
            return
        self._signals = self._signals or [Zero()]
        self._free_symbs = set.union(*(c.free_symbols for c in self._signals))
        self._layout = Layout(layout or len(self._signals))
        assert len(self._layout) == len(self._signals), (
            f"the layout {self._layout.name} contains {len(self._layout)} channels "
            f"but {len(self._signals)} equations are provided."
        )

        # check
        pattern = r"t|" + r"|".join(fr'{p}_\d+' for p in sorted(AllLayouts().individuals))
        if excess := {s for s in self._free_symbs if re.fullmatch(pattern, str(s)) is None}:
            raise AssertionError(
                f"the vars {excess} from the expr {self._signals} "
                f"doesn't match the required format {pattern}"
            )
        symbs = (
            [re.fullmatch(r"(?P<channel>[a-z]+)_(?P<index>\d+)", str(s)) for s in self._free_symbs]
        )
        symbs = [s for s in symbs if s is not None]
        if excess := (
            {s["channel"] for s in symbs} - set(AllLayouts().individuals)
        ):
            raise AssertionError(f"the vars {excess} are not in {set(AllLayouts().individuals)}")
        if excess := ({int(s["index"]) for s in symbs} - set(range(len(self.in_streams)))):
            raise AssertionError(
                f"only {len(self.in_streams)} input stream, {excess} is not reachable"
            )

        super().__init__(self.in_streams, [_StreamAudioEquation(self)])

    def _getstate(self) -> dict:
        return {
            "signals": [str(c) for c in self._signals],
            "layout": (self._layout.name if self._layout is not None else None),
        }

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"signals", "layout"}, set(state)
        FilterAudioEquation.__init__(self, in_streams, *state["signals"], layout=state["layout"])

    @property
    def layout(self) -> Layout:
        """Return the signification of each channels."""
        return self._layout

    @property
    def signals(self) -> list[Basic]:
        """Return the amplitude expression of the differents channels."""
        return self._signals.copy()

    @property
    def free_symbols(self) -> set[Symbol]:
        """Return the set of the diferents used symbols."""
        return self._free_symbs.copy()


class _StreamAudioEquation(StreamAudio):
    """Channels field parameterized by time and incoming samples."""

    def __init__(self, node: FilterAudioEquation):
        assert isinstance(node, FilterAudioEquation), node.__class__.__name__
        super().__init__(node)
        self._signals_func = None  # cache

    def _get_signals_func(self) -> callable:
        """Allow to "compile" equations at the last moment."""
        if self._signals_func is None:
            free_symbs = Tuple(*self.node.signals).free_symbols
            shapes = {frozenset(s for s in free_symbs if str(s) != "t")}
            self._signals_func = Lambdify(self.node.signals, shapes=shapes, safe=True)
        return self._signals_func

    def _get_inputs(
        self, timestamp: Fraction, rate: int, samples: int
    ) -> dict[str, float | torch.Tensor]:
        """Help for getting input vars."""
        symbs = {}
        in_frames = {}  # cache
        for symb in self.node.free_symbols:
            symb = str(symb)
            if symb == "t":
                time_field = torch.arange(samples, dtype=torch.float32)
                time_field /= float(rate)  # not linspace for avoid round mistakes
                time_field += float(timestamp)
                symbs["t"] = time_field  # 1d vect
                continue
            match = re.fullmatch(r"(?P<channel>[a-z]+)_(?P<index>\d+)", symb)
            if (stream_index := int(match["index"])) not in in_frames:
                in_frames[stream_index] = (
                    self.node.in_streams[stream_index]  # pylint: disable=W0212
                    ._snapshot(timestamp, rate, samples)
                )
            try:
                channel_index = (
                    [n for n, _ in self.node.in_streams[stream_index].layout.channels]
                    .index(match["channel"])
                )
            except ValueError as err:
                raise NotImplementedError(
                    f"symbol {match['channel']} not allowed, "
                    f"only {self.node.in_streams[stream_index].layout.channels} are allowed"
                ) from err
            symbs[symb] = in_frames[stream_index][channel_index, :]  # 1d vect
        return symbs

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        # verif
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no audio frame at timestamp {timestamp} (need >= 0)")

        # calculation
        signals = self._get_signals_func()(**self._get_inputs(timestamp, rate, samples))

        # correction + cast
        frame = FrameAudio(
            timestamp,
            rate,
            self.node.layout,
            torch.empty((len(self.node.signals), samples)),
        )
        for i, signal in enumerate(signals):
            if signal.dtype.is_complex:
                signal = torch.real(signal)
            torch.nan_to_num(signal, nan=0.0, posinf=1.0, neginf=-1.0, out=signal)
            torch.clip(signal, -1.0, 1.0, out=signal)
            frame[i, :] = signal

        return frame

    @property
    def beginning(self) -> Fraction:
        index = [re.fullmatch(r"[a-z]+_(?P<index>\d+)", str(s)) for s in self.node.free_symbols]
        index = {int(i["index"]) for i in index if i is not None}
        return min((self.node.in_streams[i].beginning for i in index), default=Fraction(0))

    @property
    def duration(self) -> Fraction | float:
        index = [re.fullmatch(r"[a-z]+_(?P<index>\d+)", str(s)) for s in self.node.free_symbols]
        index = {int(i["index"]) for i in index if i is not None}
        streams = (self.node.in_streams[i] for i in index)
        end = max((s.beginning + s.duration for s in streams), default=math.inf)
        return end - self.beginning

    @property
    def layout(self) -> Layout:
        """Return the signification of each channels."""
        return self.node.layout
