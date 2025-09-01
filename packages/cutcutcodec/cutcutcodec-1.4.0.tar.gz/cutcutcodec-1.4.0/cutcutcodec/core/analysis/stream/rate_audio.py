#!/usr/bin/env python3

"""Smartly choose the framerate of an audio stream."""

from fractions import Fraction
import math
import typing

from sympy.core.add import Add
from sympy.core.function import diff
from sympy.core.mul import Mul
from sympy.core.power import Pow
from sympy.core.symbol import Symbol
from sympy.functions.elementary.trigonometric import cos, sin
from sympy.functions.special.delta_functions import DiracDelta
from sympy.utilities import lambdify
import numpy as np

from cutcutcodec.core.analysis.stream.time_backprop import time_backprop
from cutcutcodec.core.classes.stream_audio import StreamAudio
from cutcutcodec.core.compilation.sympy_to_torch.preprocess import evalf
from cutcutcodec.core.generation.audio.equation import GeneratorAudioEquation
from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG


RATE_ESTIMATORS = {}  # to each node stream class, associate the func to find the optimal rate


def _add_estimator(node_cls: type) -> callable:
    def _add_func(func) -> callable:
        RATE_ESTIMATORS[node_cls] = func
        return func
    return _add_func


def _eq_estimate_freq_max(
    signal, t_symb: Symbol, t_min: Fraction, t_max: Fraction | float
) -> float:
    """Recursive delegation (parallelization is slower)."""
    if t_symb not in signal.free_symbols:  # facultative, optimisation
        return 0.0
    if isinstance(signal, Add):  # fourier transform is linear
        return max(_eq_estimate_freq_max(s, t_symb, t_min, t_max) for s in signal.args)
    if isinstance(signal, Mul):  # fourier transform of prod is convolution, max is sum
        return sum(_eq_estimate_freq_max(s, t_symb, t_min, t_max) for s in signal.args)
    if isinstance(signal, (cos, sin)):
        return _eq_abs_max_expr(
            diff(signal.args[0], t_symb), t_symb, float(t_min), float(t_max)
        ) / (2*math.pi)
    if isinstance(signal, Pow) and signal.exp.is_integer and signal.exp > 0:  # recursive Mul
        return float(signal.exp) * _eq_estimate_freq_max(signal.base, t_symb, t_min, t_max)
    return _eq_estimate_freq_max_by_diff(signal, t_symb, float(t_min), float(t_max))


def _eq_abs_max_expr(expr, t_symb: Symbol, t_min: float, t_max: float) -> float:
    """Search an aproximation of the max with a pseudo dichotomie gradient."""
    if expr.is_number:
        return abs(float(expr))
    if expr.atoms(DiracDelta):
        return math.inf
    func_max_and_diff = lambdify(  # sign(abs(s)') = sign((s**2)') = sign(2*s'*s) = sign(s'*s)
        [t_symb],
        [expr, Mul(diff(expr, t_symb), expr, evaluate=False)],
        modules="numpy",
        cse=True,
    )

    # the initials positions
    t_max = 3600.0 if t_max == math.inf else t_max
    t_0 = np.logspace(0, 3, 512, base=10)  # [1, 1000]
    t_0 *= (t_max-t_min) / 999.0  # [(tmax-t_min)/999, 1000/999*(tmax-t_min)]
    t_0 += (1000.0*t_min - t_max) / 999.0  # [t_min, t_max]
    t_0 = np.concatenate([t_0, np.linspace(t_min, t_max, 1024), (t_min+t_max)-t_0], axis=0)
    t_0.sort(axis=0, kind="quicksort")

    # search the maximums
    old_max = 0
    for i in range(30):  # f > 19200 Hz for delta_t <= 3600 s
        new_max, direction = func_max_and_diff(t_0)
        if not np.isfinite(new_max).any():
            return old_max

        new_max = np.absolute(new_max, out=new_max)
        new_max = np.nanmax(new_max)
        if old_max > new_max:
            return old_max
        old_max = new_max

        direction = np.sign(direction).astype(int)
        direction[0], direction[-1] = max(0, direction[0]), min(0, direction[-1])
        direction += np.arange(len(direction), dtype=int)
        t_0 = (1 - 2**(-1-i))*t_0 + (2**(-1-i))*t_0[direction]

    return old_max


def _eq_estimate_freq_max_by_diff(signal, t_symb: Symbol, t_min: float, t_max: float) -> float:
    """Match the max freq sin by differencials.

    Hypotetical model : signal = s = a*sin(2*pi*f*t)
    <=> s' = 2*pi*a*f*cos(2*pi*f*t) and s''' = -8*pi**3*a*f**3*cos(2*pi*f*t)
    <=> f_max = sqrt(abs(s'**3 * s'''))/(2 * pi * s'**2)
    <=> f_max**2 = abs(-s'''/(4*pi**2*s'))
    <=> 4*pi**2 * f_max**2 = abs(s'''/s')
    """
    # compute the successives differentials
    if signal.is_Atom:  # average 8% faster this test
        return 0
    signal = evalf(signal)  # average 60% faster with this simplification
    max_freq = diff(signal, t_symb)
    max_freq = diff(max_freq, t_symb, 2) / max_freq
    return math.sqrt(_eq_abs_max_expr(max_freq, t_symb, t_min, t_max) / (4*math.pi**2))


