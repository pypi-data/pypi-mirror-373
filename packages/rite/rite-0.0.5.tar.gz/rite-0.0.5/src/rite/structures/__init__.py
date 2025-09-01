# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Data Structures Module
==============================

This module provides data structures and utilities for managing and
processing data within the Rite application.

"""

# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import List

# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = []

from typing import List

from .structure_set_nested import NestedSetStructure  # noqa: F401

# =============================================================================
# Module Exports
# =============================================================================

__all__: List[str] = [
    "NestedSetStructure",
]
