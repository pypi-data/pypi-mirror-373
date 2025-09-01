#!/usr/bin/env python3

"""Extract the properties of different streams of a multimedia file."""

from fractions import Fraction
import json
import numbers
import pathlib
import re
import subprocess

import numpy as np
import tqdm

from cutcutcodec.core.exceptions import MissingInformation, MissingStreamError


def _decode_duration_ffmpeg(filename: str, index: int, accurate: bool) -> Fraction:
    """Extract the duration by the complete decoding of the stream.

    Slow but 100% accurate method. The duration of the last frame is taken in consideration.
    Equivalent to:
    ``ffmpeg -thread 0 -loglevel quiet -stats -i file -map 0:v:0 -c:v rawvideo -f null /dev/null``

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _decode_duration_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> audio = str(get_project_root().parent / "media" / "audio" / "narration_5_1.oga")
    >>> _decode_duration_ffmpeg(audio, 0, accurate=True)
    Fraction(8, 1)
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _decode_duration_ffmpeg(video, 0, accurate=True)
    Fraction(9809, 1000)
    >>>
    """
    # get context
    if not (data := get_metadata(filename).get("streams", [])) or index >= len(data):
        raise MissingStreamError(f"only {len(data)} streams in '{filename}', no {index}")
    data = data[index]
    time_base = Fraction(data["time_base"])
    headers, infos = get_slices_metadata(filename, slice_type=("frame" if accurate else "packet"))
    last = dict(zip(headers[index], infos[index][-1, :]))
    del headers, infos

    # extract duration
    for time_key in ("best_effort_timestamp", "pts", "pkt_pts", "dts", "pkt_dts"):
        if (time := last.get(time_key, "N/A")) != "N/A":
            time = int(time) * time_base
            break
    else:  # if time not found
        for time_key in (
            "pts_time", "pkt_pts_time", "dts_time", "pkt_dts_time", "best_effort_timestamp_time"
        ):
            if (time := last.get(time_key, "N/A")) != "N/A":
                time = Fraction(time)
            break
        else:
            raise MissingInformation(
                "impossible to extract time of the last packet "
                f"of the stream {index} of '{filename}'"
            )
    duration = 0
    for duration_key in ("duration", "pkt_duration"):
        if (duration := last.get(duration_key, "N/A")) != "N/A":
            duration = int(duration) * time_base
            break
    else:  # if duration not found
        for duration_key in ("duration_time", "pkt_duration_time"):
            if (duration := last.get(duration_key, "N/A")) != "N/A":
                duration = Fraction(duration)
                break
    return time + duration


def _decode_timestamps_ffmpeg(
    filename: str, index: int
) -> np.ndarray[None | Fraction]:
    """Retrieve the exact position of the frames in a stream.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _decode_timestamps_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> audio = str(get_project_root().parent / "media" / "audio" / "narration_5_1.oga")
    >>> _decode_timestamps_ffmpeg(audio, 0)  # doctest: +ELLIPSIS
    array([Fraction(0, 1), Fraction(4, 125), Fraction(8, 125),
           Fraction(12, 125), Fraction(16, 125), Fraction(4, 25),
           Fraction(24, 125), Fraction(28, 125), Fraction(32, 125),
           ...
           Fraction(972, 125), Fraction(976, 125), Fraction(196, 25),
           Fraction(984, 125), Fraction(988, 125), Fraction(992, 125),
           Fraction(996, 125)], dtype=object)
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _decode_timestamps_ffmpeg(video, 0)  # doctest: +ELLIPSIS
    array([Fraction(0, 1), Fraction(33, 1000), Fraction(67, 1000),
           Fraction(1, 10), Fraction(133, 1000), Fraction(167, 1000),
           Fraction(1, 5), Fraction(117, 500), Fraction(267, 1000),
           ...
           Fraction(951, 100), Fraction(9543, 1000), Fraction(1197, 125),
           Fraction(961, 100), Fraction(9643, 1000), Fraction(2419, 250),
           Fraction(971, 100), Fraction(9743, 1000), Fraction(1222, 125)],
          dtype=object)
    >>>
    """
    # get context
    if (headers := get_metadata(filename).get("streams", [])) and index < len(headers):
        headers = headers[index]
        if "time_base" in headers:
            time_base = Fraction(headers["time_base"])
    else:
        time_base = 0

    # decode frames
    headers, infos = get_slices_metadata(filename, slice_type="frame")
    if index >= len(headers):
        raise MissingStreamError(f"only {len(headers)} streams in '{filename}', no {index}")
    headers, infos = headers[index], infos[index]

    # catch information
    timestamps = []
    for frame in infos:
        data = dict(zip(headers, frame))
        for time_key in ("best_effort_timestamp", "pts", "pkt_pts", "dts", "pkt_dts"):
            if time_base and (time := data.get(time_key, "N/A")) != "N/A":
                timestamps.append(int(time) * time_base)
                break
        else:
            for time_key in (
                "best_effort_timestamp_time", "pts_time", "pkt_pts_time", "dts_time",
                "pkt_dts_time"
            ):
                if (time := data.get(time_key, "N/A")) != "N/A":
                    timestamps.append(Fraction(time))
                    break
            else:
                timestamps.append(None)

    # cast to ndarray
    timestamps = np.array(timestamps, dtype=object)
    return timestamps


