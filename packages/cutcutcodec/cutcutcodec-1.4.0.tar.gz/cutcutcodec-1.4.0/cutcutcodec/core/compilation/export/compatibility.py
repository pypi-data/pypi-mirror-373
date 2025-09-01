#!/usr/bin/env python3

"""Allow to choose a format and codecs.

The information collected here concerns the encoding and not the decoding.
"""

from fractions import Fraction
import contextlib
import io
import itertools
import multiprocessing
import os
import tempfile
import typing

import av
import numpy as np
import tqdm

from cutcutcodec.core.classes.encoder import AllEncoders, Encoder
from cutcutcodec.core.classes.muxer import AllMuxers
from cutcutcodec.core.exceptions import DecodeError, EncodeError, IncompatibleSettings
from cutcutcodec.core.opti.cache.singleton import MetaSingleton


def _decode(file: str | io.BytesIO, muxer: typing.Optional[str] = None) -> dict[str]:
    """Read and extracts the informations of the stream 0.

    Extract only the mains informations. It uses pyav in background.
    Decode the informations of the first stream only.

    Parameters
    ----------
    file : str
        The full path a the file to read or the io.BytesIO filelike, already seek to 0.
    muxer : str, optional
        The muxer name used for encode.

    Returns
    -------
    properties : dict[str, str]
        * `codec`: str  # The name of the codec found.
        * `layout`: str or None  # The audio channel organisation.
        * `muxer`: str  # The decoded muxer name.
        * `profile`: str  # The name of the binary format of the data.
        * `rate`: int or Fraction  # The framerate or the samplerate.
        * `shape`: tuple[int, int] or None  # The shape of the frames.
        * `type`: str  # The type of stream.

    Raises
    ------
    DecodeError
        If reading failed.

    Notes
    -----
    No verifications are performed because it is a subfunction.
    """
    properties = {}
    try:
        with av.open(file, mode="r", format=muxer) as container:
            stream = container.streams[0]
            properties["codec"] = stream.codec_context.codec.name
            properties["layout"] = None
            properties["muxer"] = container.format.name
            properties["profile"] = stream.codec_context.format.name
            properties["rate"] = None
            properties["shape"] = None
            properties["type"] = stream.type
            if properties["type"] == "audio":
                properties["layout"] = stream.codec_context.layout.name
                properties["rate"] = stream.rate
            elif properties["type"] == "video":
                properties["rate"] = stream.average_rate
                properties["shape"] = (stream.height, stream.width)
            list(container.decode(stream))  # try to decode
    except (
        av.error.FFmpegError,
        IndexError,
        AttributeError,
        UnicodeDecodeError,  # for the ascii codec
    ) as err:
        raise DecodeError(f"failed to decode {file}") from err
    return properties


def _encode_audio(
    file: str | io.BytesIO,
    encodec: str,
    muxer: str,
    **kwargs,
) -> None:
    """Test the encoder capability with the null muxer in a virtual file.

    Parameters
    ----------
    file : str
        The full path a the file to write or the io.BytesIO filelike.
    encodec : str
        The codec or the encoder name.
    muxer : str
        The format name.
    layout : str
        The name of the audio layout, ex "stereo"
    rate : int, optional
        The samplerate of the audio in all channels.
    profile : str, optional
        The name of the binary format of the data ex "flt".

    Raises
    ------
    EncodeError
        If reading failed.

    Notes
    -----
    No verifications are performed because it is a subfunction.
    """
    layout, rate, profile = kwargs["layout"], kwargs.get("rate", None), kwargs.get("profile", None)
    os.environ["PYAV_LOGGING"] = "off"
    try:
        with av.open(file, mode="w", format=muxer) as container:
            stream = container.add_stream(encodec, rate=rate, layout=layout)
            stream.options = {"strict": "experimental"}
            if profile is not None:
                stream.format = profile
            format_to_use = (
                stream.format.name
                if stream.format.name in av.audio.frame.format_dtypes
                else "flt"
            )
            frame = av.audio.frame.AudioFrame.from_ndarray(
                np.zeros(  # zeros encoding time faster than empty
                    (len(av.audio.layout.AudioLayout(layout).channels), 4800),
                    dtype=av.audio.frame.format_dtypes[format_to_use],
                ),
                format=format_to_use,
                layout=layout,
            )  # raise IndexError for 7.1 layout, error in pyav
            frame.rate = rate or min(av.Codec(encodec, "w").audio_rates or {48000})
            frame.time_base = Fraction(1, frame.rate)
            frame.pts = 0
            container.mux(stream.encode(frame))
            container.mux(stream.encode(None))  # flush buffer
    except (av.error.FFmpegError, ValueError, AttributeError) as err:
        raise EncodeError(f"failed to encode {file}") from err


