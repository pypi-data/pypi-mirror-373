# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Bytes - Bytes to String Converter Module
================================================

Provides functionality to convert byte values to human-readable strings.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import List, Union

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Constants
# =============================================================================

# Define byte units (unit, size in bytes)
# BYTES = [
#     ("EB", 1 << 60),
#     ("PB", 1 << 50),
#     ("TB", 1 << 40),
#     ("GB", 1 << 30),
#     ("MB", 1 << 20),
#     ("KB", 1 << 10),
# ]
BYTES = (
    ("PiB", 1125899906842624.0),
    ("TiB", 1099511627776.0),
    ("GiB", 1073741824.0),
    ("MiB", 1048576.0),
    ("KiB", 1024.0),
    ("B", 1.0),
)

# =============================================================================
# Functions
# =============================================================================


def convert_bytes_to_string(
    byte_val: Union[int, float],
    decimals: int = 1,
) -> str:
    """
    Bytes to String Converter
    =========================

    Convert a number of bytes into a human-readable string with appropriate unit.

    Args:
        byte_val: The size in bytes.
        decimals: Number of decimal places to round to (default: 1).

    Returns:
        A human-readable string, e.g. "2.3 MB", "512 KB", or "0 B".

    """
    if not isinstance(byte_val, (int, float)):
        raise TypeError("byte_val must be an int or float")
    if byte_val < 0:
        raise ValueError("byte_val must not be negative")

    for unit, factor in BYTES:
        if byte_val >= factor:
            value = byte_val / factor
            return (
                f"{int(round(value))} {unit}"
                if decimals == 0
                else f"{round(value, decimals)} {unit}"
            )
    return f"{int(byte_val)} B"


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "convert_bytes_to_string",
]


# =============================================================================
# Examples
# =============================================================================

# Example outputs:

# - convert_bytes_to_string(2345678) -> "2.2 MB"
# - convert_bytes_to_string(1234, decimals=0) -> "1 KB"
# - convert_bytes_to_string(0) -> "0 B"
