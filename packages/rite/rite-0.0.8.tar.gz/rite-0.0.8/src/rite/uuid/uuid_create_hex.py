# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - UUID Module
==================


"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import uuid

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def create_hex_uuid():
    """
    Generates a random UUID and returns it as a 32-character hexadecimal
    string.

    Returns
    -------
        str: UUID as a 32-character hexadecimal string.
    """
    return uuid.uuid4().hex
