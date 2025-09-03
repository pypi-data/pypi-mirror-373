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


def is_random_uuid(uuid_obj):
    """
    Checks if the UUID is randomly generated (UUID4).

    Parameters:
        uuid_obj (uuid.UUID): The UUID object.

    Returns
    -------
        bool: True if the UUID is a random UUID, False otherwise.
    """
    return uuid_obj.version == 4
