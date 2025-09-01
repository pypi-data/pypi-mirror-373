#!/usr/bin/env python3

"""The multimedia formats."""

import subprocess

import av

from cutcutcodec.core.opti.cache.singleton import MetaSingleton


class AllMuxers(metaclass=MetaSingleton):
    """Equivalent to parse ``ffmpeg -muxers`` but use av insted.

    Some muxers are remove if they are strange or not allow writting.

    Attributes
    ----------
    set : frozenset[str]
        All the available muxers (readonly).
    """

    def __init__(self):
        self._muxers = av.format.formats_available
        self._muxers -= {
            "alsa",
            "audiotoolbox",
            "chromaprint",
            "dash",
            "dshow",
            "fbdev",
            "ffmetadata",
            "fifo_test",
            "hds",  # it creates a folder, not a file
            "hls",  # it creates a folder, not a file
            "image2",  # it creates a None file
            "opengl",
            "pulse",
            "sdl",  # stream in live windows
            "sdl,sdl2",  # alias to sdl
            "sdl2",  # alias to sdl
            "smoothstreaming",
            "xv",
            # "caca",
            # "decklink",
            # "image2pipe",
            # "null",
            # "oss",
            # "roq",
            # "rtp",
        }
        for muxer in self._muxers.copy():
            try:
                av.format.ContainerFormat(muxer, "w")
            except ValueError:
                self._muxers.remove(muxer)
        self._muxers = frozenset(self._muxers)

    def from_suffix(self, suffix: str) -> list[str]:
        """Find the muxers from the file suffix.

        Parameters
        ----------
        suffix : str
            The filename extension, including the ".".

        Returns
        -------
        muxers : list[str]
            The sorted available muxer names,
            from the most pertinant (index 0) to the less pertinant.

        Raises
        ------
        KeyError
            If the extension is not associate to any muxer.

        Examples
        --------
        >>> from cutcutcodec.core.classes.muxer import AllMuxers
        >>> AllMuxers().from_suffix(".mkv")
        ['matroska']
        >>>
        """
        assert isinstance(suffix, str), suffix.__class__.__name__
        assert suffix.startswith("."), suffix
        suffix = suffix.lower()[1:]

        # get all avalaible extensions
        all_suffix = {}
        for muxer in self._muxers:
            for suf in av.format.ContainerFormat(muxer, "w").extensions:
                all_suffix[suf] = all_suffix.get(suf, set())
                all_suffix[suf].add(muxer)

        # simple case
        if suffix not in all_suffix:
            raise KeyError(f"{suffix} not in {sorted(all_suffix)}")
        muxers = all_suffix[suffix]
        if len(muxers) == 1:
            return list(muxers)

        criteria = []

        # 1 choice, if one of the muxer supports only this extension
        criteria.append(lambda muxer: av.format.ContainerFormat(muxer).extensions == {suffix})

        # 2 choice, alphabetic order.
        criteria.append(lambda muxer: muxer)

        # sorted with the criteria
        cost = {m: tuple(c(m) for c in criteria) for m in muxers}
        return sorted(muxers, key=lambda muxer: cost[muxer])

    @property
    def set(self) -> frozenset[str]:
        """Return the set of all the available muxer."""
        return self._muxers


class Muxer(av.format.ContainerFormat):
    """A specific muxer.

    Attributes
    ----------
    doc : str
        The documentation of the muxer (readonly).
    extensions : frozenset[str]
        All the available extensions for this muxer (readonly).
    """

    def __new__(cls, name: str):
        """Initialise and create the class.

        Parameters
        ----------
        name : str
            The canonical name or the extension with the suffix ".".
        """
        assert isinstance(name, str), name.__class__.__name__
        name = name.lower()
        if name.startswith("."):
            try:
                name = AllMuxers().from_suffix(name).pop(0)
            except KeyError as err:
                raise ValueError(f"failed to init muxer with extension {name}") from err
        if name not in AllMuxers().set:
            raise ValueError(f"muxer {name} not in {sorted(AllMuxers().set)}")
        muxer = super().__new__(cls, name, "w")
        return muxer

    @property
    def doc(self) -> str:
        """Return the documentation of the muxer.

        Based on ffmpeg, it parse ``ffmpeg -h muxer=...``.

        Examples
        --------
        >>> from cutcutcodec.core.classes.muxer import Muxer
        >>> print(Muxer("null").doc)
        Muxer null [raw null video]:
            Default video codec: wrapped_avframe.
            Default audio codec: pcm_s16le.
        <BLANKLINE>
        >>>
        """
        doc = subprocess.run(
            ["ffmpeg", "-v", "error", "-h", f"muxer={self.name}"],
            capture_output=True, check=True,
        ).stdout.decode()
        return doc

    @property
    def extensions(self) -> frozenset[str]:
        """All the available extensions for this muxer.

        Examples
        --------
        >>> from cutcutcodec.core.classes.muxer import Muxer
        >>> sorted(Muxer("matroska").extensions)
        ['.mkv']
        >>> sorted(Muxer("mpeg").extensions)
        ['.mpeg', '.mpg']
        >>>
        """
        return frozenset(f".{e}" for e in super().extensions)
