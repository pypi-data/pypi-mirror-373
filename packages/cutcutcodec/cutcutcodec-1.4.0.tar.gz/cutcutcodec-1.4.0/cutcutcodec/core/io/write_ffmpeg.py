#!/usr/bin/env python3

"""Management of the encoding of a multimedia stream based on PyAV."""

from fractions import Fraction
import copy
import math
import numbers
import pathlib
import typing

import av
import numpy as np
import tqdm

from cutcutcodec.core.classes.container import ContainerOutput
from cutcutcodec.core.classes.frame_audio import FrameAudio
from cutcutcodec.core.classes.frame_video import FrameVideo
from cutcutcodec.core.classes.stream import Stream
from cutcutcodec.core.colorspace.cst import FFMPEG_PRIMARIES_TO_COLORSPACE
from cutcutcodec.core.compilation.parse import parse_to_number
from cutcutcodec.core.io.scheduler import scheduler
from .framecaster import to_rgb, to_yuv


class ContainerOutputFFMPEG(ContainerOutput):
    """Allow to write the output file to disk.

    Attributes
    ----------
    filename : pathlib.Path
        The absolute path + name of the file to encode (readonly).
    streams_settings : list[dict]
        Information related to each codec (readonly).
    container_settings : dict
        Global container file information (readonly).

    Examples
    --------
    >>> import os
    >>> from cutcutcodec.core.filter.audio.subclip import FilterAudioSubclip
    >>> from cutcutcodec.core.filter.video.subclip import FilterVideoSubclip
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> from cutcutcodec.core.generation.video.noise import GeneratorVideoNoise
    >>> from cutcutcodec.core.io.write_ffmpeg import ContainerOutputFFMPEG
    >>> streams_settings = [
    ...     {"encodec": "libopus", "rate": 8000},
    ...     {"encodec": "libx264", "rate": 12, "shape": (2, 2)},
    ... ]
    >>> container_settings = {"format": "matroska"}
    >>> (stream_a,) = FilterAudioSubclip(GeneratorAudioNoise(0).out_streams, 0, 1).out_streams
    >>> (stream_v,) = FilterVideoSubclip(GeneratorVideoNoise(0).out_streams, 0, 1).out_streams
    >>> streams = (stream_a, stream_v)
    >>> ContainerOutputFFMPEG(streams, os.devnull, streams_settings, container_settings).write()
    >>>
    """

    def __init__(
        self,
        in_streams: typing.Iterable[Stream],
        filename: pathlib.Path | str | bytes,
        streams_settings: typing.Iterable[dict],
        container_settings: typing.Optional[dict] = None,
    ):
        """Initialise and create the class.

        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            The ordered video or audio streams to be encoded.
            For more information, please refer to initializator of
            ``cutcutcodec.core.classes.container.ContainerOutput``.
        filename : pathlike
            Path to the file to be encoded.
        streams_settings : typing.Iterable[dict]
            These are the encoding parameters associated with each stream.
            They contain all the information about the codecs.
            For audio streams, here is the format to follow:

                * "encodec": str,  # name of the codec or encoding library (ex libopus)
                * "rate": int or str,  # (autodetect) samplerate in Hz (ex 48000)
                * "options": dict,  # (optional) option for codec (ex {"application": "voip"})
                * "bitrate": int,  # (optional) the flow in bits/s (ex 1024000)
            For video streams, here is the format to follow:

                * "encodec": str,  # name of the codec or encoding library (ex libx264)
                * "rate": numbers.Real or str,  # (autodetect) the framerate in Hz (ex "30000/1001")
                * "shape": tuple[int, int],  # (autodetect) shape (height, width) of the frames
                * "options": dict,  # (optional) option for codec (ex {"crf": "23"})
                * "bitrate": int,  # (optional) the flow in bits/s (ex 6400000)
                * "pix_fmt": str,  # (optional) pixel format (ex "yuv444p10le")
        container_settings : dict, optional
            Global container file information.
            must contain the following fields:

                * "format": str or None,  # specific format to use, defaults to autodect
                * "container_options": dict,  # (optional) options to pass to the container
                * "options": dict,  # (optional) options to pass to the container and all streams
        """
        super().__init__(in_streams)

        filename = pathlib.Path(filename)
        assert filename.parent.exists(), filename
        assert not filename.is_dir(), filename
        self._filename = filename

        assert isinstance(streams_settings, typing.Iterable), streams_settings.__class__.__name__
        streams_settings = list(streams_settings)
        assert len(streams_settings) == len(self.in_streams)
        assert all(isinstance(s, dict) for s in streams_settings), streams_settings
        for stream, settings in zip(in_streams, streams_settings):
            assert "encodec" in settings, "missing the 'encodec' key"
            assert isinstance(settings["encodec"], str), settings["encodec"].__class__.__name__
            if "rate" in settings:
                # assert "rate" in settings, "missing the 'rate' key"
                settings["rate"] = Fraction(settings["rate"])
                assert isinstance(settings["rate"], numbers.Number)
                assert settings["rate"] > 0, settings["rate"]
            settings["options"] = settings.get("options", {})
            assert isinstance(settings["options"], dict), settings["options"].__class__.__name__
            settings["bitrate"] = settings.get("bitrate", None)
            if settings["bitrate"] is not None:
                settings["bitrate"] = round(parse_to_number(settings["bitrate"]))
                assert settings["bitrate"] >= 0, settings["bitrate"]
            if stream.type == "video":
                if "shape" in settings:
                    # assert "shape" in settings, "missing the 'shape' key"
                    assert isinstance(
                        settings["shape"], typing.Iterable
                    ), settings["shape"].__class__.__name__
                    settings["shape"] = settings["shape"]
                    assert all(isinstance(s, int) and s >= 1 for s in settings["shape"])
                settings["pix_fmt"] = settings.get("pix_fmt", None)
                assert settings["pix_fmt"] is None or isinstance(settings["pix_fmt"], str), \
                    settings["pix_fmt"].__class__.__name__
        self._streams_settings = streams_settings

        if container_settings is None:
            container_settings = {}
        assert isinstance(container_settings, dict), container_settings.__class__.__name__
        assert isinstance(container_settings.get("format", None), (str, type(None)))
        assert isinstance(container_settings.get("options", {}), dict)
        assert isinstance(container_settings.get("container_options", {}), dict)
        self._container_settings = copy.deepcopy(container_settings)

    def _getstate(self) -> dict:
        # conversion fraction to str for jsonisable
        streams_settings = self.streams_settings
        for settings in streams_settings:
            if not isinstance(settings["rate"], (int, float)):
                settings["rate"] = str(settings["rate"])
        # get the rest
        return {
            "filename": str(self.filename),
            "streams_settings": streams_settings,
            "container_settings": self.container_settings,
        }

    def _setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        keys = {"filename", "streams_settings", "container_settings"}
        assert state.keys() == keys, set(state)-keys
        ContainerOutputFFMPEG.__init__(self, in_streams, **state)

    @property
    def container_settings(self) -> dict:
        """Global container file information."""
        return {
            "format": self._container_settings.get("format", None),
            "options": self._container_settings.get("options", {}),
            "container_options": self._container_settings.get("container_options", {}),
        }

    @property
    def filename(self) -> pathlib.Path:
        """Return the absolute path + name of the file to encode."""
        return self._filename

    @property
    def streams_settings(self) -> list[dict]:
        """Information related to each codec."""
        return copy.deepcopy(self._streams_settings)

    def write(self):
        """Encode the streams and writes the file."""
        # container initialisation
        with av.open(
            str(self.filename),
            mode="w",
            format=self.container_settings["format"],
            options=self.container_settings["options"],
            container_options=self.container_settings["container_options"],
        ) as container_av:

            # streams initialisation
            streams_av = []
            shapes = []
            rates = []
            for stream, settings in zip(self.in_streams, self.streams_settings):
                if stream.type == "audio":
                    from cutcutcodec.core.analysis.stream import optimal_rate_audio
                    rates.append(int(settings.get("rate", optimal_rate_audio(stream))))
                    # assert rate == settings["rate"], settings["rate"]
                    stream_av = container_av.add_stream(
                        settings["encodec"], rates[-1], layout=stream.layout.name
                    )
                    stream_av.options = settings["options"] | {"strict": "experimental"}
                    if settings["bitrate"]:
                        stream_av.bit_rate = settings["bitrate"]  # int
                    streams_av.append(stream_av)
                    shapes.append(None)
                elif stream.type == "video":
                    from cutcutcodec.core.analysis.stream import optimal_rate_video
                    rates.append(settings.get("rate", optimal_rate_video(stream)))
                    stream_av = container_av.add_stream(settings["encodec"], rates[-1])
                    stream_av.options = settings["options"] | {
                        "strict": "experimental",
                        "color_primaries": str(stream.colorspace.color_primaries),
                        "color_trc": str(stream.colorspace.color_trc),
                        "colorspace": str(
                            FFMPEG_PRIMARIES_TO_COLORSPACE
                            .get(stream.colorspace.color_primaries, 2)
                        ),
                        "color_range": "tv",
                    }
                    from cutcutcodec.core.analysis.stream import optimal_shape_video
                    stream_av.height, stream_av.width = (
                        settings.get("shape", optimal_shape_video(stream))
                    )
                    if settings["pix_fmt"] is not None:
                        stream_av.pix_fmt = settings["pix_fmt"]  # str
                    if settings["bitrate"]:
                        stream_av.bit_rate = settings["bitrate"]  # int
                    streams_av.append(stream_av)
                    shapes.append((stream_av.height, stream_av.width))
                else:
                    raise TypeError(f"only audio and video streams are accepted, not {stream.type}")

            # display avancement
            duration = float(max(s.beginning + s.duration for s in self.in_streams))
            with tqdm.tqdm(
                desc=f"Encoding {self.filename.name}",
                total=duration,
                dynamic_ncols=True,
                bar_format=(
                    "{n:.2f}s {rate_fmt}"
                    if math.isinf(duration) else
                    "{l_bar}{bar}| {n:.2f}s/{total:.2f}s [{elapsed}<{remaining}]"
                ),
                smoothing=0.01,
                unit="sec_video",
            ) as progress_bar:

                # encode
                # rates = [settings["rate"] for settings in self.streams_settings]
                for index, frame in scheduler(
                    list(self.in_streams),
                    rates,
                    shapes=shapes,
                    samples=65536,  # for audio optimisation, 1 s vs 100 ms in average
                ):
                    frame = {
                        FrameAudio: frame_audio_to_av,
                        FrameVideo: frame_video_to_av,
                    }[frame.__class__](frame)
                    container_av.mux(streams_av[index].encode(frame))
                    progress_bar.total = max(progress_bar.total, frame.time)
                    progress_bar.update(frame.time - progress_bar.n)
                for stream_av in streams_av:
                    container_av.mux(stream_av.encode(None))  # flush buffer
                progress_bar.update(progress_bar.total - progress_bar.n)


