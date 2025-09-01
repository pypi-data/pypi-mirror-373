#!/usr/bin/env python3

"""Groups the exceptions specific to ``cutcutcodec``.

Rather than returning too general exceptions, these exceptions allow a much more precise debugging.
"""


class CutcutcodecException(Exception):
    """Base class for exceptions specific to this module."""


class CompilationError(CutcutcodecException, RuntimeError):
    """When a dynamic compilation or execution failed."""


class DecodeError(CutcutcodecException, OSError):
    """When failed to decode a multimedia file or a stream."""


class EncodeError(CutcutcodecException, OSError):
    """When failed to encode a multimedia file or a stream."""


class IncompatibleSettings(CutcutcodecException, RuntimeError):
    """When parameters are incompatible with each other.

    This exception may means that a choice is not possible.
    """


class MissingFrameError(CutcutcodecException, OSError):
    """When a frame is missing in a stream.

    This exception can be thrown if the readed frames have a strange behavior.
    """


class MissingInformation(CutcutcodecException, ValueError):
    """When information is unreadable or missing from the metadata.

    It can be raised when trying to access a tag that is not defined
    or that returns a surprising value.
    """


class MissingStreamError(CutcutcodecException, OSError):
    """When a stream is missing in a file.

    This exception can be raised when looking for a video,
    audio or image stream in a media that does not contain any or that is unreadable.
    """


class OutOfTimeRange(CutcutcodecException, EOFError):
    """Access outside the definition range.

    This exception is raised when accessing or writing
    outside the range in which the stream is defined.
    """
