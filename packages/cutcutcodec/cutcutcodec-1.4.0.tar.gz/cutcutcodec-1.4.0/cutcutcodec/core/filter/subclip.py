#!/usr/bin/env python3

"""The common part for ``FilterAudioSubclip`` and ``FilterVideoSubclip``."""

from fractions import Fraction
import math
import numbers


class FilterSubclip:
    """Extract a segment from a stream.

    Attributes
    ----------
    delay : Fraction
        The offset from the parent stream (readonly).
    duration_max : Fraction or inf
        The maximum duration beyond which the flows do not return anything (readonly).
    """

    def __init__(self, delay: numbers.Real = Fraction(0), duration_max: numbers.Real = math.inf):
        """Initialise and create the class.

        Parameters
        ----------
        delay: numbers.Real, default=0
            The time lapse from the parent stream.
            0 means that the beginning of the new stream coincides
            with the beginning of the stream that arrives at this node.
            A delay of x >= 0 seconds means that
            the first x seconds of the stream arriving on this filter are discarded.
        duration_max : numbers.Real, default=inf
            The maximal duration of the new stream.
        """
        assert isinstance(delay, numbers.Real), delay.__class__.__name__
        assert math.isfinite(delay) and delay >= 0, delay
        assert isinstance(duration_max, numbers.Real), duration_max.__class__.__name__
        assert duration_max > 0, duration_max
        self._delay = Fraction(delay)
        self._duration_max = Fraction(duration_max) if math.isfinite(duration_max) else duration_max

    def _getstate(self) -> dict:
        return {"delay": str(self.delay), "duration_max": str(self.duration_max)}

    @property
    def delay(self) -> Fraction:
        """Return the offset from the parent stream."""
        return self._delay

    @property
    def duration_max(self) -> Fraction:
        """Return the maximum duration beyond which the flows do not return anything."""
        return self._duration_max
