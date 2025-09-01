#!/usr/bin/env python3

"""Ensures all source files are importable."""

import importlib

from cutcutcodec.utils import get_project_root


def test_import():
    """Recursively browse all files to import them."""
    for filepath in get_project_root().rglob("*.py"):
        importlib.import_module(
            ".".join(
                ("cutcutcodec" / filepath.relative_to(get_project_root()).with_suffix("")).parts
            )
        )