def _encode_video(
    file: str | io.BytesIO,
    encodec: str,
    muxer: str,
    **kwargs,
) -> None:
    """Test the encoder capability with the null muxer in a virtual file.

    Parameters
    ----------
    file : str
        The full path a the file to write or the io.BytesIO filelike.
    encodec : str
        The codec or the encoder name.
    muxer : str
        The format name.
    shape : tuple[int, int]
        The shape of the frames of the encoded video.
    rate : Fraction, optional
        The frame rate.
    pix_fmt : str, optional
        The name of the pixel format used.

    Raises
    ------
    EncodeError
        If reading failed.

    Notes
    -----
    No verifications are performed because it is a subfunction.
    """
    shape, rate, pix_fmt = kwargs["shape"], kwargs.get("rate", None), kwargs.get("pix_fmt", None)
    os.environ["PYAV_LOGGING"] = "off"
    try:
        with av.open(file, mode="w", format=muxer) as container:
            stream = container.add_stream(encodec, rate=rate, height=shape[0], width=shape[1])
            stream.options = {
                "strict": "experimental",  # to allow new codecs
                "x265-params": "log_level=none",  # to make libx265 quiet
            }
            if encodec == "libsvtav1":
                os.environ["SVT_LOG"] = "1"  # to make libsvtav1 quiet
            stream.pix_fmt = (
                pix_fmt or max(
                    (av.Codec(encodec, "w").video_formats or (av.VideoFormat("yuv420p"),)),
                    key=lambda f: f.bits_per_pixel
                ).name
            )
            for i in range(3):  # nbr frames
                frame = av.video.frame.VideoFrame.from_ndarray(
                    np.zeros((*shape, 3), dtype=np.uint8), format="rgb24"
                )
                frame.time_base = Fraction(1, 300300)  # ppcm 1001, 1000, 25, 30, 60
                frame.pts = round(
                    (i / (rate or stream.average_rate or Fraction(30000, 1001)))
                    / frame.time_base
                )
                container.mux(stream.encode(frame))
            container.mux(stream.encode(None))  # flush buffer
    except (av.error.FFmpegError, ValueError, AttributeError) as err:
        raise EncodeError(f"failed to encode {file}") from err


def audio_encodec_compatibility(
    encodec: str,
    muxer: str,
    layout: str = "mono",
    rate: typing.Optional[int] = None,
    profile: typing.Optional[str] = None,
) -> str:
    """Test throw av the compatibility of the encoding audio parameters.

    Parameters
    ----------
    encodec : str
        The codec or the encoder name.
    muxer : str
        The format name.
    layout : str, default="mono"
        The name of the audio layout, ex "stereo"
    rate : int, optional
        The samplerate of the audio in all channels.
    profile : str, optional
        The name of the binary format of the data ex "flt".

    Returns
    -------
    codec : str
        The name of the codec found.

    Raises
    ------
    IncompatibleSettings
        If it fails to encode or if the decoded parameters don't matched.

    Examples
    --------
    >>> from cutcutcodec.core.compilation.export.compatibility import audio_encodec_compatibility
    >>> audio_encodec_compatibility("libvorbis", "ogg")
    'vorbis'
    >>>
    """
    assert isinstance(muxer, str), muxer.__class__.__name__
    assert isinstance(encodec, str), encodec.__class__.__name__
    assert isinstance(layout, str), layout.__class__.__name__
    assert rate is None or isinstance(rate, int), rate.__class__.__name__
    assert profile is None or isinstance(profile, str), profile.__class__.__name__

    # theorical verifications
    codec_av = av.Codec(encodec, "w")
    if codec_av.type != "audio":
        raise IncompatibleSettings(f"the codec {encodec} is {codec_av.type}, not audio")
    if (
        rate is not None and codec_av.audio_rates is not None
        and rate not in codec_av.audio_rates
    ):
        raise IncompatibleSettings(
            f"the codec {encodec} dose not support {rate} Hz, only {codec_av.audio_rates}"
        )
    if (
        profile is not None and codec_av.audio_formats is not None
        and profile not in {p.name for p in codec_av.audio_formats}
    ):
        raise IncompatibleSettings(f"the codec {encodec} dose not support {profile} profile")

    # prepare context
    properties = {}

    try:
        with io.BytesIO() as file:
            file.name = os.devnull
            _encode_audio(file, encodec, muxer, layout=layout, rate=rate, profile=profile)
            file.seek(0)
            properties = _decode(file, muxer)
    except (EncodeError, DecodeError) as err:
        raise IncompatibleSettings("failed to encode or decode") from err
    for ref_name, ref_val in [
        ("type", "audio"),
        ("muxer", muxer),
        ("layout", layout),
        ("rate", rate),
        ("profile", profile),
    ]:
        if ref_val is not None and ref_val != properties[ref_name]:
            raise IncompatibleSettings(
                f"encoded {ref_name} {ref_val} but decoded with {properties[ref_name]}"
            )

    return properties["codec"]


