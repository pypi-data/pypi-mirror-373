#!/usr/bin/env python3

"""The significance of the audio and video frame channels."""

import numbers
import re
import subprocess

from cutcutcodec.core.opti.cache.singleton import MetaSingleton


class AllLayouts(metaclass=MetaSingleton):
    """Parse the ``ffmpeg -layouts`` command line.

    Attributes
    ----------
    individuals : dict[str, str]
        To each channel canonical name in lower case, associate the description (readonly).
    layouts : dict[str, tuple[str, ...]]
        To each layouts name, associate the names of the channels (readonly).
    """

    def __init__(self):
        doc = "\n" + subprocess.run(
            ("ffmpeg", "-v", "error", "-layouts"), capture_output=True, check=True
        ).stdout.decode()

        if (match := re.search(r"\n.+:\s+NAME[ \t]+DESCRIPTION", doc)) is None:
            raise RuntimeError(f"impossible to find invidual channels description in {doc}")
        ind = match.span()
        if (match := re.search(r"\n.+:\s+NAME[ \t]+DECOMPOSITION", doc)) is None:
            raise RuntimeError(f"impossible to find standard channel layouts description in {doc}")
        lay = match.span()
        ind, lay = (
            (ind[1], lay[0] if lay[0] > ind[1] else len(doc)),
            (lay[1], ind[0] if ind[0] > lay[1] else len(doc)),
        )
        ind, lay = doc[ind[0]:ind[1]], doc[lay[0]:lay[1]]
        self._individuals = {
            m["name"].lower(): m["desc"]
            for m in re.finditer(r"(?P<name>[a-zA-Z0-9]+)[ \t]+(?P<desc>.+)", ind)
        }
        self._layouts = {
            m["name"].lower(): tuple(c.lower() for c in m["channels"].split("+"))
            for m in re.finditer(r"(?P<name>[\w\.\-\(\)]+)[ \t]+(?P<channels>[a-zA-Z0-9\+]+)", lay)
        }

    @property
    def individuals(self) -> dict[str, str]:
        """To each channel canonical name in lower case, associate the description.

        Examples
        --------
        >>> from pprint import pprint
        >>> from cutcutcodec.core.classes.layout import AllLayouts
        >>> pprint(AllLayouts().individuals)  # doctest: +ELLIPSIS
        {'bc': 'back center',
         ...
         'wl': 'wide left',
         'wr': 'wide right'}
        >>>
        """
        return self._individuals.copy()

    @property
    def layouts(self) -> dict[str, list[str]]:
        """To each layouts name, associate the names of the channels.

        Examples
        --------
        >>> from pprint import pprint
        >>> from cutcutcodec.core.classes.layout import AllLayouts
        >>> pprint(AllLayouts().layouts)  # doctest: +ELLIPSIS
        {'2.1': ('fl', 'fr', 'lfe'),
         ...
         'stereo': ('fl', 'fr')}
        >>>
        """
        return self._layouts.copy()


class Layout:
    """An audio profile.

    Attributes
    ----------
    channels : tuple[tuple[str, str], ...]
        Each audio channel (readonly) as an ordered dict with:
        The canonical name of the audio channel and a human description of the audio channel.
    name : str
        The canonical name of the audio profile (readonly).
    """

    def __init__(self, name: str | numbers.Integral):
        """Initialise and create the class.

        Parameters
        ----------
        name : str or numbers.Integral
            The canonical name of the audio profile.
            If an integer is provide, a default profile is assigned.
        """
        if isinstance(name, numbers.Integral):
            if (
                name_ := {
                    1: "mono",
                    2: "stereo",
                    3: "2.1",
                    4: "quad",
                    5: "4.1",
                    6: "5.1",
                    7: "6.1",
                    8: "7.1",
                    10: "5.1.4",
                    12: "7.1.4",
                    16: "hexadecagonal",
                    24: "22.2",
                }.get(name, None)
            ) is None:
                raise ValueError(
                    f"only 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16, or 24 audio channels, not {name}"
                )
            name = name_
        assert isinstance(name, str), name.__class__.__name__
        audio_profile = AllLayouts()
        name = {"1 channel": "mono", "2 channels": "stereo"}.get(name, name)  # debug .wav files
        if (channels := audio_profile.layouts.get(name, None)) is None:
            raise ValueError(
                f"profile audio {name} not in {sorted(AllLayouts().layouts)}"
            )
        self._name = str(name)
        self._channels = tuple((c, audio_profile.individuals[c]) for c in channels)

    def __hash__(self):
        """Make this object able to be used in set or as dict key."""
        return hash(self._name)

    def __eq__(self, other) -> bool:
        """Make this object able to be used in set or as dict key."""
        if not isinstance(other, Layout):
            return False
        return other.name == self._name

    def __len__(self) -> int:
        """Return the numbers of channels."""
        return len(self._channels)

    def __repr__(self) -> str:
        """Give a nice representation of the layout."""
        return f"{self.__class__.__name__}({repr(self._name)})"

    @property
    def channels(self) -> tuple[tuple[str, str], ...]:
        """Return the description of each channels.

        Examples
        --------
        >>> from pprint import pprint
        >>> from cutcutcodec.core.classes.layout import Layout
        >>> Layout("stereo").channels
        (('fl', 'front left'), ('fr', 'front right'))
        >>> pprint(Layout("5.1").channels)
        (('fl', 'front left'),
         ('fr', 'front right'),
         ('fc', 'front center'),
         ('lfe', 'low frequency'),
         ('bl', 'back left'),
         ('br', 'back right'))
        >>>
        """
        return self._channels

    @property
    def name(self) -> str:
        """Return the canonical name of the audio profile.

        Examples
        --------
        >>> from cutcutcodec.core.classes.layout import Layout
        >>> Layout(2).name
        'stereo'
        >>>
        """
        return self._name
