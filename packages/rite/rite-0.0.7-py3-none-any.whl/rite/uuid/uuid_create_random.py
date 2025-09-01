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


def create_random_uuid():
    """
    Generates a random UUID (UUID4).

    Returns
    -------
        uuid.UUID: A randomly generated UUID.
    """
    return uuid.uuid4()
