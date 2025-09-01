#!/usr/bin/env python3

"""Tools for the Power Spectral Density (PSD) estimation."""

import numbers
import typing
import math

import torch

from .window import alpha_to_band, att_to_alpha, band_to_alpha, dpss


def _compute_psd(
    signal_1: torch.Tensor, signal_2: torch.Tensor, win: torch.Tensor, shift: int, return_std: bool
) -> torch.Tensor:
    """Help welch."""
    assert win.ndim == 1, win.shape
    assert signal_1.shape[-1] >= len(win), "signal to short or window to tall"
    is_autocorr = signal_1 is signal_2  # optimisation to avoid redondant operations
    signal_1 = signal_1.contiguous()
    signal_1 = signal_1.as_strided(  # shape (..., o, m), big ram usage!
        (
            *signal_1.shape[:-1],
            (signal_1.shape[-1] - len(win)) // shift + 1,  # number of slices
            len(win),
        ),
        (*signal_1.stride()[:-1], shift, 1),
    )
    signal_1 = signal_1 * win  # not inplace because blocs was not contiguous
    signal_1 = torch.fft.rfft(signal_1, norm="ortho", dim=-1)  # norm ortho for perceval theorem
    if not is_autocorr:
        signal_2 = signal_2.contiguous()
        signal_2 = signal_2.as_strided(  # shape (..., o, m), big ram usage!
            (
                *signal_2.shape[:-1],
                (signal_2.shape[-1] - len(win)) // shift + 1,  # number of slices
                len(win),
            ),
            (*signal_2.stride()[:-1], shift, 1),
        )
        signal_2 = signal_2 * win
        signal_2 = torch.fft.rfft(signal_2, norm="ortho", dim=-1)
        psd = signal_1 * signal_2.conj()
    else:
        psd = signal_1.real*signal_1.real + signal_1.imag*signal_1.imag
    win_power = (win**2).mean()
    if return_std:
        std, psd = torch.std_mean(psd, dim=-2)  # shape (..., m)
        std /= win_power
        psd /= win_power
        return abs(std), psd
    psd = torch.mean(psd, dim=-2)  # shape (..., m)
    psd /= win_power
    return psd


def _find_len(s_x: float, sigma_max: float, psd_max: float, freq_res: float) -> float:
    s_w_min, s_w_max = 3.0, 65536.0
    for _ in range(16):  # dichotomy, resol = 2**-n
        s_w = 0.5*(s_w_min + s_w_max)
        eta = sigma_max * math.sqrt(s_w/s_x) / psd_max
        att = max(20.0, -20.0*math.log10(eta))  # 20 is a minimal acceptable attenuation
        value = s_w*freq_res - 2.0 * alpha_to_band(att_to_alpha(att)) - 1.0
        if value <= 0:
            s_w_min = s_w
        else:
            s_w_max = s_w
    return s_w


