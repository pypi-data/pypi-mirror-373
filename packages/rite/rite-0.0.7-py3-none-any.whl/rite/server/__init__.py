# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Server Module
====================

This module provides utilities for server management and communication.

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


from .http import MyHTTPRequestHandler
from .sqlite import SQLiteServer
