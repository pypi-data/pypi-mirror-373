#!/usr/bin/env python3

r"""Manage color spaces.

Let try the `online demo app <https://cutcutcodec-colorspace.streamlit.app>`_!

.. math::

    \begin{pmatrix} y' \\ p_b \\ p_r \end{pmatrix}_{p,t}
    \overset{T_1}\longleftrightarrow
    \begin{pmatrix} r' \\ g' \\ b' \end{pmatrix}_{p,t}
    \overset{T_2}\longleftrightarrow
    \begin{pmatrix} r \\ g \\ b \end{pmatrix}_{p}
    \overset{T_3}\longleftrightarrow
    \begin{pmatrix} x \\ y \\ z \end{pmatrix}

With:
    * :math:`p` is the color primaries (gamut), tristimulus values defined in the cst module
      :py:mod:`cutcutcodec.core.colorspace.cst` as the `PRIMARIES` constant.
    * :math:`t` is the transfere function (gamma), defined in the cst module
      :py:mod:`cutcutcodec.core.colorspace.cst` as the `TRC` constant.
    * :math:`\begin{pmatrix} y' \\ p_b \\ p_r \end{pmatrix}_{p,t}`
      is the color space in which video is encoded in `yuv` pixel format.
      :math:`y' \in [0, 1]` is the luma,
      :math:`p_b \in \left[-\frac{1}{2}, \frac{1}{2}\right]` the blue difference and
      :math:`p_r \in \left[-\frac{1}{2}, \frac{1}{2}\right]` the red difference.
      As the human eye perceives differences in luminosity
      better in dark values than in bright ones,
      :math:`y'` stretches low values in order to encode dark pixels more accurately
      The :math:`u` and :math:`v` values encode chrominance,
      which is less important than luminance for the human eye.
      So they are encoded with fewer bits than :math:`y'`
    * :math:`\begin{pmatrix} r' \\ g' \\ b' \end{pmatrix}_{p,t}`
      is the gamma corrected color space expected by terminals (screen, TV, printer, etc...).
      For example, this is the space expected by matplotlib's imshow function.
      :math:`r' \in [0, 1]` is the non-linear red,
      :math:`g' \in [0, 1]` the non-linear green and
      :math:`b' \in [0, 1]` the non-linear blue.
      As this space depends on a primaries :math:`p` and a transfer function :math:`t`,
      we have to choose the one expected by the terminal to obtain a faithful color representation.
    * :math:`\begin{pmatrix} r \\ g \\ b \end{pmatrix}_{p}`
      is the linear workspace in which all cutcutcodec operations are performed.
      :math:`r \in [0, 1]` is the linear red,
      :math:`g \in [0, 1]` the linear green and
      :math:`b \in [0, 1]` the linear blue.
      Unlike the non-linear rgb space, color mixing (and many other physics laws)
      are correct in this space only.
    * :math:`\begin{pmatrix} x \\ y \\ z \end{pmatrix}_{p}`
      is the absolute CIE 1931 reference space, independent of
      any transfer function :math:`t` and any primaries :math:`p`.
      As soon as you change your transfer function or color primaries, you pass through this space.
      :math:`(x, y, z) \in \mathbb{R}^3`
    * :math:`T_1` is a linear transformation that depends on the primaries :math:`p`,
      implemented in :py:func:`cutcutcodec.core.colorspace.func.rgb2yuv_matrix_from_kr_kb`.
    * :math:`T_2` is the transformation that applies the non-linear
      transfer function :math:`t` to each red, green and blue component.
    * :math:`T_3` is a linear transformation that depends on the primaries :math:`p`,
      implemented in :py:func:`cutcutcodec.core.colorspace.func.rgb2xyz_matrix_from_chroma`.

Here are some other sources that talk about color spaces:

    * The `ITU-T H.273 (V4) <https://www.itu.int/rec/T-REC-H.273-202407-I/en>`_ report.
    * The `brucelinbloom <http://www.brucelindbloom.com/index.html>`_ website.
    * The `linux kernel
      <https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/colorspaces-details.html>`_
      documentation.
    * The `colour-science <https://www.colour-science.org>`_ python module.
    * The ffmpeg
      `zscale <https://github.com/sekrit-twc/zimg/blob/master/src/zimg/colorspace>`_ filter.
    * The `REC <https://everything.explained.today/contents/list_REC.htm>`_ website.
    * The `colorspace-routines <https://github.com/m13253/colorspace-routines>`_ python module.

And here's a list of color calculators:

    * The `brucelinbloom <http://www.brucelindbloom.com/index.html?ColorCalculator.html>`_
      calculator.
    * The `haraldbrendel <https://haraldbrendel.com/colorspacecalculator.html>`_ calculator.
    * On the `colorspaceconverter <https://www.colorspaceconverter.com>`_ website.
    * The `colormine <https://www.colormine.org/convert>`_ partial converter.
    * The `physically based <https://physicallybased.info/tools/color-space-converter>`_ databse.
"""