def video_encodec_compatibility(
    encodec: str,
    muxer: str,
    shape: typing.Optional[tuple[int, int]] = None,
    rate: typing.Optional[Fraction] = None,
    pix_fmt: typing.Optional[str] = None,
) -> str:
    """Test throw av the compatibility of the encoding video parameters.

    Parameters
    ----------
    encodec : str
        The codec or the encoder name.
    muxer : str
        The format name.
    shape : tuple[int, int], optional
        The shape of the frames of the encoded video.
    rate : Fraction, optional
        The frame rate.
    pix_fmt : str, optional
        The name of the pixel format used.

    Returns
    -------
    codec : str
        The name of the codec found.

    Raises
    ------
    IncompatibleSettings
        If it fails to encode or if the decoded parameters don't matched.

    Examples
    --------
    >>> from cutcutcodec.core.compilation.export.compatibility import video_encodec_compatibility
    >>> video_encodec_compatibility("libx264", "mp4")
    'h264'
    >>>
    """
    assert isinstance(muxer, str), muxer.__class__.__name__
    assert isinstance(encodec, str), encodec.__class__.__name__
    shape = shape or (64, 64)
    assert isinstance(shape, tuple), shape.__class__.__name__
    assert len(shape) == 2, shape
    assert isinstance(shape[0], int), shape[0].__class__.__name__
    assert isinstance(shape[1], int), shape[1].__class__.__name__
    assert rate is None or isinstance(rate, Fraction), rate.__class__.__name__
    assert pix_fmt is None or isinstance(pix_fmt, str), pix_fmt.__class__.__name__

    # theorical verifications
    codec_av = av.Codec(encodec, "w")
    if codec_av.type != "video":
        raise IncompatibleSettings(f"the codec {encodec} is {codec_av.type}, not video")
    try:
        if (
            rate is not None and codec_av.frame_rates is not None
            and rate not in codec_av.frame_rates
        ):
            raise IncompatibleSettings(
                f"the codec {encodec} dose not support {rate} fps, only {codec_av.frame_rates}"
            )
    except AttributeError:  # failed sometimes in ``codec_av.frame_rates``
        pass
    if (
        pix_fmt is not None and codec_av.video_formats is not None
        and pix_fmt not in {f.name for f in codec_av.video_formats}
    ):
        raise IncompatibleSettings(f"the codec {encodec} dose not support {pix_fmt} pixel format")

    # prepare context
    properties = {}

    try:
        with tempfile.SpooledTemporaryFile(max_size=10_000_000, mode="rwb") as file:  # max 10Mo
            _encode_video(file, encodec, muxer, shape=shape, rate=rate, pix_fmt=pix_fmt)
            file.seek(0)
            properties = _decode(file, muxer)
    except (EncodeError, DecodeError) as err:
        raise IncompatibleSettings("failed to encode") from err
    for ref_name, ref_val in [
        ("type", "video"),
        ("muxer", muxer),
        ("profile", pix_fmt),
        ("rate", rate),
        ("shape", shape),
    ]:
        if ref_val is not None and ref_val != properties[ref_name]:
            raise IncompatibleSettings(
                f"encoded {ref_name} {ref_val} but decoded with {properties[ref_name]}"
            )

    return properties["codec"]


