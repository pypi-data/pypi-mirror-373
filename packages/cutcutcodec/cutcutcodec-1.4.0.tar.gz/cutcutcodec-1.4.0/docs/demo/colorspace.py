#!/usr/bin/env python3

"""Colorspace demo code with streamlit."""

import pathlib
import re
import tempfile

import cutcutcodec
import streamlit as st
import sympy


def draw_header():
    """Display the header."""
    st.markdown(
        """
        ## Colorspace Converter

        This app shows how to model and convert different colorspaces using the
        [`cutcutcodec`](https://cutcutcodec.readthedocs.io/stable/build/api/cutcutcodec.core.colorspace.html) library.
        """
    )
    st.latex(
        r"""
        \begin{pmatrix} y' \\ p_b \\ p_r \end{pmatrix}_{p,t}
        \overset{T_1}\longleftrightarrow
        \begin{pmatrix} r' \\ g' \\ b' \end{pmatrix}_{p,t}
        \overset{T_2}\longleftrightarrow
        \begin{pmatrix} r \\ g \\ b \end{pmatrix}_{p}
        \overset{T_3}\longleftrightarrow
        \begin{pmatrix} x \\ y \\ z \end{pmatrix}
        """
    )


def conf_selector() -> tuple[cutcutcodec.Colorspace, cutcutcodec.Colorspace]:
    """Create the widgets to choose the colorspace conversion path."""
    col1, col2 = st.columns(2)
    with col1:
        src_space = st.selectbox("source space", cutcutcodec.core.colorspace.cst.SYMBS)
        src_prim = st.selectbox(
            "source primaries",
            sorted(cutcutcodec.core.colorspace.cst.PRIMARIES),
            disabled=(src_space in {"xyz"}),
            index=sorted(cutcutcodec.core.colorspace.cst.PRIMARIES).index("bt2020"),
        )
        src_trc = st.selectbox(
            "source transfer",
            sorted(cutcutcodec.core.colorspace.cst.TRC),
            disabled=(src_space in {"rgb", "xyz"}),
            index=sorted(cutcutcodec.core.colorspace.cst.TRC).index("smpte2084"),
        )
    with col2:
        dst_space = st.selectbox("target space", cutcutcodec.core.colorspace.cst.SYMBS)
        dst_prim = st.selectbox(
            "target primaries",
            sorted(cutcutcodec.core.colorspace.cst.PRIMARIES),
            disabled=(dst_space in {"xyz"}),
            index=sorted(cutcutcodec.core.colorspace.cst.PRIMARIES).index("bt709"),
        )
        dst_trc = st.selectbox(
            "target transfer",
            sorted(cutcutcodec.core.colorspace.cst.TRC),
            disabled=(dst_space in {"rgb", "xyz"}),
            index=sorted(cutcutcodec.core.colorspace.cst.TRC).index("srgb"),
        )
    src_colorspace = cutcutcodec.Colorspace(src_space, src_prim, src_trc)
    dst_colorspace = cutcutcodec.Colorspace(dst_space, dst_prim, dst_trc)
    return src_colorspace, dst_colorspace


def show_equation(src: cutcutcodec.Colorspace, dst: cutcutcodec.Colorspace):
    """Create the options to show the equations."""
    if st.checkbox("Display equations in LaTeX", value=False):
        equation = src.to_equation(dst)
        st.latex(
            f"{cutcutcodec.core.colorspace.cst.SYMBS[dst.space][0]} = {sympy.latex(equation[0])}",
            width="content",
        )
        st.latex(
            f"{cutcutcodec.core.colorspace.cst.SYMBS[dst.space][1]} = {sympy.latex(equation[1])}",
            width="content",
        )
        st.latex(
            f"{cutcutcodec.core.colorspace.cst.SYMBS[dst.space][2]} = {sympy.latex(equation[2])}",
            width="content",
        )


def show_pseudo_code(src_colorspace: cutcutcodec.Colorspace, dst_colorspace: cutcutcodec.Colorspace):
    """Create the options to show the CSE equation as pseudo code."""
    if st.checkbox("Show the pseudo code", value=False):
        code = str(src_colorspace.to_function(dst_colorspace))
        st.latex(code)


def show_c(src_colorspace: cutcutcodec.Colorspace, dst_colorspace: cutcutcodec.Colorspace):
    """Create the options to show the c code."""
    if st.checkbox("Show the C code", value=False):
        code = src_colorspace.to_function(dst_colorspace)._tree["dyn_code"]
        st.code(code, language="c")