def _estimate_duration_ffmpeg(filename: str, index: int, *, _indirect=True) -> Fraction:
    """Extract the duration from the metadata.

    Very fast method but inaccurate. It doesn't work all the time.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _estimate_duration_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> audio = str(get_project_root().parent / "media" / "audio" / "narration_5_1.oga")
    >>> _estimate_duration_ffmpeg(audio, 0)
    Fraction(8, 1)
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_duration_ffmpeg(video, 0)
    Fraction(9809, 1000)
    >>>
    """
    metadata = get_metadata(filename)
    if (stream_meta := metadata.get("streams", [])) and len(stream_meta) > index:
        stream_meta = stream_meta[index]
        if "duration_ts" in stream_meta and "time_base" in stream_meta:
            return stream_meta["duration_ts"] * Fraction(stream_meta["time_base"])
        if "duration" in stream_meta:
            return Fraction(stream_meta["duration"])
        for key, val in stream_meta.get("tags", {}).items():
            if "duration" in key.lower():
                if (duration := parse_duration(val)) is not None:
                    return duration
    if (format_meta := metadata.get("format", None)) is not None and "duration" in format_meta:
        return Fraction(format_meta["duration"])

    if _indirect:
        return (
            _estimate_len_ffmpeg(filename, index, _indirect=False)
            / _estimate_rate_ffmpeg(filename, index, _indirect=False)
        )

    raise MissingInformation(
        f"'ffprobe' did not get a correct duration in '{filename}' stream {index}"
    )


def _estimate_len_ffmpeg(filename: str, index: int, *, _indirect=True) -> int:
    """Extract the number of frames or samples from the metadata.

    Very fast method but inaccurate. It doesn't work all the time.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _estimate_len_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> audio = str(get_project_root().parent / "media" / "audio" / "narration_5_1.oga")
    >>> _estimate_len_ffmpeg(audio, 0)
    128000
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_len_ffmpeg(video, 0)
    294
    >>>
    """
    metadata = get_metadata(filename)
    if not ((stream_meta := metadata.get("streams", [])) and len(stream_meta) > index):
        raise MissingStreamError(f"no stream {index} metadata detected in '{filename}'")
    stream_meta = stream_meta[index]

    if "nb_frames" in stream_meta:
        return int(stream_meta["nb_frames"])

    if _indirect:
        return round(
            _estimate_duration_ffmpeg(filename, index, _indirect=False)
            * _estimate_rate_ffmpeg(filename, index, _indirect=False)
        )
    raise MissingInformation(
        f"'ffprobe' did not get a correct frames number in '{filename}' stream {index}"
    )


def _estimate_pix_fmt_ffmpeg(filename: str, index: int) -> str:
    """Retrive via ffmpeg, the metadata concerning the pixel format.

    This function is fast because it reads only the header of the file.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _estimate_pix_fmt_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_pix_fmt_ffmpeg(video, 0)
    'yuv420p'
    >>>
    """
    metadata = get_metadata(filename)
    if not ((stream_meta := metadata.get("streams", [])) and len(stream_meta) > index):
        raise MissingStreamError(f"no stream {index} metadata detected in '{filename}'")
    stream_meta = stream_meta[index]

    if "pix_fmt" not in stream_meta:
        raise MissingInformation(
            f"'ffprobe' did not find the pixel format in '{filename}' stream {index}"
        )
    return stream_meta["pix_fmt"]