class Compatibilities(metaclass=MetaSingleton):
    """Link the muxers and the encoders."""

    def __init__(self):
        self._compatibilites = {}

    @staticmethod
    def _check_mono(enc_mux_spec: tuple[str, str, tuple[tuple[str, ...], tuple]]) -> str:
        """Test if the encodec is compatible with the given specifications.

        It is process and thread safe.
        """
        encoder, muxer, specifications = enc_mux_spec
        kwargs = dict(zip(*specifications))
        kind: str = Encoder(encoder).type
        if (checker := {
            "audio": audio_encodec_compatibility,
            "video": video_encodec_compatibility,
        }.get(kind, None)) is None:
            raise NotImplementedError(f"only available for audio and video, not for {kind}")
        with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):  # quiet
            try:
                codec = checker(encoder, muxer, **kwargs)
            except IncompatibleSettings:
                return ""
        return codec

    def check(self, encoders: list[str], muxers: list[str], **kwargs) -> np.ndarray[str]:
        """Check all the couples encoder/muxer (cartesian product).

        Parameters
        ----------
        encoders : list[str]
            The encoder names.
        muxers : list[str]
            The muxer (format) names.
        **kwargs : dict
            The optionals named parameters of
            ``cutcutcodec.core.compilation.export.compatibility.audio_encodec_compatibility``
            and ``cutcutcodec.core.compilation.export.compatibility.video_encodec_compatibility``.

        Returns
        -------
        compatibility_matrix : np.ndarray[str]
            The 2d boolean compatibility matrix.
            Item (i, j) contains the codec name of the encoder[i] with the muxer[j].

        Examples
        --------
        >>> from cutcutcodec.core.compilation.export.compatibility import Compatibilities
        >>> Compatibilities().check(["libx264", "libaom-av1", "libvorbis"], ["mp4", "ogg"])
        array([['h264', ''],
               ['libdav1d', ''],
               ['vorbis', 'vorbis']], dtype='<U8')
        >>> Compatibilities().check([], [])
        array([], shape=(1, 0), dtype='<U1')
        >>> Compatibilities().check(["libx264"], [])
        array([], shape=(1, 0), dtype='<U1')
        >>> Compatibilities().check([], ["mp4"])
        array([], shape=(1, 0), dtype='<U1')
        >>>
        """
        assert isinstance(encoders, list), encoders.__class__.__name__
        assert all(isinstance(ec, str) for ec in encoders), encoders
        assert set(encoders).issubset(AllEncoders().set), set(encoders)-AllEncoders().set
        assert isinstance(muxers, list), muxers.__class__.__name__
        assert all(isinstance(f, str) for f in muxers), muxers
        assert set(muxers).issubset(AllMuxers().set), set(muxers)-AllMuxers().set

        # case empty:
        if len(encoders) == 0 or len(muxers) == 0:
            return np.asarray([[]], dtype=str)  # oblige for keep 2d array homogeneous

        # makes checks
        signature = tuple(sorted(kwargs))
        signature = (signature, tuple(kwargs[k] for k in signature))
        if (all_enc_mux_spec := [  # iter over encoder first, muxer second (same aim as shuffle)
            (me[1], me[0], signature) for me in itertools.product(muxers, encoders)
            if (me[1], me[0], signature) not in self._compatibilites
        ]):  # reduce the number of tests to the minimum for optimisation
            # maxtasksperchild != None for memory leak and != 1 for fork efficiency (granularity)
            with multiprocessing.get_context("spawn").Pool(maxtasksperchild=128) as pool:
                for enc_mux_spec, is_compatible in tqdm.tqdm(
                    zip(
                        all_enc_mux_spec,
                        pool.imap(
                            Compatibilities._check_mono,
                            all_enc_mux_spec,
                            chunksize=16,
                        ),
                        # map(Compatibilities._check_mono, all_enc_mux_spec),  # for debug only
                    ),
                    total=len(all_enc_mux_spec),
                    desc="Testing encoder/muxer",
                    dynamic_ncols=True,
                    disable=(len(all_enc_mux_spec) <= 4*os.cpu_count()),
                    smoothing=0.1,
                    unit="comb",
                ):
                    self._compatibilites[enc_mux_spec] = is_compatible

        # create matrix
        return np.asarray(
            [
                [self._compatibilites[(encoder, muxer, signature)] for muxer in muxers]
                for encoder in encoders
            ],
            dtype=str,
        )

    def codecs_audio(
        self, muxers: typing.Optional[list[str]] = None, **kwargs
    ) -> dict[str, list[tuple[str, str]]]:
        """Search all the compatibles audio codecs.

        Parameters
        ----------
        muxers : list[str]
            The muxer (format) names.
        **kwargs : dict
            The optionals named parameters of
            ``cutcutcodec.core.compilation.export.compatibility.audio_encodec_compatibility``.

        Returns
        -------
        codecs : dict[str, list[tuple[str, str]]]
            For all audio codec, associate the encoder/muxer pairs.

        Examples
        --------
        >>> from pprint import pprint
        >>> from cutcutcodec.core.compilation.export.compatibility import Compatibilities
        >>> pprint(Compatibilities().codecs_audio(layout="5.1"))  # doctest: +ELLIPSIS
        {'aac': [('aac', '3g2'),
                 ('aac', '3gp'),
                 ('aac', 'adts'),
                 ...
                 ('aac', 'w64'),
                 ('aac', 'wav'),
                 ('aac', 'wtv')],
         ...
         'wavpack': [('wavpack', 'matroska'), ('wavpack', 'nut'), ('wavpack', 'wv')]}
        >>>
        """
        encoders = sorted(AllEncoders().audio)  # sorted, not list because dict is sorted
        if muxers is None:
            muxers = sorted(AllMuxers().set)  # sorted, not list because dict is sorted
        else:
            assert isinstance(muxers, list), muxers.__class__.__name__
            assert all(isinstance(m, str) for m in muxers), muxers
        comp = self.check(encoders, muxers, **kwargs)
        codecs = {}
        for encoder, decoded_codecs in zip(encoders, comp):
            for muxer, codec in zip(muxers, decoded_codecs):
                if codec_str := str(codec):
                    codecs[codec_str] = codecs.get(codec_str, [])
                    codecs[codec_str].append((encoder, muxer))
        return codecs

    def codecs_video(
        self, muxers: typing.Optional[list[str]] = None, **kwargs
    ) -> dict[str, list[tuple[str, str]]]:
        """Search all the compatibles video codecs.

        Parameters
        ----------
        muxers : list[str]
            The muxer (format) names.
        **kwargs : dict
            The optionals named parameters of
            ``cutcutcodec.core.compilation.export.compatibility.video_encodec_compatibility``.

        Returns
        -------
        codecs : dict[str, list[tuple[str, str]]]
            For all video codec, associate the encoder/muxer pairs.

        Examples
        --------
        >>> from fractions import Fraction
        >>> from pprint import pprint
        >>> from cutcutcodec.core.compilation.export.compatibility import Compatibilities
        >>> comp = Compatibilities().codecs_video(pix_fmt="yuv444p12le", rate=Fraction(120))
        >>> pprint(comp["hevc"])  # doctest: +ELLIPSIS
        [('libx265', 'flv'),
         ...
         ('libx265', 'vob')]
        >>>
        """
        encoders = sorted(AllEncoders().video)  # sorted, not list because dict is sorted
        if muxers is None:
            muxers = sorted(AllMuxers().set)  # sorted, not list because dict is sorted
        else:
            assert isinstance(muxers, list), muxers.__class__.__name__
            assert all(isinstance(m, str) for m in muxers), muxers
        comp = self.check(encoders, muxers, **kwargs)
        codecs = {}
        for encoder, decoded_codecs in zip(encoders, comp):
            for muxer, codec in zip(muxers, decoded_codecs):
                if codec_str := str(codec):
                    codecs[codec_str] = codecs.get(codec_str, [])
                    codecs[codec_str].append((encoder, muxer))
        return codecs

    def encoders_audio(
        self, codec: str, muxers: typing.Optional[list[str]] = None, **kwargs
    ) -> dict[str, set[str]]:
        """Search all the compatible audio encoders.

        Parameters
        ----------
        codec : str
            The audio codec name.
        muxers : list[str]
            The muxer (format) names.
        **kwargs : dict
            The optionals named parameters of
            ``cutcutcodec.core.compilation.export.compatibility.audio_encodec_compatibility``.

        Returns
        -------
        encoders : dict[str, set[str]]
            For all audio encoder, associate the available muxers.

        Examples
        --------
        >>> from pprint import pprint
        >>> from cutcutcodec.core.compilation.export.compatibility import Compatibilities
        >>> pprint(Compatibilities().encoders_audio("vorbis", layout="5.1"))  # doctest: +ELLIPSIS
        {'libvorbis': {'asf',
                       ...
                       'wtv'}}
        >>>
        """
        assert isinstance(codec, str), codec.__class__.__name__
        if muxers is None:
            muxers = sorted(AllMuxers().set)  # sorted, not list because dict is sorted
        else:
            assert isinstance(muxers, list), muxers.__class__.__name__
            assert all(isinstance(m, str) for m in muxers), muxers
        encoders = sorted(AllEncoders().audio)  # sorted, not list because dict is sorted
        comp = self.check(encoders, muxers, **kwargs)
        compatible_encoders = {}
        for encoder, decoded_codecs in zip(encoders, comp):
            for muxer, decoded_codec in zip(muxers, decoded_codecs):
                if decoded_codec == codec:
                    compatible_encoders[encoder] = compatible_encoders.get(encoder, set())
                    compatible_encoders[encoder].add(muxer)
        return compatible_encoders

    def encoders_video(
        self, codec: str, muxers: typing.Optional[list[str]] = None, **kwargs
    ) -> dict[str, set[str]]:
        """Search all the compatible video encoders.

        Parameters
        ----------
        codec : str
            The video codec name.
        muxers : list[str]
            The muxer (format) names.
        **kwargs : dict
            The optionals named parameters of
            ``cutcutcodec.core.compilation.export.compatibility.video_encodec_compatibility``.

        Returns
        -------
        encoders : dict[str, set[str]]
            For all video encoder, associate the available muxers.

        Examples
        --------
        >>> from pprint import pprint
        >>> from cutcutcodec.core.compilation.export.compatibility import Compatibilities
        >>> pprint(
        ...     Compatibilities().encoders_video("h264", pix_fmt="yuv420p")
        ... )  # doctest: +ELLIPSIS
        {'libopenh264': {'3g2',
                         '3gp',
                         ...
                         'vob',
                         'wtv'},
         'libx264': {'3g2',
                     '3gp',
                     ...
                     'vob',
                     'wtv'}}
        >>>
        """
        assert isinstance(codec, str), codec.__class__.__name__
        if muxers is None:
            muxers = sorted(AllMuxers().set)  # sorted, not list because dict is sorted
        else:
            assert isinstance(muxers, list), muxers.__class__.__name__
            assert all(isinstance(m, str) for m in muxers), muxers
        encoders = sorted(AllEncoders().video)  # sorted, not list because dict is sorted
        comp = self.check(encoders, muxers, **kwargs)
        compatible_encoders = {}
        for encoder, decoded_codecs in zip(encoders, comp):
            for muxer, decoded_codec in zip(muxers, decoded_codecs):
                if decoded_codec == codec:
                    compatible_encoders[encoder] = compatible_encoders.get(encoder, set())
                    compatible_encoders[encoder].add(muxer)
        return compatible_encoders

    def muxers(self, encoder: str, **kwargs) -> frozenset[str]:
        """Search all the compatibles muxers.

        Parameters
        ----------
        encoder : str
            The encoder name.
        **kwargs : dict
            The optionals named parameters of
            ``cutcutcodec.core.compilation.export.compatibility.Compatibilities.check``.

        Returns
        -------
        available_muxers : frozenset[str]
            All the available muxers for the given encoder.

        Examples
        --------
        >>> from pprint import pprint
        >>> from cutcutcodec.core.compilation.export.compatibility import Compatibilities
        >>> pprint(Compatibilities().muxers("libx264"))  # doctest: +ELLIPSIS
        frozenset({'3g2',
                   '3gp',
                   ...
                   'vob',
                   'wtv'})
        >>>
        """
        assert isinstance(encoder, str), encoder.__class__.__name__
        muxers = sorted(AllMuxers().set)  # sorted for repetability
        comp = self.check([encoder], muxers, **kwargs)
        available_muxers = frozenset(m for m, a in zip(muxers, comp[0]) if a)
        return available_muxers
