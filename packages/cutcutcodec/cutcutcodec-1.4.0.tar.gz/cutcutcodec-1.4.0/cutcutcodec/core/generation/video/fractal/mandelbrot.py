#!/usr/bin/env python3

"""Allow to generate a fractal annimation."""

from fractions import Fraction
import math
import numbers
import typing

from sympy.core.basic import Basic
from sympy.core.symbol import Symbol
import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.container import ContainerInput
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.compilation.parse import parse_to_sympy
from cutcutcodec.core.compilation.sympy_to_torch import Lambdify
from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.generation.video.fractal.fractal import mandelbrot
from cutcutcodec.core.generation.video.fractal.geometry import deduce_all_bounds


class GeneratorVideoMandelbrot(ContainerInput):
    """Generation of an annimated mandelbrot fractal.

    Attributes
    ----------
    bounds : tuple[sympy.core.expr.Expr, ...]
        The four i_min, i_max, j_min and j_max bounds expressions of `t` (readonly).
    iterations : sympy.core.expr.Expr
        The maximum number of iterations function based on `t` (readonly).

    Examples
    --------
    >>> from cutcutcodec.core.generation.video.fractal.mandelbrot import GeneratorVideoMandelbrot
    >>> (stream,) = GeneratorVideoMandelbrot(
    ...     bounds={"i_min": -1.12, "i_max": 1.12, "j_min": -2.0, "j_max": 0.47},
    ...     iterations=256,
    ... ).out_streams
    >>> stream.snapshot(0, (10, 8))[..., 0]
    tensor([[0.0000, 0.0039, 0.0078, 0.0078, 0.0078, 0.0156, 0.0078, 0.0039],
            [0.0000, 0.0039, 0.0078, 0.0078, 0.0117, 0.0625, 0.0156, 0.0078],
            [0.0000, 0.0078, 0.0078, 0.0117, 0.1445, 1.0000, 1.0000, 0.0156],
            [0.0000, 0.0117, 0.0273, 0.0234, 1.0000, 1.0000, 1.0000, 0.0273],
            [0.0000, 0.0156, 0.0391, 1.0000, 1.0000, 1.0000, 1.0000, 0.0156],
            [0.0000, 0.0156, 0.0391, 1.0000, 1.0000, 1.0000, 1.0000, 0.0156],
            [0.0000, 0.0117, 0.0273, 0.0234, 1.0000, 1.0000, 1.0000, 0.0273],
            [0.0000, 0.0078, 0.0078, 0.0117, 0.1445, 1.0000, 1.0000, 0.0156],
            [0.0000, 0.0039, 0.0078, 0.0078, 0.0117, 0.0625, 0.0156, 0.0078],
            [0.0000, 0.0039, 0.0078, 0.0078, 0.0078, 0.0156, 0.0078, 0.0039]])
    >>>
    """

    def __init__(
        self,
        bounds: dict[str, Basic | numbers.Real | str],
        iterations: Basic | numbers.Real | str = 256,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        bounds : dict[str, str or sympy.Basic]
            The 4 bounds expressions of the complex plan limit of pixels.
            The admitted keys are defined in
            ``cutcutcodec.core.generation.video.fractal.geometry.SYMBOLS``.
            If an expression is used, only the symbol `t` is available.
        iterations : str or sympy.Basic
            The expression of the maximum iterations number.
            If a function is used, only the symbol `t` is available.
            The final value is the integer part of the result. It has to be > 0.
        """
        assert isinstance(bounds, dict), bounds.__class__.__name__
        assert all(isinstance(name, str) for name in bounds), bounds
        all_bounds = {
            name: parse_to_sympy(expr, symbols={"t": Symbol("t", real=True, positive=True)})
            for name, expr in bounds.items()
        }
        assert all(set(map(str, e.free_symbols)).issubset({"t"}) for e in all_bounds.values())
        all_bounds = deduce_all_bounds(**all_bounds)
        iters = parse_to_sympy(iterations, symbols={"t": Symbol("t", real=True, positive=True)})

        self._bounds = (
            all_bounds["i_min"],
            all_bounds["i_max"],
            all_bounds["j_min"],
            all_bounds["j_max"],
        )
        self._iters = iters

        super().__init__([_StreamVideoMandelbrot(self)])

    def _getstate(self) -> dict:
        return {
            "bounds": dict(zip(("i_min", "i_max", "j_min", "j_max"), map(str, self._bounds))),
            "iterations": str(self.iterations),
        }

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"bounds", "iterations"}, set(state)
        GeneratorVideoMandelbrot.__init__(self, **state)

    @property
    def bounds(self) -> tuple[Basic, Basic, Basic, Basic]:
        """Return the four i_min, i_max, j_min and j_max bounds expressions of `t`."""
        return self._bounds

    @property
    def iterations(self) -> Basic:
        """Return the maximum number of iterations function based on `t`."""
        return self._iters


class _StreamVideoMandelbrot(StreamVideo):
    """Fractal video stream."""

    colorspace = Colorspace.from_default_target_rgb()

    def __init__(self, node: GeneratorVideoMandelbrot):
        assert isinstance(node, GeneratorVideoMandelbrot), node.__class__.__name__
        super().__init__(node)
        self._bounds_func = None  # cache

    def _get_func(self) -> callable:
        """Allow to "compile" bounds and iterations equations at the last moment."""
        if self._bounds_func is None:
            self._bounds_func = Lambdify(
                (*self.node.bounds, self.node.iterations),
                safe=False,
                compile=False,
            )
        return self._bounds_func

    def _get_complex_map_and_iter_max(
        self, timestamp: Fraction, mask: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, int]:
        """Compute the complex map, one complex number by pixel."""
        func = self._get_func()
        args = {"t": torch.tensor(timestamp, dtype=torch.float32)} if "t" in func.args else {}
        i_min, i_max, j_min, j_max, iters = func(**args)
        iter_max = int(iters.item())
        assert iter_max > 0, \
            f"for t={timestamp}, {self.node.iterations} gives {iter_max}, it has to be > 0"
        i_min, i_max, j_min, j_max = i_min.item(), i_max.item(), j_min.item(), j_max.item()
        imag, real = torch.meshgrid(
            torch.linspace(i_min, i_max, mask.shape[0], dtype=torch.float64),
            torch.linspace(j_min, j_max, mask.shape[1], dtype=torch.float64),
            indexing="ij",
        )
        cpx = real + 1j*imag
        return cpx, iter_max

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no audio frame at timestamp {timestamp} (need >= 0)")

        cpx, iter_max = self._get_complex_map_and_iter_max(timestamp, mask)
        # real = self._to_masked_items(real, mask)
        # imag = self._to_masked_items(imag, mask)
        frame = mandelbrot(cpx.numpy(force=True), iter_max)
        # frame = self._from_masked_items(torch.from_numpy(iterations), mask)
        return torch.from_numpy(frame)[:, :, None]

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> Fraction | float:
        return math.inf
