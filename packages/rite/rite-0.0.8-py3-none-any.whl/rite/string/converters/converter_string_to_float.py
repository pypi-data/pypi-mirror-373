# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - String - String to Float Converter Module
==============================================

Provides functionality to convert strings to float values.

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


def convert_string_to_float(val: str) -> Optional[float]:
    """
    Convert a string representation of a float value to a float.
    """

    val = (val or "").strip()

    if val == "":
        return None

    try:
        return float(val)

    except ValueError:
        return None


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "convert_string_to_float",
]
