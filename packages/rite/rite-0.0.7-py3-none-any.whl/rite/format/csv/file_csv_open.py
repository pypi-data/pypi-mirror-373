# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Open CSV File Module
===========================

This module provides utilities for CSV file handling and manipulation.

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


def open_csv(path_or_resource):
    """
    Open a CSV file for reading.
    """
    if hasattr(path_or_resource, "open"):
        return path_or_resource.open("r", newline="", encoding="utf-8")
    return open(path_or_resource, "r", newline="", encoding="utf-8")


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "open_csv",
]
