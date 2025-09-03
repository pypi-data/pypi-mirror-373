# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - List - List to Dictionary Converter Module
==================================================

Provides functionality to convert lists to dictionaries.

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


def convert_list_to_dict(lst):
    """
    Convert List to Dictionary
    ==========================

    Convert a list to a dictionary with list items as keys and empty strings
    as values.

    """
    op = {i: "" for i in lst}
    return op


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "convert_list_to_dict",
]