def frame_audio_to_av(frame_audio: FrameAudio) -> av.audio.frame.AudioFrame:
    """Convert a FrameAudio cutcutcodec into a av audio frame for encoding.

    Parameters
    ----------
    frame_audio : cutcutcodec.core.classes.frame_audio.FrameAudio
        The torch frame to cast.

    Returns
    -------
    av_frame : av.audio.frame.audioFrame
        The equivalent av audio frame containing a similar audio signal.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.classes.frame_audio import FrameAudio
    >>> from cutcutcodec.core.io.write_ffmpeg import frame_audio_to_av
    >>>
    >>> frame_audio_to_av(FrameAudio(10, 48000, "mono", torch.empty(1, 1024)))  # doctest: +ELLIPSIS
    <av.AudioFrame pts=480000, 1024 samples at 48000Hz, mono, flt at ...
    >>> frame_audio_to_av(FrameAudio(10, 48000, "5.1", torch.empty(6, 1024)))  # doctest: +ELLIPSIS
    <av.AudioFrame pts=480000, 1024 samples at 48000Hz, 5.1, flt at ...
    >>>
    """
    assert isinstance(frame_audio, FrameAudio), frame_audio.__class__.__name__
    frame_np = frame_audio.numpy(force=True)
    frame_np = frame_np.astype(np.float32, copy=False)
    frame_np = np.ascontiguousarray(frame_np)  # fix ValueError: ndarray is not C-contiguous
    frame_av = av.audio.frame.AudioFrame.from_ndarray(
        np.expand_dims(frame_np.ravel(order="F"), 0),
        format="flt",
        layout=frame_audio.layout.name,
    )
    frame_av.rate = frame_audio.rate
    frame_av.time_base = Fraction(1, frame_audio.rate)
    frame_av.pts = round(frame_audio.time * frame_audio.rate)
    return frame_av


