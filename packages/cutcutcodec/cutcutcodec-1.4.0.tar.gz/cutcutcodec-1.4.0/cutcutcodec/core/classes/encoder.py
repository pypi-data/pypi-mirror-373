#!/usr/bin/env python3

"""The codecs and encoders."""

import subprocess

import av

from cutcutcodec.core.opti.cache.singleton import MetaSingleton


class AllEncoders(metaclass=MetaSingleton):
    """Equivalent to parse ``ffmpeg -codecs`` and ``ffmpeg -encoders`` but use av insted.

    Parameters
    ----------
    audio : frozenset[str]
        All the referenced audio encoders (readonly).
    set : frozenset[str]
        All the referenced encoders (readonly).
    subtitle : frozenset[str]
        All the referenced subtitle encoders (readonly).
    video : frozenset[str]
        All the referenced video encoders (readonly).
    """

    def __init__(self):
        self._encoders = set()
        for encodec in av.codec.codecs_available:
            if encodec in {
                "anull",  # empty audio
                "libjxl",  # create segfault
                "msrle",  # old on microsoft windows only, segfault on linux
                "rle",  # alias to 'msrle'
                "smc",  # old on microsoft windows only, segfault on linux
                "vnull",  # empty video
            }:
                continue
            try:
                encoder = av.codec.Codec(encodec, "w").name
            except av.codec.codec.UnknownCodecError:
                continue
            self._encoders.add(encoder)

    def _select(self, encoder_type: str) -> frozenset[str]:
        """Select the encoders of a specific type.

        Parameters
        ----------
        encoder_type : str
            The codec type ``audio``, ``video`` or ``subtitle``.

        Returns
        -------
        encoders : frozenset[str]
            All the encoders of the provide type.
        """
        assert isinstance(encoder_type, str), encoder_type.__class__.__name__
        assert encoder_type in {"audio", "video", "subtitle"}, encoder_type
        return frozenset(e for e in self._encoders if av.codec.Codec(e, "w").type == encoder_type)

    @property
    def audio(self) -> frozenset[str]:
        """All the referenced audio encoders.

        Examples
        --------
        >>> from cutcutcodec.core.classes.encoder import AllEncoders
        >>> sorted(AllEncoders().audio)  # doctest: +ELLIPSIS
        ['aac', 'ac3', ..., 'wmav1', 'wmav2']
        >>>
        """
        return self._select("audio")

    @property
    def set(self) -> frozenset[str]:
        """All the referenced encoders."""
        return self._encoders

    @property
    def subtitle(self) -> frozenset[str]:
        """All the referenced subtitle encoders.

        Examples
        --------
        >>> from cutcutcodec.core.classes.encoder import AllEncoders
        >>> sorted(AllEncoders().subtitle)  # doctest: +ELLIPSIS
        ['ass', 'dvbsub', ..., 'webvtt', 'xsub']
        >>>
        """
        return self._select("subtitle")

    @property
    def video(self) -> frozenset[str]:
        """All the referenced video encoders.

        Examples
        --------
        >>> from cutcutcodec.core.classes.encoder import AllEncoders
        >>> sorted(AllEncoders().video)  # doctest: +ELLIPSIS
        ['a64multi', 'a64multi5', ..., 'zlib', 'zmbv']
        >>>
        """
        return self._select("video")


class Encoder(av.codec.Codec):
    """A specific encoder.

    Attributes
    ----------
    doc : str
        The documentation of the encoder (readonly).
    """

    def __new__(cls, name: str):
        """Initialise and create the class.

        Parameters
        ----------
        name : str
            The name of the encoder.
        """
        assert isinstance(name, str), name.__class__.__name__
        assert name in AllEncoders().set, f"{name} encoder is not in {AllEncoders().set}"
        encoder = super().__new__(cls, name, "w")
        return encoder

    @property
    def doc(self) -> str:
        """Return the documentation of the encoder.

        Based on ffmpeg, it parse ``ffmpeg -h encoder=...``.

        Examples
        --------
        >>> from cutcutcodec.core.classes.encoder import Encoder
        >>> print(Encoder("libopus").doc)  # doctest: +ELLIPSIS
        Encoder libopus [libopus Opus]:
            General capabilities: ...
            Threading capabilities: none
            Supported sample rates: 48000 24000 16000 12000 8000
            Supported sample formats: s16 flt
        libopus AVOptions:
          ...
        >>>
        """
        doc = subprocess.run(
            ["ffmpeg", "-v", "error", "-h", f"encoder={self.name}"],
            capture_output=True, check=True,
        ).stdout.decode().strip()
        return doc
