#!/usr/bin/env python3

"""Generate an audio noise signal."""

from fractions import Fraction
import math
import numbers
import typing

import numpy as np

from cutcutcodec.core.classes.container import ContainerInput
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.layout import Layout
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.interfaces.seedable import Seedable


class GeneratorAudioNoise(ContainerInput, Seedable):
    """Generate a pure noise audio signal.

    Attributes
    ----------
    layout : cutcutcodec.core.classes.layout.Layout
        The signification of each channels (readonly).

    Examples
    --------
    >>> from fractions import Fraction
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> (stream,) = GeneratorAudioNoise(0).out_streams
    >>> stream.snapshot(Fraction(2, 48000), 48000, 5).numpy(force=True)
    array([[-0.25397146, -0.1199106 , -0.12052107, -0.16986334, -0.50950706],
           [ 0.17409873,  0.42185044, -0.7231959 ,  0.39764726, -0.25968206]],
          dtype=float32)
    >>> stream.snapshot(0, 24000, 5).numpy(force=True)
    array([[ 0.44649088, -0.25397146, -0.12052107, -0.50950706,  0.5112531 ],
           [-0.8036704 ,  0.17409873, -0.7231959 , -0.25968206, -0.7944578 ]],
          dtype=float32)
    >>> frame = stream.snapshot(0, 48000, 48000*60)  # test uniform
    >>> abs(round(frame.mean().item(), 3))  # theory 0
    0.0
    >>> round(frame.var().item(), 3)  # theory 1/3
    0.333
    >>>
    """

    def __init__(
        self,
        seed: typing.Optional[numbers.Real] = None,
        layout: typing.Optional[Layout | str | numbers.Integral] = "stereo",
    ):
        """Initialise and create the class.

        Parameters
        ----------
        seed : numbers.Real, optional
            Transmitted to ``cutcutcodec.core.interfaces.seedable.Seedable``.
        layout: cutcutcodec.core.classes.layout.Layout or str or int, optional
            The audio layout to associate to each equation,
            let see ``cutcutcodec.core.classes.layout.Layout`` for more details.
            By default, the layout is stereo, two channels.
        """
        assert layout is None or isinstance(layout, (Layout, str, numbers.Integral)), \
            layout.__class__.__name__
        Seedable.__init__(self, seed)
        super().__init__([_StreamAudioNoiseUniform(self)])
        self._layout = Layout(layout)

    def _getstate(self) -> dict:
        return {**self._getstate_seed(), "layout": self._layout.name}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"seed", "layout"}, set(state)
        self._setstate_seed(state)
        self._layout = Layout(state["layout"])
        ContainerInput.__init__(self, [_StreamAudioNoiseUniform(self)])

    @property
    def layout(self) -> Layout:
        """Return the signification of each channels."""
        return self._layout


class _StreamAudioNoiseUniform(StreamAudio):
    """Random audio stream where each sample follows a uniform law.

    Based on the md5 hash algorithm on the timestamps.
    """

    def __init__(self, node: GeneratorAudioNoise):
        assert isinstance(node, GeneratorAudioNoise), node.__class__.__name__
        super().__init__(node)
        self._seed = np.frombuffer(self.node.seed_bytes, dtype=np.uint32).reshape(8, 1)

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no audio frame at timestamp {timestamp} (need >= 0)")

        # initialisation message, depend to the seed and the timestamps
        string = np.empty((16, samples), dtype=np.uint32)  # ti = t0 + i/rate
        num = timestamp.numerator*rate + np.arange(samples, dtype=np.uint64)*timestamp.denominator
        gcds = np.gcd(num, timestamp.denominator*rate)
        num //= gcds
        den = rate*timestamp.denominator // gcds
        string[0, :] = num >> 32
        string[1, :] = num  # & 0x00000000ffffffff is implicite
        string[2, :] = den >> 32
        string[3, :] = den  # & 0x00000000ffffffff is implicite
        string[4:8, :] = 0  # because unitializated
        string[8:16, :] = self._seed

        # compute hash pseudo md5
        hashes = []
        while True:
            hashes.extend(md5(string))  # +4 items
            if len(hashes) >= len(self.node.layout):
                break
            string[5, :] = hashes[-1]

        # conversion uint32 to float32 uniform [0, 1]
        n_channels = len(self.node.layout)
        for i in range(n_channels):
            sign = hashes[i] & 0b1_00000000_00000000000000000000000
            hashes[i] &= 0b0_00000000_11111111111111111111111  # exponant reset and sign > 0
            hashes[i] ^= 0b0_01111111_00000000000000000000000  # exponant set for 2**0, range [1, 2]
            hashes[i] = hashes[i].view(np.float32)  # reinterpret cast for substraction operation
            hashes[i] -= 1.0  # range [0, 1]
            hashes[i] = hashes[i].view(np.uint32)  # reinterpret cast for bit operation
            hashes[i] |= sign  # add random sign, range [-1, 1]
            hashes[i] = hashes[i].view(np.float32)  # reinterpret cast for final dtype
        return FrameAudio(
            timestamp,
            rate,
            self.node.layout,
            np.vstack(hashes[:n_channels])
        )

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> Fraction | float:
        return math.inf

    @property
    def layout(self) -> Layout:
        """Return the signification of each channels."""
        return self.node.layout


def md5(string: np.ndarray) -> np.ndarray:
    """Vectorised version of the md5 algorithm.

    Parameters
    ----------
    string : np.ndarray
        The values to hash, of shape (16, n) and dtype uint32.

    Returns
    -------
    hash : tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        The hashed value of the input string, of shape (n,).
        Fours differents 32 bits values ares yields, total 128 bits.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.generation.audio.noise import md5
    >>> string = np.zeros((16, 1), dtype=np.uint32)
    >>> np.vstack(md5(string))
    array([[1543640769],
           [2049272632],
           [1899532917],
           [2915357108]], dtype=uint32)
    >>>
    """
    # verifs
    assert isinstance(string, np.ndarray), string.__class__.__name__
    assert string.dtype == np.uint32, string.dtype
    assert string.ndim == 2, string.shape
    assert string.shape[0] == 16, string.shape

    # initialisation
    _a = np.full((string.shape[1],), 0x67452301, dtype=np.uint32)
    _b = np.full((string.shape[1],), 0xefcdab89, dtype=np.uint32)
    _c = np.full((string.shape[1],), 0x98badcfe, dtype=np.uint32)
    _d = np.full((string.shape[1],), 0x10325476, dtype=np.uint32)
    _f = np.empty(string.shape[1], dtype=np.uint32)

    # compute md5 on each elements
    for i, (const, shift) in enumerate(zip(
        [
            0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
            0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
            0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
            0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
            0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
            0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
            0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
            0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
            0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
            0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
            0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
            0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
            0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
            0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
            0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
            0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
        ],
        [
            7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
            5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
            4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
            6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,
        ],
    )):
        if i <= 15:
            _f = (_b & _c) | ((~_b) & _d)
            index = i
        elif i <= 31:
            _f = (_d & _b) | ((~_d) & _c)
            index = (5*i + 1) % 16
        elif i <= 47:
            _f = _b ^ _c ^ _d
            index = (3*i + 5) % 16
        else:
            _f = _c ^ (_b | (~_d))
            index = (7*i) % 16
        _f += const + _a + string[index]
        _f = ((_f << shift) | (_f >> (32-shift)))
        _a, _b, _c, _d = _d, _f, _b, _c
    return _a, _b, _c, _d
