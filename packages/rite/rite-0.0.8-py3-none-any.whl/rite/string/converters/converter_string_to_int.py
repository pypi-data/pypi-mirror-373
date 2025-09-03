# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - String - String to Int Converter Module
==============================================

Provides functionality to convert strings to integer values.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import List, Optional

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def convert_string_to_int(val: str) -> Optional[int]:
    """
    Convert a string representation of an integer value to an integer.
    """

    val = (val or "").strip()

    if val == "":
        return None

    try:
        return int(val)

    except ValueError:
        return None


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "convert_string_to_int",
]
