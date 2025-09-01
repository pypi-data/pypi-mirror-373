#!/usr/bin/env python3

"""Test the behavour of the metrics."""

import timeit

import numpy as np
import pytest
import torch

from cutcutcodec.core.analysis.video.metric.metric import psnr as psnr_c, ssim as ssim_c
from cutcutcodec.core.analysis.video.metric.psnr_torch import psnr_torch
from cutcutcodec.core.analysis.video.metric.ssim_torch import ssim_conv_torch, ssim_fft_torch


def test_psnr_c_equal_psnr_torch_float32():
    """Test if both psnr methods give the same result."""
    np.random.seed(0)
    im1 = np.random.randn(720, 1080, 3).astype(np.float32)
    im2 = np.random.randn(720, 1080, 3).astype(np.float32)
    assert psnr_c(im1, im2) == pytest.approx(
        float(psnr_torch(torch.asarray(im1), torch.asarray(im2))), abs=1e-3, rel=1e-3
    )


def test_psnr_c_equal_psnr_torch_float64():
    """Test if both psnr methods give the same result."""
    np.random.seed(0)
    im1 = np.random.randn(720, 1080, 3).astype(np.float64)
    im2 = np.random.randn(720, 1080, 3).astype(np.float64)
    assert psnr_c(im1, im2) == pytest.approx(
        float(psnr_torch(torch.asarray(im1), torch.asarray(im2)))
    )


def test_psnr_same_float32():
    """Test if all psnr methods retun 100 when images are the same."""
    np.random.seed(0)
    for img in (
        np.ones((720, 1080, 3), dtype=np.float32),
        np.zeros((720, 1080, 3), dtype=np.float32),
        np.random.random((720, 1080, 3)).astype(np.float32),
    ):
        assert psnr_c(img, img) == pytest.approx(100.0, abs=1e-3, rel=1e-3)
        img = torch.asarray(img)
        assert float(psnr_torch(img, img)) == pytest.approx(100.0, abs=1e-3, rel=1e-3)


def test_psnr_same_float64():
    """Test if all psnr methods retun 100 when images are the same."""
    np.random.seed(0)
    for img in (
        np.ones((720, 1080, 3), dtype=np.float64),
        np.zeros((720, 1080, 3), dtype=np.float64),
        np.random.random((720, 1080, 3)).astype(np.float64),
    ):
        assert psnr_c(img, img) == pytest.approx(100.0)
        img = torch.asarray(img)
        assert float(psnr_torch(img, img)) == pytest.approx(100.0)


def test_ssim_same_float32():
    """Test if all psnr methods retun 1 when images are the same."""
    np.random.seed(0)
    for img in (
        np.ones((720, 1080, 3), dtype=np.float32),
        np.zeros((720, 1080, 3), dtype=np.float32),
        np.random.random((720, 1080, 3)).astype(np.float32),
    ):
        assert ssim_c(img, img) == pytest.approx(1.0, abs=1e-3, rel=1e-3)
        img = torch.asarray(img)
        assert float(ssim_conv_torch(img, img)) == pytest.approx(1.0, abs=1e-3, rel=1e-3)
        assert float(ssim_fft_torch(img, img)) == pytest.approx(1.0, abs=1e-3, rel=1e-3)


def test_ssim_same_float64():
    """Test if all psnr methods retun 1 when images are the same."""
    np.random.seed(0)
    for img in (
        np.ones((720, 1080, 3), dtype=np.float64),
        np.zeros((720, 1080, 3), dtype=np.float64),
        np.random.random((720, 1080, 3)).astype(np.float64),
    ):
        assert ssim_c(img, img) == pytest.approx(1.0)
        img = torch.asarray(img)
        assert float(ssim_conv_torch(img, img)) == pytest.approx(1.0)
        assert float(ssim_fft_torch(img, img)) == pytest.approx(1.0)


