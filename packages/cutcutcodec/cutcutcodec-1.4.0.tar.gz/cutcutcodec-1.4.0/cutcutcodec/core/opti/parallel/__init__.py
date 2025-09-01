#!/usr/bin/env python3

"""Provide tools for managing multi thread/processing as best a possible."""

from .buffer import map, imap, starmap, starimap  # pylint: disable=W0622

__all__ = ["map", "imap", "starmap", "starimap"]
