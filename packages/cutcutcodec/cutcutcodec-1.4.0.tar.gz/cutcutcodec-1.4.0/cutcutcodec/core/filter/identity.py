#!/usr/bin/env python3

"""An audio filter that doing nothing."""

import typing

from cutcutcodec.core.classes.filter import Filter
from cutcutcodec.core.classes.stream import Stream


class FilterIdentity(Filter):
    """Allow to convert a set of streams into a filter.

    Examples
    --------
    >>> from cutcutcodec.core.filter.identity import FilterIdentity
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_base_audio,) = GeneratorAudioNoise(0).out_streams
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> identity = FilterIdentity([s_base_audio, s_base_video])
    >>>
    >>> s_base_audio is identity.out_streams[0]
    True
    >>> s_base_video is identity.out_streams[1]
    True
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream]):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            All the streams to keep intact.
            Transmitted to ``cutcutcodec.core.classes.filter.Filter``.
        """
        super().__init__(in_streams, in_streams)

    def _getstate(self) -> dict:
        return {}

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterIdentity.__init__(self, in_streams)