def _estimate_rate_ffmpeg(filename: str, index: int, *, _indirect=True) -> Fraction:
    """Retrieve via ffmpeg, the metadata concerning the fps or the framerate.

    This function is fast because it reads only the header of the file.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _estimate_rate_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> audio = str(get_project_root().parent / "media" / "audio" / "narration_5_1.oga")
    >>> _estimate_rate_ffmpeg(audio, 0)
    Fraction(16000, 1)
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_rate_ffmpeg(video, 0)
    Fraction(30000, 1001)
    >>>
    """
    metadata = get_metadata(filename)
    if not ((stream_meta := metadata.get("streams", [])) and len(stream_meta) > index):
        raise MissingStreamError(f"no stream {index} metadata detected in '{filename}'")
    stream_meta = stream_meta[index]

    for rate_key in ("r_frame_rate", "sample_rate", "avg_frame_rate"):
        if rate_key in stream_meta:
            try:
                return Fraction(stream_meta[rate_key])
            except ZeroDivisionError:
                continue

    if _indirect:
        return (
            _estimate_len_ffmpeg(filename, index, _indirect=False)
            / _estimate_duration_ffmpeg(filename, index, _indirect=False)
        )
    raise MissingInformation(
        f"'ffprobe' did not get a correct framerate in '{filename}' stream {index}"
    )


def _estimate_resolution_ffmpeg(filename: str, index: int) -> tuple[int, int]:
    """Retrive via ffmpeg, the metadata concerning the image resolution.

    This function is fast because it reads only the header of the file.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _estimate_resolution_ffmpeg
    >>> from cutcutcodec.utils import get_project_root
    >>> video = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _estimate_resolution_ffmpeg(video, 0)
    (720, 1280)
    >>> _estimate_resolution_ffmpeg(video, 1)
    (360, 640)
    >>>
    """
    metadata = get_metadata(filename)
    if not ((stream_meta := metadata.get("streams", [])) and len(stream_meta) > index):
        raise MissingStreamError(f"no stream {index} metadata detected in '{filename}'")
    stream_meta = stream_meta[index]

    for h_key, w_key in (("height", "width"), ("coded_height", "coded_width")):
        if h_key in stream_meta and w_key in stream_meta:
            return (stream_meta[h_key], stream_meta[w_key])
    raise MissingInformation(
        f"'ffprobe' did not get a correct resolution in '{filename}' stream {index}"
    )


def _get_streams_type(filename: pathlib.Path) -> list[str]:
    """Help ``get_streams_type``."""
    # optional shortcut
    from cutcutcodec.core.io.cst import AUDIO_SUFFIXES, IMAGE_SUFFIXES
    if filename.suffix.lower() in IMAGE_SUFFIXES:
        return ["video"]
    if filename.suffix.lower() in AUDIO_SUFFIXES:
        return ["audio"]

    # rigourus way
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=index,codec_type",
        "-of", "csv=p=0", str(filename),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        raise MissingStreamError(f"'ffprobe' can not open '{filename}'") from err
    if not (indexs_streams := result.stdout.decode().strip().split("\n")):
        raise MissingStreamError(f"'ffprobe' did not find any stream info in '{filename}'")

    indexs_streams = [ind for ind in indexs_streams if ind]
    streams = {}
    for index_stream in indexs_streams:
        index, stream, *_ = index_stream.split(",")
        index = int(index)
        if streams.get(index, None) is not None and stream != streams[index]:
            raise MissingStreamError(f"index {index} appears twice in '{filename}'")
        if stream not in {"audio", "subtitle", "video"}:
            raise ValueError(
                f"the stream {index} ({stream}) in '{filename}' "
                "not in 'audio', 'video' or 'subtitle'"
            )
        streams[index] = stream

    if streams.keys() != set(range(len(streams))):
        raise MissingStreamError(f"missing stream index in '{filename}', {streams}")

    return [streams[i] for i in range(len(streams))]


def _help_slices_metadata_context(filename: pathlib.Path) -> tuple[list[Fraction], Fraction]:
    """Help ``get_slices_metadata``."""
    if not (data := get_metadata(filename).get("streams", [])):
        raise MissingStreamError(f"no stream metadata detected in '{filename}'")
    times_base = [Fraction(s["time_base"]) for s in data if "time_base" in s]
    if len(times_base) != len(data):
        raise MissingInformation(
            f"the field 'time_base' is not founded for all streams metadata of '{filename}'"
        )
    duration = Fraction(0)
    for stream_index in range(len(times_base)):
        try:
            duration = max(duration, _estimate_duration_ffmpeg(filename, stream_index))
        except MissingInformation:
            continue
    return times_base, duration


