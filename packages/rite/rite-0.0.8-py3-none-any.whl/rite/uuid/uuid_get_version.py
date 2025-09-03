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


def get_version(uuid_obj):
    """
    Extracts the version of a UUID.

    Parameters:
        uuid_obj (uuid.UUID): The UUID object.

    Returns
    -------
        int: The version number of the UUID.
    """
    return uuid_obj.version
