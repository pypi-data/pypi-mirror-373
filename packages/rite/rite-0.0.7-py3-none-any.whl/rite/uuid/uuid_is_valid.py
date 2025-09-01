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

import json

# Import | Standard Library
import uuid

# Import | Standard Library
from typing import List
from uuid import UUID

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def is_valid_uuid(
    uuid_to_test,
    version=4,
) -> bool:
    """
    Check if uuid_to_test is a valid UUID.

    Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = UUID(
            uuid_to_test,
            version=version,
        )
    except ValueError:
        return False

    answer = str(uuid_obj) == uuid_to_test

    return answer