def num_selector(src: cutcutcodec.Colorspace, dst: cutcutcodec.Colorspace):
    """Numerical value setter."""
    space_to_comp = {
        "y'pbpr": ["luma", "blue-diff", "red-diff"],
        "r'g'b'": ["corrected red", "corrected green", "corrected blue"],
        "rgb": ["linear red", "linear green", "linear blue"],
        "xyz": ["x", "y", "z"]
    }
    space_to_born = {
        "y'pbpr": [(0.0, 1.0), (-0.5, 0.5), (-0.5, 0.5)],
        "r'g'b'": [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)],
        "rgb": [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)],
        "xyz": [(None, None), (None, None), (None, None)],
    }
    col1, col2 = st.columns(2)

    with col1:
        comp_src = [
            st.number_input(
                (
                    f"input {space_to_comp[src.space][0]} "
                    f"({cutcutcodec.core.colorspace.cst.SYMBS[src.space][0]})"
                ),
                key="comp_src_0",
                min_value=space_to_born[src.space][0][0],
                max_value=space_to_born[src.space][0][1],
                value=0.5*sum(space_to_born[src.space][0]),
                step=1e-6,
            ),
            st.number_input(
                (
                    f"input {space_to_comp[src.space][1]} "
                    f"({cutcutcodec.core.colorspace.cst.SYMBS[src.space][1]})"
                ),
                key="comp_src_1",
                min_value=space_to_born[src.space][1][0],
                max_value=space_to_born[src.space][1][1],
                value=0.5*sum(space_to_born[src.space][1]),
                step=1e-6,
            ),
            st.number_input(
                (
                    f"input {space_to_comp[src.space][2]} "
                    f"({cutcutcodec.core.colorspace.cst.SYMBS[src.space][2]})"
                ),
                key="comp_src_2",
                min_value=space_to_born[src.space][2][0],
                max_value=space_to_born[src.space][2][1],
                value=0.5*sum(space_to_born[src.space][2]),
                step=1e-6,
            ),
        ]

    equation = src.to_equation(dst)
    with col2:
        label = (
            f"output {space_to_comp[dst.space][0]} "
            f"({cutcutcodec.core.colorspace.cst.SYMBS[dst.space][0]})"
        )
        result = equation[0].subs(
            dict(zip(cutcutcodec.core.colorspace.cst.SYMBS[src.space], comp_src))
        ).evalf(37)
        result = re.sub(r"(\d)0+$", r"\1", f"{result:.37f}")
        st.code(f"{label}:\n{result}", language="text")
        label = (
            f"output {space_to_comp[dst.space][1]} "
            f"({cutcutcodec.core.colorspace.cst.SYMBS[dst.space][1]})"
        )
        result = equation[1].subs(
            dict(zip(cutcutcodec.core.colorspace.cst.SYMBS[src.space], comp_src))
        ).evalf(37)
        result = re.sub(r"(\d)0+$", r"\1", f"{result:.37f}")
        st.code(f"{label}:\n{result}", language="text")
        label = (
            f"output {space_to_comp[dst.space][2]} "
            f"({cutcutcodec.core.colorspace.cst.SYMBS[dst.space][2]})"
        )
        result = equation[2].subs(
            dict(zip(cutcutcodec.core.colorspace.cst.SYMBS[src.space], comp_src))
        ).evalf(37)
        result = re.sub(r"(\d)0+$", r"\1", f"{result:.37f}")
        st.code(f"{label}:\n{result}", language="text")


def show_python_conv_code(dst: cutcutcodec.Colorspace):
    """Display the python code to convert a video."""
    st.code(
        "\n".join([
            "#!/usr/bin/env python3",
            "",
            '"""Change the colorspace of a video."""',
            "",
            "import cutcutcodec",
            "",
            f"with cutcutcodec.read({'media/video/intro.webm'!r}) as container:  # open the file",
            '    stream = container.out_select("video")[0]  # take the first video stream',
            '    cutcutcodec.write(',
            '        [stream],',
            '        "/tmp/my_video.mp4",  # converted video',
            f"        colorspace=cutcutcodec.{dst},",
            '        streams_settings=[{"encodec": "libx264", "options": {"crf": "23", "preset": "fast"}}],',
            '    )',
        ]),
        language="python",
    )


def main():
    """Call the full loop."""
    draw_header()
    st.markdown("### Set configuration")
    src_colorspace, dst_colorspace = conf_selector()
    st.markdown("### Symbolic equations")
    show_equation(src_colorspace, dst_colorspace)
    show_pseudo_code(src_colorspace, dst_colorspace)
    st.markdown("### Numerical simulator")
    show_c(src_colorspace, dst_colorspace)
    num_selector(src_colorspace, dst_colorspace)
    st.markdown("### Video converter")
    show_python_conv_code(dst_colorspace)


# if dst_space == "y'pbpr":
#     uploaded_file = st.file_uploader(
#         "Choose a video to convert",
#         accept_multiple_files=False,
#         type=cutcutcodec.core.io.cst.VIDEO_SUFFIXES,
#     )
#     if uploaded_file is not None:
#         src = pathlib.Path(tempfile.gettempdir()) / uploaded_file.name
#         with open(src, "wb") as raw:
#             raw.write(uploaded_file.read())
#         dst = src.with_name("converted.mp4")

#         with cutcutcodec.read(src) as container:
#             stream = container.out_select("video")[0]
#             cutcutcodec.write(
#                 [stream],
#                 dst,
#                 colorspace=cutcutcodec.Colorspace(dst_space, dst_prim, dst_trc),
#                 streams_settings=[{"encodec": "libx264", "options": {"crf": "23", "preset": "fast"}}],
#             )

#         src.unlink()
#         st.success("Conversion terminate!")
#         st.download_button("Download", open(dst, "rb"), file_name=dst.name)

if __name__ == "__main__":
    main()
