# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - File - File Size to String Converter Module
==================================================

Provides functionality to convert file sizes to human-readable strings.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import BinaryIO, List, Union

from rite.data.bytes.converter_bytes_to_string import convert_bytes_to_string

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def file_size_to_string(
    filehandle: Union[BinaryIO, object],
) -> str:
    """
    Return the size of a file in a human-readable string.

    Attempts to use `filehandle.size` if available (e.g. Django's UploadedFile),
    otherwise seeks to the end to determine size.

    Args:
        filehandle: A file-like object.

    Returns:
        A string representing the file size, e.g., '2.4 MB', '1 KB'.
    """
    if hasattr(filehandle, "size"):
        return convert_bytes_to_string(filehandle.size)

    try:
        current_position = filehandle.tell()
        filehandle.seek(0, 2)  # Move to end
        size = filehandle.tell()
        filehandle.seek(current_position)  # Reset to original position
        return convert_bytes_to_string(size)
    except (AttributeError, OSError):
        return "Unknown size"


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "file_size_to_string",
]
