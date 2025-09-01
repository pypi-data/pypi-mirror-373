#!/usr/bin/env python3

"""The rules of compilation for setuptools."""

# find . -name "*.so" | xargs rm

import os
import sys

from setuptools import Extension
from setuptools.command.build_py import build_py as _build_py

sys.path.insert(0, os.path.join(os.getcwd(), "cutcutcodec"))  # to avoid cutcutcodec.__init__
from utils import get_compilation_rules, get_project_root


class Build(_build_py):
    """Builder to compile c files."""

    def run(self):
        self.run_command("build_ext")
        return super().run()

    def initialize_options(self):
        super().initialize_options()
        if self.distribution.ext_modules is None:
            self.distribution.ext_modules = []
        rules = get_compilation_rules()
        root = get_project_root()
        for file in (
            file_root / basename for file_root, _, files in root.walk() for basename in files
        ):
            if file.suffix.lower() not in {".cc", ".c", ".c++", ".cp", ".cxx", ".cpp"}:
                continue
            file = file.relative_to(root.parent)
            self.distribution.ext_modules.append(
                Extension(".".join(file.with_suffix("").parts), sources=[str(file)], **rules)
            )