def welch(
    signal_1: torch.Tensor,
    signal_2: typing.Optional[torch.Tensor] = None,
    freq_res: typing.Optional[numbers.Real] = None,
) -> torch.Tensor:
    r"""Estimate the power spectral density (PSD) ie intercorrelation with the Welch method.

    Terminology
    -----------
    * :math:`x_1` and :math:`x_2` are the signal whose we want to estimate the intercorrelation.
    * :math:`s_x` is the number of samples in the signal.
    * :math:`s_w` is the number of samples in the dpss window.
    * :math:`r` is the normalize frequency resolution in Hz, for a sample rate of 1.
    * :math:`\Sigma(f)` is an estimation of the standard deviation of the psd.
    * :math:`\Gamma_{x_1,x_2}(f) = psd(f)` is the power spectral density or the intercorrelation.
    * :math:`n_{psd}(f)` is the psd noise, ignoring gibbs effects.
    * :math:`n_{win}` is the additive noise created by the gibbs effect of the window.
    * :math:`\eta` is the maximum amplitude of the largest of the window's secondary lobs.
    * :math:`\alpha` is the window theorical standardized half bandwidth.
    * :math:`\beta` is the window experimental standardized half bandwidth.

    Equations
    ---------
    There, the equation to find the optimal windows size:

    .. math::

        \begin{cases}
            n_{psd}(f) = \Sigma(f) . \sqrt{\frac{s_w}{s_x}} & \text{std of mean estimator} \\
            n_{win} = \max\left(\Gamma_{x_1,x_2}(f)\right) . \eta & \text{because convolution}\\
            \eta = g(\alpha) \\
            \beta = \alpha + \epsilon = h(\alpha) \\
            r = \frac{1}{s_w} + 2 . \frac{\beta}{s_w} & \text{convolution main lob} \\
        \end{cases}

    To avoid having a too big gibbs noise, we want :math:`n_{win} < n_{psd}(f)`.

    .. math::

        \Leftrightarrow \begin{cases}
            psd_{max} . \eta  < \Sigma_{max} . \sqrt{\frac{s_w}{s_x}} \\
            r . s_w = 1 + 2.h(g^{-1}(\eta)) \\
        \end{cases} \Leftrightarrow
            s_w . r - 2 . h\left(
                g^{-1}\left(\frac{\Sigma_{max} . \sqrt{\frac{s_w}{s_x}}}{psd_{max}}\right)
            \right) - 1 > 0


    Parameters
    ----------
    signal_1 : torch.Tensor
        The stationary signal $x_1$ on witch we evaluate the PSD.
        The tensor can be batched, so the shape is (..., n).
    signal_2 : torch.Tensor, default=signal_1
        If you prefer to compute an intercorrelation rather an autocorrelation,
        please provide it (:math:`x_2`), otherwise, :math:`x_2 = x_1`.
    freq_res : float
        The normlised frequency resolution in Hz
        :math:`\left(r \in \left]0, \frac{1}{2}\right[\right)`, for a sample rate of 1.
        Higher it is, better is the frequency resolution but noiser it is.

    Returns
    -------
    psd : torch.Tensor
        An estimation of the power spectral density :math:`\Gamma_{x_1,x_2}(f)`, of shape (..., m).
        Ie an estimation of :math:`\mathbb{E}\left[X_1(f)X_2^x(f)\right]`.
        In the case of autocorrelation, psd is returned as float type,
        overwise (in case of intercorrelation), it is returned as complex.

    Notes
    -----
    The complexity is :math:`O\left(\frac{s_x}{r}\right)`.

    Examples
    --------
    >>> import torch
    >>> from cutcutcodec.core.signal.psd import welch
    >>> sr, delta_t = 8000, 60  # sample rate in (Hz) and duration in (s)
    >>> t = torch.arange(0, delta_t, 1/sr)  # timae smaple in (s)
    >>> signal = torch.randn((16, 2, len(t))) + torch.sin(2*torch.pi*440*t)  # 16 stereo signals
    >>> psd = welch(signal, freq_res=20.0/sr)  # band of 20 Hz
    >>>
    >>> # we should observe a background at 1 and a pic a 440 Hz.
    >>> # import matplotlib.pyplot as plt
    >>> # freq = torch.fft.rfftfreq(2*psd.shape[-1]-1, 1/sr)
    >>> # _ = plt.plot(freq, psd[0].T)
    >>> # _ = plt.xlabel("freq (Hz)")
    >>> # _ = plt.ylabel("psd")
    >>> # plt.show()
    >>>
    """
    assert isinstance(signal_1, torch.Tensor), signal_1.__class__.__name__
    assert signal_1.ndim >= 1
    assert signal_1.shape[-1] >= 32, "the signal is to short, please provide more samples"
    if signal_2 is not None:
        assert isinstance(signal_2, torch.Tensor), signal_2.__class__.__name__
        assert signal_2.ndim >= 1
        assert signal_2.shape[-1] == signal_1.shape[-1], (signal_2.shape, signal_1.shape)
        signal_2 = signal_2.to(dtype=signal_1.dtype, device=signal_1.device)
    else:
        signal_2 = signal_1

    # The first step consists in having a fast and inaccurate estimation of the psd.
    win_len = min(4096, signal_1.shape[-1]//3)
    win = torch.hann_window(win_len, periodic=False, dtype=signal_1.dtype, device=signal_1.device)
    std, psd = _compute_psd(signal_1, signal_2, win, win_len//2, return_std=True)

    # Get a frequency resolution.
    if freq_res is None:
        freq_res = max(1.0/win_len, 10.0/48000)  # simple heuristic
    else:
        assert isinstance(freq_res, numbers.Real), freq_res.__class__.__name__
        assert 0 < freq_res < 0.5, freq_res
        freq_res = float(freq_res)

    # The second step constists in finding the best windows size.
    # According to the inequality specified in the docstring.
    win_len = math.ceil(
        _find_len(signal_1.shape[-1], float(std.max()), float(abs(psd).max()), freq_res)
    )
    win_len = min(win_len, signal_1.shape[-1])

    # The fird step consists in deducing alpha
    # according the frequency accuracy expression in the doctring.
    alpha = band_to_alpha(0.5 * (freq_res * win_len - 1))

    # compute the psd
    win = dpss(win_len, alpha, dtype=signal_1.dtype)
    psd = _compute_psd(signal_1, signal_2, win, win_len//4, return_std=False)  # //4 for overlapp

    return psd
