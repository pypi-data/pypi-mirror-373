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


def create_string_uuid():
    """
    Generates a random UUID and returns it as a string in standard form.

    Returns
    -------
        str: UUID as a string in standard form.
    """
    return str(uuid.uuid4())
