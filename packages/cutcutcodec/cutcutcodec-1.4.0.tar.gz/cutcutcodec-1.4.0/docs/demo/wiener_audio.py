#!/usr/bin/env python3

"""Audio wiener demo code with streamlit."""

import math
import pathlib
import tempfile

import cutcutcodec
import streamlit as st


def draw_header():
    """Display the header."""
    st.markdown(
        """
        ## Winer Audio Denoiser

        This app shows how to model and convert different colorspaces using the
        [`cutcutcodec`](https://cutcutcodec.readthedocs.io/latest/build/api/cutcutcodec.core.filter.audio.wiener.html) library.
        """
    )


def upload_file() -> pathlib.Path:
    """Upload an audio file."""
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        accept_multiple_files=False,
        type=cutcutcodec.core.io.cst.AUDIO_SUFFIXES,
    )
    if uploaded_file is not None:
        file = pathlib.Path(tempfile.gettempdir()) / uploaded_file.name
        file = file.with_stem("wiener_audio_uploaded")
        with open(file, "wb") as raw:
            raw.write(uploaded_file.read())
        return file
    return cutcutcodec.utils.get_project_root().parent / "media" / "audio" / "wiener.wav"


def play_audio(stream: cutcutcodec.classes.stream_audio.StreamAudio) -> float:
    """Play the audio file."""
    rate = cutcutcodec.core.analysis.stream.optimal_rate_audio(stream)
    st.write(f"{stream.layout.name} noisy audio, sampled at {rate} Hz")
    duration = stream.duration
    samples = stream.snapshot(0, rate, round(rate*duration), pad=True)
    st.audio(samples.numpy(), sample_rate=rate)
    return float(duration)


def select_noise(stream: cutcutcodec.classes.stream_audio.StreamAudio) -> cutcutcodec.classes.stream_audio.StreamAudio:
    """Show a slicer to select the noise part."""
    duration = float(stream.duration)
    start, stop = st.slider(
        "noise profile",
        0.0,
        duration,
        format="%.2f",
        value=(0.5*duration, duration),
    )
    noise = stream.apply_audio_subclip(start, (stop - start)).apply_audio_delay(-start)
    return noise


def conf_selector(noise: cutcutcodec.classes.stream_audio.StreamAudio) -> tuple[float, float]:
    """Select the winer filter parameters."""
    level = st.slider("denoise level", 0.0, 1.0, format="%.2f", value=0.9)
    rate = cutcutcodec.core.analysis.stream.optimal_rate_audio(noise)
    min_band = math.log10(2.0/float(noise.duration))
    max_band = math.log10(float(rate)/2.0)
    default = min(max_band, max(min_band, math.log10(20.0)))
    log_band = st.slider("freq band log(Hz)", min_band, max_band, value=default)
    band = 10.0 ** log_band
    st.text(f"band: {band:.1f} Hz")
    return level, band


def download_result(denoised: cutcutcodec.classes.stream_audio.StreamAudio):
    """Set an option to save the file."""
    rate = cutcutcodec.core.analysis.stream.optimal_rate_audio(denoised)
    dst = pathlib.Path(tempfile.gettempdir()) / "wiener_audio_denoised.flac"
    cutcutcodec.write([denoised], dst, streams_settings=[{"encodec": "flac", "rate": rate}])
    st.download_button("Download", open(dst, "rb"), file_name=dst.name)


def main():
    """Call the full loop."""
    draw_header()
    st.markdown("### Select the full audio file")
    with cutcutcodec.read(upload_file()) as container:
        stream = container.out_select("audio")[0]
        duration = play_audio(stream)
        st.markdown("### Select the noise Profile")
        noise = select_noise(stream)
        print(float(noise.duration))
        play_audio(noise)
        st.markdown("### Set parameters")
        level, band = conf_selector(noise)
        st.markdown("### Denoise with the optimal wiener filter")
        denoised = (noise | stream).apply_audio_wiener(level=level, band=band).out_streams[0]
        play_audio(denoised)
        download_result(denoised)


if __name__ == "__main__":
    main()
