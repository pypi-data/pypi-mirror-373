#!/usr/bin/env python3

"""Interface for the nodes that require a random seed."""

import hashlib
import numbers
import random
import struct
import typing


class Seedable:
    """Interface for appening a seed management.

    Attributes
    ----------
    seed : float
        The value of the seed between [0, 1[ (readonly).
    seed_bytes : bytes
        The hashed version of the seed.
        Contains 32 bytes, ie 256 bits.
    """

    def __init__(self, seed: typing.Optional[numbers.Real] = None):
        """Initialise and create the class.

        Parameters
        ----------
        seed : numbers.Real, optional
            The random seed to have a repeatability.
            The value must be between 0 included and 1 excluded.
            If not provided, the seed is chosen randomly.
        """
        if seed is None:
            seed = random.random()
        assert isinstance(seed, numbers.Real), seed.__class__.__name__
        assert 0 <= seed < 1, seed
        self._seed = float(seed)
        self._seed_bytes = None

    def _getstate_seed(self, state: typing.Optional[dict] = None) -> dict:
        """Fast helper for getstate."""
        if state is None:
            return {"seed": self._seed}
        return state | {"seed": self._seed}

    def _setstate_seed(self, state: dict) -> None:
        """Fast helper for setstate."""
        Seedable.__init__(self, state["seed"])

    @property
    def seed(self) -> float:
        """Return the value of the seed between 0 and 1.

        Examples
        --------
        >>> from fractions import Fraction
        >>> from cutcutcodec.core.interfaces.seedable import Seedable
        >>> Seedable(0).seed  # int
        0.0
        >>> Seedable(Fraction(1, 2)).seed  # fraction
        0.5
        >>> Seedable(0.5).seed  # float
        0.5
        >>>
        """
        return self._seed

    @property
    def seed_bytes(self) -> bytes:
        r"""Return the bytes seed string, containing 256 bits.

        Examples
        --------
        >>> from cutcutcodec.core.interfaces.seedable import Seedable
        >>> Seedable(0.25).seed_bytes
        b"'/x\x03m\xb6r\x1f|\xf7DC\x15\xe5\xf66\x04&\xd1L=Dmj\xe8\xa8\x9e\xf7\r\x13@\x02"
        >>>
        """
        if self._seed_bytes is None:
            self._seed_bytes = hashlib.sha256(struct.pack("d", self._seed)).digest()
        return self._seed_bytes
