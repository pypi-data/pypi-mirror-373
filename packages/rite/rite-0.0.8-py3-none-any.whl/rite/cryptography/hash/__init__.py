# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Hash Cryptography Module
===============================

This module provides cryptographic utilities for the Rite application.

"""

# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import List

# Import | Local Modules
from .hash_sha256 import sha256_hash
from .hash_sha512 import sha512_hash

# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "sha256_hash",
    "sha512_hash",
]
