# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - String - String to Binary Converter Module
=================================================

Provides functionality to convert strings to binary values.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import List

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def convert_string_to_binary(text: str) -> str:
    """
    String to Binary Converter
    ==========================

    Convert the text to binary form.
    Example: 'AB' -> '01000001 01000010'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in binary form.
    """
    return " ".join(format(ord(char), "08b") for char in text)


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "convert_string_to_binary",
]