def frame_video_to_av(
    frame_video: FrameVideo,
    full: bool = False,
    yuv: bool = True,
) -> av.video.frame.VideoFrame:
    """Convert a FrameVideo cutcutcodec into a av video frame for encoding.

    Parameters
    ----------
    frame_video : cutcutcodec.core.classes.frame_video.FrameVideo
        The torch frame video to cast.
    full : boolean, default=False
        If set to True, encode in full range rather limited range as default.
    yuv : boolean, default=True
        If set to false, return a frame in rgb pixel format rather yuv.

    Returns
    -------
    av_frame : av.video.frame.VideoFrame
        The equivalent av video frame containing the similar image in format bgr24.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.classes.frame_video import FrameVideo
    >>> from cutcutcodec.core.io.write_ffmpeg import frame_video_to_av
    >>>
    >>> frame_video_to_av(
    ...     FrameVideo(10, torch.zeros(480, 720, 3))
    ... )  # doctest: +ELLIPSIS
    <av.VideoFrame, pts=3003000 yuv444p16le 720x480 at ...>
    >>> frame_video_to_av(
    ...     FrameVideo(10, torch.zeros(480, 720, 4))
    ... )  # doctest: +ELLIPSIS
    <av.VideoFrame, pts=3003000 yuva444p16le 720x480 at ...>
    >>> frame_video_to_av(
    ...     FrameVideo(10, torch.zeros(480, 720, 3)),
    ...     yuv=False,
    ... )  # doctest: +ELLIPSIS
    <av.VideoFrame, pts=3003000 rgb24 720x480 at ...>
    >>>
    """
    assert isinstance(frame_video, FrameVideo), frame_video.__class__.__name__
    assert isinstance(full, bool), full.__class__.__name__
    assert isinstance(yuv, bool), yuv.__class__.__name__

    frame_av = av.video.frame.VideoFrame.from_ndarray(
        to_yuv(frame_video.numpy(force=True), not full),
        format={  # get details with ffmpeg -pix_fmts
            3: "yuv444p16le",
            4: "yuva444p16le",
        }[frame_video.shape[2]],
    ) if yuv else av.video.frame.VideoFrame.from_ndarray(
        to_rgb(frame_video.convert(3).numpy(force=True), not full),
        format="rgb24",
    )
    frame_av.time_base = Fraction(1, 300300)  # ppcm 1001, 1000, 25, 30, 60
    frame_av.pts = round(frame_video.time / frame_av.time_base)
    frame_av.color_range = (  # see cutcutcodec.core.colorspace.cst.FFMPEG_RANGE
        av.video.reformatter.ColorRange.JPEG if full else av.video.reformatter.ColorRange.MPEG
    )
    return frame_av
