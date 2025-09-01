#!/usr/bin/env python3

"""Generate a video noise signal."""

from fractions import Fraction
import hashlib
import math
import numbers
import struct
import typing

import numpy as np
import torch

from cutcutcodec.core.classes.colorspace import Colorspace
from cutcutcodec.core.classes.container import ContainerInput
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.classes.stream_video import StreamVideo
from cutcutcodec.core.exceptions import OutOfTimeRange
from cutcutcodec.core.interfaces.seedable import Seedable


class GeneratorVideoNoise(ContainerInput, Seedable):
    """Generate a pure noise video signal.

    Examples
    --------
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>> stream = GeneratorVideoNoise(0).out_streams[0]
    >>> stream.snapshot(0, (13, 9))[..., 0]
    tensor([[0.4976, 0.1507, 0.7209, 0.9210, 0.4234, 0.6914, 0.5738, 0.7943, 0.2666],
            [0.8495, 0.8949, 0.1428, 0.2344, 0.7305, 0.2934, 0.7902, 0.7953, 0.7240],
            [0.8922, 0.5601, 0.3209, 0.7038, 0.6147, 0.6749, 0.5931, 0.4498, 0.8169],
            [0.8651, 0.8585, 0.6637, 0.7421, 0.7787, 0.8397, 0.5273, 0.1200, 0.0898],
            [0.6951, 0.8386, 0.0467, 0.0464, 0.3364, 0.7802, 0.2447, 0.4340, 0.5589],
            [0.6606, 0.0946, 0.4455, 0.7455, 0.3952, 0.1906, 0.1819, 0.0491, 0.0420],
            [0.8508, 0.9034, 0.9956, 0.1559, 0.8482, 0.7545, 0.7674, 0.2627, 0.4990],
            [0.6151, 0.8380, 0.2572, 0.2566, 0.2822, 0.6001, 0.2548, 0.5048, 0.5755],
            [0.0945, 0.3594, 0.7347, 0.7935, 0.6703, 0.7138, 0.1562, 0.2473, 0.9415],
            [0.9597, 0.8605, 0.6243, 0.6964, 0.2863, 0.2299, 0.9015, 0.5524, 0.5453],
            [0.7710, 0.3945, 0.5054, 0.7245, 0.1786, 0.1364, 0.3120, 0.0159, 0.6122],
            [0.6102, 0.5685, 0.2871, 0.2369, 0.5085, 0.9186, 0.3615, 0.7656, 0.0692],
            [0.0971, 0.0807, 0.6121, 0.7933, 0.5584, 0.4088, 0.8809, 0.1755, 0.2246]])
    >>>
    """

    def __init__(self, seed: typing.Optional[numbers.Real] = None):
        """Initialise and create the class.

        Parameters
        ----------
        seed : numbers.Real, optional
            Transmitted to :py:class:`cutcutcodec.core.interfaces.seedable.Seedable`.
        """
        Seedable.__init__(self, seed)
        super().__init__([_StreamVideoNoiseUniform(self)])

    def _getstate(self) -> dict:
        return self._getstate_seed()

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state.keys() == {"seed"}, set(state)
        self._setstate_seed(state)
        ContainerInput.__init__(self, [_StreamVideoNoiseUniform(self)])


class _StreamVideoNoiseUniform(StreamVideo):
    """Random video stream where each pixel follows a uniform law."""

    colorspace = Colorspace.from_default_working()

    def __init__(self, node: GeneratorVideoNoise):
        assert isinstance(node, GeneratorVideoNoise), node.__class__.__name__
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, mask: torch.Tensor) -> torch.Tensor:
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no audio frame at timestamp {timestamp} (need >= 0)")
        seed = int.from_bytes(
            hashlib.md5(
                struct.pack(
                    "dLL",
                    self.node.seed,
                    timestamp.numerator % (1 << 64),
                    timestamp.denominator % (1 << 64),
                )
            ).digest(),
            byteorder="big",
        ) % (1 << 64)  # solve RuntimeError: Overflow when unpacking long
        return torch.from_numpy(
            np.random.Generator(np.random.SFC64(seed=seed))  # np.random.default_rng(seed=seed)
            .random((*mask.shape, 3), dtype=np.float32)
        )
        # numpy 1.24.1 vs torch 2.0.0 is 11 times faster
        # this version is faster:
        # return torch.from_numpy(
        #     np.random.Generator(np.random.SFC64(seed=seed))  # np.random.default_rng(seed=seed)
        #     .integers(0, 256, (*mask.shape, 3), dtype=np.uint8)
        # )

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> Fraction | float:
        return math.inf