@_add_estimator(ContainerInputFFMPEG)
def _optimal_rate_container_input_ffmpeg(stream: StreamAudio, *_) -> int:
    """Detect the rate of a ContainerInputFFMPEG stream.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.stream.rate_audio import optimal_rate_audio
    >>> from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG
    >>> from cutcutcodec.utils import get_project_root
    >>> audio = get_project_root().parent / "media" / "audio" / "narration_5_1.oga"
    >>> (stream,) = ContainerInputFFMPEG(audio).out_streams
    >>> optimal_rate_audio(stream)
    16000
    >>>
    """
    assert isinstance(stream.node, ContainerInputFFMPEG), stream.node.__class__.__name__
    return stream.rate


@_add_estimator(GeneratorAudioEquation)
def _optimal_rate_generator_audio_equation(
    stream: StreamAudio, t_min: Fraction, t_max: Fraction | float
) -> int:
    """Detect the rate of a GeneratorAudioEquation stream.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.stream.rate_audio import optimal_rate_audio
    >>> from cutcutcodec.core.generation.audio.equation import GeneratorAudioEquation
    >>>
    >>> optimal_rate_audio(GeneratorAudioEquation(0).out_streams[0])
    0
    >>> (stream,) = GeneratorAudioEquation("sin(2*pi*440*t)").out_streams
    >>> optimal_rate_audio(stream)
    881
    >>> (stream,) = GeneratorAudioEquation("1/2*cos(2*pi*440*t)").out_streams
    >>> optimal_rate_audio(stream)
    881
    >>> (stream,) = GeneratorAudioEquation("cos(2*pi*440*t)+cos(2*pi*880*t)").out_streams
    >>> optimal_rate_audio(stream)
    1761
    >>> (stream,) = GeneratorAudioEquation("cos(2*pi*440*t)**4").out_streams
    >>> optimal_rate_audio(stream)
    3521
    >>> (stream,) = GeneratorAudioEquation("cos(2*pi*440*t)*cos(2*pi*880*t)").out_streams
    >>> optimal_rate_audio(stream)
    2641
    >>> (stream,) = GeneratorAudioEquation("sin(2*pi*440*exp(-t))").out_streams
    >>> optimal_rate_audio(stream)
    881
    >>> (stream,) = GeneratorAudioEquation("exp(-t**2/(2*1/1000))").out_streams
    >>> optimal_rate_audio(stream)
    192000
    >>> (stream,) = GeneratorAudioEquation("max(-1, min(1, 100*t))").out_streams
    >>> optimal_rate_audio(stream)
    192000
    >>>
    """
    assert isinstance(stream.node, GeneratorAudioEquation), stream.node.__class__.__name__

    t_symb = Symbol("t", real=True, positive=True)
    freq = max(
        _eq_estimate_freq_max(signal, t_symb, t_min, t_max) for signal in stream.node.signals
    )
    if math.isfinite(freq):
        shannon = math.floor(2*freq) + 1 if freq else 0  # shannon strict superior to 2 f_max
        return min(192000, shannon)  # the max supported by some sound cards
    return 192000


@_add_estimator(GeneratorAudioNoise)
def _optimal_rate_generator_audio_noise(stream: StreamAudio, *_) -> int:
    """Detect the rate of a GeneratorAudioNoise stream.

    Examples
    --------
    >>> from cutcutcodec.core.analysis.stream.rate_audio import optimal_rate_audio
    >>> from cutcutcodec.core.generation.audio.noise import GeneratorAudioNoise
    >>> (stream,) = GeneratorAudioNoise(0).out_streams
    >>> optimal_rate_audio(stream)
    48000
    >>>
    """
    assert isinstance(stream.node, GeneratorAudioNoise), stream.node.__class__.__name__
    return 48000


def optimal_rate_audio(
    stream: StreamAudio,
    t_min: typing.Optional[Fraction] = None,
    t_max: typing.Optional[Fraction | float] = None,
) -> int:
    """Find the optimal sampling rate for a given audio stream.

    Parameters
    ----------
    stream : cutcutcodec.core.classes.stream_audio.StreamAudio
        The audio stream that we want to find the optimal rate.
    t_min : float, optional
        The lower bound of the time slice estimation.
    t_max : float, optional
        The higher bound of the time slice estimation.

    Returns
    -------
    framerate : int
        The minimum samplerate that respects the Nyquist–Shannon theorem.
        The special value 0 is returned if not special rate is suggested.
    """
    # verifications
    assert isinstance(stream, StreamAudio), stream.__class__.__name__
    assert t_min is None or isinstance(t_min, Fraction), t_min.__class__.__name__
    assert t_max is None or t_max == math.inf or isinstance(t_max, Fraction), t_max

    # estimation of the best rate
    t_min, t_max = t_min or stream.beginning, t_max or stream.beginning + stream.duration
    if (estimator := RATE_ESTIMATORS.get(stream.node.__class__, None)) is not None:
        return estimator(stream, t_min, t_max)
    return max(
        (
            optimal_rate_audio(s, *t)
            for s, *t in time_backprop(stream, t_min, t_max)
            if s.type == "audio"
        ),
        default=0,
    )
