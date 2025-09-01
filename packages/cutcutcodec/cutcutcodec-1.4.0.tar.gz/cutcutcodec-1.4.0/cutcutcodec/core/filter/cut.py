#!/usr/bin/env python3

"""The common part for ``FilterAudioCut`` and ``FilterVideoCut``."""

from fractions import Fraction
import math
import numbers
import typing

from cutcutcodec.core.classes.stream import Stream


class FilterCut:
    """Splits the stream at the given positions.

    Attributes
    ----------
    limits : list[Fraction]
        The ordered limits of each slices in seconds (readonly).
    """

    def init(self, in_streams: typing.Iterable[Stream], stream_cls: type, *limits: numbers.Real):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        stream_cls : type
            A subclass of ``cutcutcodec.core.classes.stream.Stream``.
            It is the constructor of the `out_streams` of self.
        limits : numbers.Real
            The temporal limits between the differents slices.
            The timings are like a duration relative to the beginning of the first stream.

        Returns
        -------
        _limits : list[Fraction]
            The verificated limits.
        out_streams : list[cutcutcodec.core.classes.stream.Stream]
            The instanciated out streams
        """
        assert issubclass(stream_cls, Stream), stream_cls.__name__
        assert all(
            isinstance(lim, numbers.Real) and math.isfinite(lim) and lim >= 0 for lim in limits
        )

        _limits = list(map(Fraction, limits))
        assert sorted(_limits) == _limits, f"limits are not sorted, {limits}"
        assert len(set(_limits)) == len(_limits), f"some limits are equal, {limits}"

        if not in_streams:
            return _limits, []

        beginning = min(s.beginning for s in in_streams)
        abs_limits = [lim + beginning for lim in _limits]
        abs_limits_min = [-math.inf] + abs_limits
        abs_limits_max = abs_limits + [math.inf]
        return (
            _limits,
            [
                stream_cls(self, index, l_min, l_max)
                for l_min, l_max in zip(abs_limits_min, abs_limits_max)
                for index in range(len(in_streams))
            ],
        )

    def _getstate(self) -> dict:
        return {"limits": list(map(str, self.limits))}

    @property
    def limits(self):
        """Return the ordered limits of each slices in seconds."""
        return self._limits.copy()
