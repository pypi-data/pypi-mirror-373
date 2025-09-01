.. rst syntax: https://deusyss.developpez.com/tutoriels/Python/SphinxDoc/
.. version conv: https://peps.python.org/pep-0440/
.. icons: https://specifications.freedesktop.org/icon-naming-spec/latest/ar01s04.html or https://www.pythonguis.com/faq/built-in-qicons-pyqt/
.. pyqtdoc: https://www.riverbankcomputing.com/static/Docs/PyQt6/

.. image:: https://img.shields.io/badge/License-GPL-green.svg
    :alt: [license GPL]
    :target: https://opensource.org/license/gpl-3-0

.. image:: https://img.shields.io/badge/linting-pylint-green
    :alt: [linting: pylint]
    :target: https://github.com/pylint-dev/pylint

.. image:: https://img.shields.io/badge/tests-pass-green
    :alt: [testing]
    :target: https://docs.pytest.org/

.. image:: https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue
    :alt: [versions]
    :target: https://cutcutcodec.readthedocs.io/latest/developer_guide/testing.html

.. image:: https://static.pepy.tech/badge/cutcutcodec
    :alt: [downloads]
    :target: https://www.pepy.tech/projects/cutcutcodec

.. image:: https://readthedocs.org/projects/cutcutcodec/badge/?version=latest
    :alt: [documentation]
    :target: https://cutcutcodec.readthedocs.io/latest

Useful links:
`Binary Installers <https://pypi.org/project/cutcutcodec>`_ |
`Source Repository <https://framagit.org/robinechuca/cutcutcodec>`_ |
`Online Documentation <https://cutcutcodec.readthedocs.io/stable>`_ |


Description
===========

This **video editing software** has been designed for speed and to implement some effects that are hard to find elsewhere.
The kernel is written in python and C, so it's easy to integrate it in your own project.
Although it allows you to fine-tune many parameters, it's smart enough to find the settings that are best suited to your project.

This software is **light**, **fast** and **highly configurable** for the following reasons:

#. Based on `PyAV <https://pyav.org>`_, this software supports an incredible number of formats and codecs.
#. This software allows editing the assembly graph. Compared to a timeline, this representation permits to do everything.
#. A complete test benchmark guarantees an excelent kernel reliability.
#. Powered by `torch <https://pytorch.org>`_ and written in C, this software efficiently exploits the CPU and GPU in order to make it very fast.
#. This software is able to optimize the assembly graph in order to limit calculation waste.
#. The code is parallelised to take advantage of all the CPU threads, making it extremely fast.


Examples
========

There are plenty of `other examples in the documentation <https://cutcutcodec.readthedocs.io/stable/getting_started/tutorial.html>`_!

In the following stupid example, we blink the blue color and we add a red noise on the bottom.

.. code-block:: python

    import cutcutcodec

    SETTINGS = [
        {"encodec": "libsvtav1", "rate": 30, "shape": (480, 720)},
        {"encodec": "libvorbis", "rate": 44100, "bitrate": 128000},  # optional bitrate
    ]

    with cutcutcodec.read("media/video/intro.webm") as container:
        video, audio = container.out_select("video")[0], container.out_select("audio")[0]
        noise = cutcutcodec.generation.video.GeneratorVideoNoise().out_streams[0]
        video = cutcutcodec.filter.video.equation.FilterVideoEquation(
            [video, noise], "r0/2 + r1*(i+1)/2", "g0", "b0*sin(2*pi*0.5*t)"
        ).out_streams[0]
        cutcutcodec.write([video, audio], "/tmp/my_video.webm", streams_settings=SETTINGS)


Features
========

Audio
-----

* General properties
    #. Supports a `large number of channels <https://cutcutcodec.readthedocs.io/stable/build/examples/advanced/multi_channels.html>`_ (mono, stereo, 5.1, 7.1, ...) with all sampeling rate.
    #. Automatic detection of the optimal sample frequency based on shannon theory.
* Generation
    #. `Audio-white-noise <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.generation.audio.noise.html>`_ generation.
    #. Generate any `audio signal from any equation <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.generation.audio.equation.html>`_.
* Filters
    #. `Audio-cutting <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.cut.html>`_, `Audio-translate <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.delay.html>`_ and `Audio-concatenate <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.cat.html>`_.
    #. `Add <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.add.html>`_ multiple tracks.
    #. `Audio arbitrary equation <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.equation.html>`_ on several channels of several tracks. (dynamic volume, mixing, wouawoua, ...)
    #. `Finite Impulse Response <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.fir.html>`_ (FIR) invariant filter. (reverb, equalizer, echo, delay, volume, ...)
    #. `Denoising <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.wiener.html>`_ based on optimal Winer filtering.
    #. Hight quality `anti aliasing <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.audio.resample.html>`_ low pass filter (based on FIR).

Video
-----

* General properties
    #. Unlimited support of all image resolutions. (SD, FULL HD, 4K, 8K, ...)
    #. No limit on fps. (3000/1001 fps, 60 fps, 120 fps, ...)
    #. Automatic detection of the optimal resolution and fps.
    #. Support for the `alpha transparency layer <https://cutcutcodec.readthedocs.io/stable/build/examples/advanced/write_alpha.html>`_.
    #. Floating-point image calculation for greater accuracy.
* Generation
    #. `Video-white-noise <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.generation.video.noise.html>`_ generation.
    #. Generate any `video signal from any equation <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.generation.video.equation.html>`_.
    #. `Mandelbrot fractal <https://cutcutcodec.readthedocs.io/stable/build/examples/advanced/mandelbrot.html>`_ generation.
* Filters
    #. `Video-cutting <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.video.cut.html>`_, `Video-translate <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.video.delay.html>`_ and `Video-concatenate <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.video.cat.html>`_.
    #. `Resize <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.video.resize.html>`_ and crop (high quality, no aliasing).
    #. `Overlaying <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.video.add.html>`_ video tracks (with transparency control).
    #. Apply a `video arbitrary equation <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.filter.video.equation.html>`_ one several video streams.
    #. Fast C and fft differentiable implementation of the ``lpips``, ``psnr``, ``ssim``, ``uvq`` and ``vmaf`` `metrics <https://cutcutcodec.readthedocs.io/stable/build/examples/basic/metrics.html>`_.
    #. All gamut and gamma `colorspace conversion <https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.colorspace.html>`_. (sRGB, BT709, BT2020, ...)