def _help_slices_metadata_parse_data(data, sort_new_h, sort_old_h=None):
    """Help ``get_slices_metadata``."""
    if not isinstance(data, dict):
        data = dict(zip(sort_old_h, data))
    data = [[data.get(h, "N/A") for h in sort_new_h]]
    data = np.array(data, dtype="U")
    return data


def _map_index_rel_to_abs(filename: str, index: int, stream_type: str) -> int:
    """Relative stream index to absolute stream index.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import _map_index_rel_to_abs
    >>> from cutcutcodec.utils import get_project_root
    >>> media = str(get_project_root().parent / "media" / "video" / "intro.webm")
    >>> _map_index_rel_to_abs(media, 0, "video")
    0
    >>> _map_index_rel_to_abs(media, 1, "video")
    1
    >>> _map_index_rel_to_abs(media, 0, "audio")
    2
    >>> _map_index_rel_to_abs(media, 1, "audio")
    3
    >>>
    """
    types = get_streams_type(filename)
    abs_indexs = [i for i, t in enumerate(types) if t == stream_type]
    if index >= len(abs_indexs):
        raise MissingStreamError(
            f"relative {stream_type} index {index} of '{filename}' not in {types}"
        )
    return abs_indexs[index]


def get_metadata(
    filename: pathlib.Path | str | bytes, ignore_errors=False
) -> dict[str]:
    """Call ``ffprobe`` and parse the result as a dictionary.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the file containing streams.
    ignore_errors : boolean, default=False
        If True, returns an empty dict
        rather than throwing an exception if invalid data are detected.

    Returns
    -------
    metadata : dict
        All the metadata containing in the container and each streams.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.analysis.ffprobe import get_metadata
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> pprint(get_metadata(media))  # doctest: +ELLIPSIS
    {'format': {'bit_rate': '401541',
                'duration': '9.891000',
                'filename': ...,
                'format_long_name': 'Matroska / WebM',
                'format_name': 'matroska,webm',
                ...
                'size': '496456',
                'start_time': '0.000000',
                'tags': ...,
     'streams': [{'avg_frame_rate': '30000/1001',
                  'chroma_location': 'left',
                  'closed_captions': 0,
                  'codec_long_name': 'Google VP9',
                  'codec_name': 'vp9',
                  'codec_tag': '0x0000',
                  'codec_tag_string': '[0][0][0][0]',
                  'codec_type': 'video',
                  'coded_height': 720,
                  'coded_width': 1280,
                  'color_primaries': 'bt709',
                  'color_range': 'tv',
                  'color_space': 'bt709',
                  'color_transfer': 'bt709',
                  'display_aspect_ratio': '16:9',
                  'disposition': {'attached_pic': 0,
                                  ...
                                  'visual_impaired': 0},
                  'field_order': 'progressive',
                  'film_grain': 0,
                  'has_b_frames': 0,
                  'height': 720,
                  'index': 0,
                  'level': -99,
                  'pix_fmt': 'yuv420p',
                  'profile': 'Profile 0',
                  'r_frame_rate': '30000/1001',
                  'refs': 1,
                  'sample_aspect_ratio': '1:1',
                  'start_pts': 0,
                  'start_time': '0.000000',
                  'tags': ...,
                  'time_base': '1/1000',
                  'width': 1280},
                 ...
                 {'avg_frame_rate': '0/0',
                  'bits_per_sample': 0,
                  'channel_layout': 'mono',
                  'channels': 1,
                  'codec_long_name': 'Vorbis',
                  'codec_name': 'vorbis',
                  'codec_tag': '0x0000',
                  'codec_tag_string': '[0][0][0][0]',
                  'codec_type': 'audio',
                  'disposition': {'attached_pic': 0,
                                  ...
                                  'visual_impaired': 0},
                  'extradata_size': 3340,
                  'index': 3,
                  'initial_padding': 0,
                  'r_frame_rate': '0/0',
                  'sample_fmt': 'fltp',
                  'sample_rate': '22050',
                  'start_pts': 0,
                  'start_time': '0.000000',
                  'tags': ...,
                  'time_base': '1/1000'}]}
    >>>
    """
    filename = pathlib.Path(filename)
    assert filename.exists(), filename
    assert isinstance(ignore_errors, bool), ignore_errors.__class__.__name__

    cmd = [
        "ffprobe", "-v", "error",
        "-show_format", "-show_streams", "-show_programs", "-show_chapters",
        "-of", "json", str(filename),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        if ignore_errors:
            return {}
        raise MissingInformation(f"can not open '{filename}' with 'ffprobe'") from err
    if not (meta_str := result.stdout.decode()) and not ignore_errors:
        raise MissingInformation(f"'ffprobe' did not decode '{filename}'")
    try:
        meta_dict = json.loads(meta_str)
    except json.decoder.JSONDecodeError:
        if ignore_errors:
            return {}
    meta_dict = {k: v for k, v in meta_dict.items() if v}
    return meta_dict


def get_slices_metadata(
    filename: pathlib.Path | str | bytes, slice_type: str = "frame"
) -> tuple[list[list[str]], list[np.ndarray]]:
    """Get the packets informations for all streams.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the file containing streams.
    slice_type : str
        The type of slices to decode, 'frame' or 'packet'.
        'frame' is slower but more accurate and informative.
        'packet' is faster but less acurate.

    Returns
    -------
    headers : list[list[str]]
        For each stream, the name of the columns.
    infos: list[np.ndarray]
        For each stream, the 2d str array.
        Each row correspond to one packet.

    Examples
    --------
    >>> from pprint import pprint
    >>> from cutcutcodec.core.analysis.ffprobe import get_slices_metadata
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> headers, data = get_slices_metadata(media, slice_type="packet")
    >>> pprint(headers)  # doctest: +ELLIPSIS
    [['codec_type',
      'dts',
      'dts_time',
      'duration',
      'duration_time',
      'flags',
      'pos',
      'pts',
      'pts_time',
      'size',
      'stream_index'],
     ...
     ['codec_type',
      'dts',
      'dts_time',
      'duration',
      'duration_time',
      'flags',
      'pos',
      'pts',
      'pts_time',
      'size',
      'stream_index']]
    >>> pprint(data)  # doctest: +ELLIPSIS
    [array([['video', '0', '0.000000', ..., '0.000000', '311', '0'],
           ['video', '33', '0.033000', ..., '0.033000', '48', '0'],
           ['video', '67', '0.067000', ..., '0.067000', '48', '0'],
           ...,
           ['video', '9710', '9.710000', ..., '9.710000', '167', '0'],
           ['video', '9743', '9.743000', ..., '9.743000', '133', '0'],
           ['video', '9776', '9.776000', ..., '9.776000', '82', '0']],
          dtype='<U8'),
     ...
     array([['audio', '0', '0.000000', ..., '0.000000', '1', '3'],
           ['audio', '23', '0.023000', ..., '0.023000', '1', '3'],
           ['audio', '46', '0.046000', ..., '0.046000', '1', '3'],
           ...,
           ['audio', '9822', '9.822000', ..., '9.822000', '100', '3'],
           ['audio', '9845', '9.845000', ..., '9.845000', '92', '3'],
           ['audio', '9868', '9.868000', ..., '9.868000', '46', '3']],
          dtype='<U8')]
    >>>
    """
    filename = pathlib.Path(filename)
    assert filename.exists(), filename
    assert isinstance(slice_type, str), slice_type.__class__.__name__
    assert slice_type in {"frame", "packet"}, slice_type

    # create subprocess, as soon as possible to start calculations
    with subprocess.Popen(
        [
            "ffprobe", "-v", "error",
            f"-show_{slice_type}s",
            "-of", "compact", str(filename)
        ],
        stdout=subprocess.PIPE
    ) as child:

        # get context
        times_base, duration = _help_slices_metadata_context(filename)

        # declaration
        headers_infos = [
            [set() for _ in range(len(times_base))],  # contains all headers
            [[] for _ in range(len(times_base))],  # contains the dictionary for each streams
        ]

        # display avancement
        with tqdm.tqdm(
            desc=f"Decoding {slice_type} of {pathlib.Path(filename).name}",
            total=float(duration),
            dynamic_ncols=True,
            bar_format="{l_bar}{bar}| {n:.0f}s/{total:.0f}s [{elapsed}<{remaining}]",
            disable=(duration < 60),
        ) as progress_bar:

            # parse result
            while (data := child.stdout.readline()) or child.poll() is None:
                data = data.decode().strip()
                if not data.startswith(slice_type):
                    continue
                data = dict((field.split("=")+["N/A"])[:2] for field in data.split("|")[1:])
                data = {k: v for k, v in data.items() if v != "N/A"}
                stream_index = int(data["stream_index"])
                data_keys = set(data)
                sort_all_h = sorted(headers_infos[0][stream_index] | data_keys)

                # management append new header
                if not data_keys.issubset(headers_infos[0][stream_index]):
                    sort_old_h = sorted(headers_infos[0][stream_index])
                    headers_infos[1][stream_index] = [
                        _help_slices_metadata_parse_data(d.ravel(), sort_all_h, sort_old_h)
                        for d in headers_infos[1][stream_index]
                    ]
                    headers_infos[0][stream_index] |= data_keys

                # append new data
                headers_infos[1][stream_index].append(
                    _help_slices_metadata_parse_data(data, sort_all_h)
                )
                if sum(len(inf) for inf in headers_infos[1]) == 500_000:  # memory compression
                    headers_infos[1] = [[np.vstack(d)] if d else [] for d in headers_infos[1]]

                # update display
                for time_key in ("best_effort_timestamp", "pts", "pkt_pts", "dts", "pkt_dts"):
                    if (time := data.get(time_key, "N/A")) != "N/A":
                        if (time := float(int(time) * times_base[stream_index])) > progress_bar.n:
                            progress_bar.total = max(progress_bar.total, time)
                            progress_bar.update(time - progress_bar.n)
                        break

        # close subprocess
        data = child.communicate()
        progress_bar.update(progress_bar.total - progress_bar.n)
        if child.returncode:
            raise OSError(child.returncode, b" and ".join(data).decode())

        # parse
        headers_infos[0] = [sorted(h) for h in headers_infos[0]]
        headers_infos[1] = [np.vstack(d) if d else [] for d in headers_infos[1]]
        return headers_infos


def get_streams_type(
    filename: pathlib.Path | str | bytes, ignore_errors=False
) -> list[str]:
    """Retrieve in order the stream types present in the file.

    Parameters
    ----------
    filename : pathlike
        The pathlike of the file containing streams.
    ignore_errors : boolean, default=False
        If True, returns an empty list
        rather than throwing an exception if no valid stream is detected.

    Returns
    -------
    streams_type : list[str]
        Each item can be "audio", "subtitle" or "video".

    Raises
    ------
    MissingStreamError
        If ``ignore_errors`` is False and if one of the indexes is missing or redondant.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import get_streams_type
    >>> from cutcutcodec.utils import get_project_root
    >>> media = get_project_root().parent / "media" / "video" / "intro.webm"
    >>> get_streams_type(media)
    ['video', 'video', 'audio', 'audio']
    >>> get_streams_type(get_project_root() / "__main__.py", ignore_errors=True)
    []
    >>>
    """
    filename = pathlib.Path(filename)
    assert filename.exists(), filename
    assert isinstance(ignore_errors, bool), ignore_errors.__class__.__name__

    try:
        return _get_streams_type(filename)
    except MissingStreamError as err:
        if ignore_errors:
            return []
        raise err


def parse_duration(duration: numbers.Real | str) -> None | Fraction:
    """Try to convert a duration information into a fraction in second.

    Parameters
    ----------
    duration : number or str
        The duration to cast in integer

    Returns
    -------
    sec_duration : Fraction
        The decoded duration in second.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.ffprobe import parse_duration
    >>> parse_duration(1.5)  # from float
    Fraction(3, 2)
    >>> parse_duration(2)  # from integer
    Fraction(2, 1)
    >>> parse_duration(".5")  # from float rep
    Fraction(1, 2)
    >>> parse_duration("1.")  # from float rep
    Fraction(1, 1)
    >>> parse_duration("1.5")  # from complete float rep
    Fraction(3, 2)
    >>> parse_duration("1:01:01")  # from h:m:s
    Fraction(3661, 1)
    >>>
    """
    assert isinstance(duration, (numbers.Real, str)), duration.__class__.__name__
    try:
        return Fraction(duration)
    except ValueError:
        pass
    if (match := re.fullmatch(r"(?P<h>\d+):(?P<m>\d\d):(?P<s>\d*\.?\d+)", duration)):
        return 3600*int(match["h"]) + 60*int(match["m"]) + Fraction(match["s"])
    return None