def test_ssim_c_equal_ssim_conv_torch_float32():
    """Test if both ssim methods give the same result."""
    np.random.seed(0)
    im1 = np.random.randn(720, 1080, 3).astype(np.float32)
    im2 = np.random.randn(720, 1080, 3).astype(np.float32)
    assert ssim_c(im1, im2) == pytest.approx(
        float(ssim_conv_torch(torch.asarray(im1), torch.asarray(im2))), abs=1e-3, rel=1e-3
    )
    assert ssim_c(im1, im2, stride=2) == pytest.approx(
        float(ssim_conv_torch(torch.asarray(im1), torch.asarray(im2), stride=2)), abs=1e-3, rel=1e-3
    )


def test_ssim_c_equal_ssim_conv_torch_float64():
    """Test if both ssim methods give the same result."""
    np.random.seed(0)
    im1 = np.random.randn(720, 1080, 3).astype(np.float64)
    im2 = np.random.randn(720, 1080, 3).astype(np.float64)
    assert ssim_c(im1, im2) == pytest.approx(
        float(ssim_conv_torch(torch.asarray(im1), torch.asarray(im2)))
    )
    assert ssim_c(im1, im2, stride=2) == pytest.approx(
        float(ssim_conv_torch(torch.asarray(im1), torch.asarray(im2), stride=2))
    )


def test_ssim_c_equal_ssim_fft_torch_float32():
    """Test if both ssim methods give the same result."""
    np.random.seed(0)
    im1 = np.random.randn(720, 1080, 3).astype(np.float32)
    im2 = np.random.randn(720, 1080, 3).astype(np.float32)
    assert ssim_c(im1, im2) == pytest.approx(
        float(ssim_fft_torch(torch.asarray(im1), torch.asarray(im2))), abs=1e-3, rel=1e-3
    )


def test_ssim_c_equal_ssim_fft_torch_float64():
    """Test if both ssim methods give the same result."""
    np.random.seed(0)
    im1 = np.random.randn(720, 1080, 3).astype(np.float64)
    im2 = np.random.randn(720, 1080, 3).astype(np.float64)
    assert ssim_c(im1, im2) == pytest.approx(
        float(ssim_fft_torch(torch.asarray(im1), torch.asarray(im2))), abs=1e-3, rel=1e-3
    )


@pytest.mark.slow
def test_perf_psnr():
    """Ensure C version if faster than the naive one."""
    for shape in [(480, 720, 3), (720, 1280, 3), (1080, 1920, 3), (2160, 3840, 3)]:
        im1 = np.random.randn(*shape).astype(np.float32)
        im2 = np.random.randn(*shape).astype(np.float32)
        rep = (200 * 2160 * 3840) // (shape[0] * shape[1])
        t_c = np.median(timeit.repeat(
            lambda: psnr_c(im1, im2), repeat=rep, number=1  # pylint: disable=W0640
        ))
        im1, im2 = torch.asarray(im1), torch.asarray(im2)
        t_naive = np.median(timeit.repeat(
            lambda: psnr_torch(im1, im2), repeat=rep, number=1  # pylint: disable=W0640
        ))
        print(
            f"naive:{1000*t_naive:.2f}ms vs c:{1000*t_c:.2f}ms ({t_naive/t_c:.2f} x faster)"
            f" for the shape {shape[1]}x{shape[0]}"
        )
        assert t_c < t_naive


@pytest.mark.slow
def test_perf_ssim():
    """Ensure C version if faster than the naive one."""
    for shape in [(480, 720, 3), (720, 1280, 3), (1080, 1920, 3), (2160, 3840, 3)]:
        im1 = np.random.randn(*shape).astype(np.float32)
        im2 = np.random.randn(*shape).astype(np.float32)
        rep = (3 * 2160 * 3840) // (shape[0] * shape[1])
        t_c = np.median(timeit.repeat(
            lambda: ssim_c(im1, im2), repeat=rep, number=1  # pylint: disable=W0640
        ))
        im1, im2 = torch.asarray(im1), torch.asarray(im2)
        t_naive = np.median(timeit.repeat(
            lambda: ssim_conv_torch(im1, im2),  # pylint: disable=W0640
            repeat=rep, number=1
        ))
        print(
            f"naive:{1000*t_naive:.2f}ms vs c:{1000*t_c:.2f}ms ({t_naive/t_c:.2f} x faster)"
            f" for the shape {shape[1]}x{shape[0]}"
        )
        assert t_c < t_naive
