#!/usr/bin/env python3

"""Disjonction of alla cases of framecaster."""

import time

import numpy as np

from cutcutcodec.core.io.framecaster import from_yuv


TVH, TVL = 219.0/255.0, 16.0/255.0


def naive_converter(frame: np.ndarray, is_tv: bool) -> np.ndarray:
    """Pure numpy implementation."""
    assert isinstance(frame, np.ndarray), frame.__class__.__name__
    if frame.ndim == 2:
        frame = frame[:, :, None]
    else:
        assert frame.ndim == 3, frame.shape
    assert isinstance(is_tv, bool), is_tv.__class__.__name__

    n_bits = 8 * frame.itemsize
    out = frame.astype(np.float32, copy=True)
    if is_tv and frame.dtype.type in {np.uint8, np.uint16}:
        fact = float(2**(n_bits - 8))
        out[:, :, 0] = out[:, :, 0] * (1.0 / (219.0 * fact)) - (16.0 / 219.0)
        if out.shape[2] >= 3:
            out[:, :, 1:3] = out[:, :, 1:3] * (1.0 / (224.0 * fact)) - (128.0 / 224.0)
        if out.shape[2] == 4:
            out[:, :, 3] = out[:, :, 3] * (1.0 / (219.0 * fact)) - (16.0 / 219.0)
    elif not is_tv and frame.dtype.type in {np.uint8, np.uint16}:
        out *= 1.0 / float(2**n_bits - 1)
        if out.shape[2] >= 3:
            out[:, :, 1:3] -= float(2**(n_bits-1)) / float(2**n_bits - 1)
    elif frame.dtype == np.float32:
        pass
    else:
        raise NotImplementedError("this input frame format is not yet supported")

    return out


def timer(frame: np.ndarray, name: str, *args):
    """Ensure C implementation is faster than pure numpy."""
    t_naive, t_c = [], []
    for _ in range(64):
        frame_copy = frame.copy()
        t_i = time.time()
        naive_converter(frame_copy, *args)
        t_naive.append(time.time() - t_i)
        frame_copy = frame.copy()
        t_i = time.time()
        from_yuv(frame_copy, *args)
        t_c.append(time.time() - t_i)
    t_naive = np.median(t_naive)
    t_c = np.median(t_c)
    print(f"{name} naive:{1000*t_naive:.2f}ms vs c:{1000*t_c:.2f}ms ({t_naive/t_c:.2f} x faster)")
    assert t_c < t_naive


def test_float32_y_pc():
    """Test this conversion."""
    frame = np.array([[0.0, 1.0]], dtype=np.float32)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
    )


def test_float32_yuv_pc():
    """Test this conversion."""
    frame = np.array([[[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]], dtype=np.float32)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
    )


def test_float32_yuva_pc():
    """Test this conversion."""
    frame = np.array([[[0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0]]], dtype=np.float32)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
    )


def test_uint8_y_pc():
    """Test this conversion."""
    frame = np.array([[0, 255]], dtype=np.uint8)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
    )
    timer(np.empty((1080, 1920), dtype=np.uint8), "u8-y-pc", is_tv)


def test_uint8_y_tv():
    """Test this conversion."""
    frame = np.array([[16, 235]], dtype=np.uint8)
    is_tv = True
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
    )
    timer(np.empty((1080, 1920), dtype=np.uint8), "u8-y-tv", is_tv)


def test_uint8_yuv_pc():
    """Test this conversion."""
    frame = np.array([[[0, 0, 0], [255, 255, 255]]], dtype=np.uint8)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 3), dtype=np.uint8), "u8-yuv-pc", is_tv)


def test_uint8_yuv_tv():
    """Test this conversion."""
    frame = np.array([[[16, 16, 16], [235, 235, 235]]], dtype=np.uint8)
    is_tv = True
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 3), dtype=np.uint8), "u8-yuv-tv", is_tv)


def test_uint8_yuva_pc():
    """Test this conversion."""
    frame = np.array([[[0, 0, 0, 0], [255, 255, 255, 255]]], dtype=np.uint8)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 4), dtype=np.uint8), "u8-yuva-pc", is_tv)


def test_uint8_yuva_tv():
    """Test this conversion."""
    frame = np.array([[[16, 16, 16, 16], [235, 235, 235, 235]]], dtype=np.uint8)
    is_tv = True
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 4), dtype=np.uint8), "u8-yuva-tv", is_tv)


def test_uint16_y_pc_16b():
    """Test this conversion."""
    frame = np.array([[0, 65535]], dtype=np.uint16)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920), dtype=np.uint16), "u16-y-pc-16b", is_tv)


def test_uint16_y_tv_65535():
    """Test this conversion."""
    frame = np.array([[4864, 60160]], dtype=np.uint16)
    is_tv = True
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920), dtype=np.uint16), "u16-y-tv-16b", is_tv)


def test_uint16_yuv_pc_16b():
    """Test this conversion."""
    frame = np.array([[[0, 0, 0], [65535, 65535, 65535]]], dtype=np.uint16)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 3), dtype=np.uint16), "u16-yuv-pc_16b", is_tv)


def test_uint16_yuv_tv_16b():
    """Test this conversion."""
    frame = np.array([[[4864, 4864, 4864], [60160, 60160, 60160]]], dtype=np.uint16)
    is_tv = True
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 3), dtype=np.uint16), "u16-yuv-tv-16b", is_tv)


def test_uint16_yuva_pc_16b():
    """Test this conversion."""
    frame = np.array([[[0, 0, 0, 0], [65535, 65535, 65535, 65535]]], dtype=np.uint16)
    is_tv = False
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 4), dtype=np.uint16), "u16-yuva-pc-16b", is_tv)


def test_uint16_yuva_tv_10b():
    """Test this conversion."""
    frame = np.array([[[4864, 4864, 4864, 4864], [60160, 60160, 60160, 60160]]], dtype=np.uint16)
    is_tv = True
    np.testing.assert_allclose(
        from_yuv(frame, is_tv),
        naive_converter(frame, is_tv),
        atol=1e-6,
    )
    timer(np.empty((1080, 1920, 4), dtype=np.uint16), "u16-yuva-tv-16b", is_tv)
