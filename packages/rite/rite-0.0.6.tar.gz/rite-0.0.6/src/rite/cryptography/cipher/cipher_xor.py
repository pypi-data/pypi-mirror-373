# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - XOR Cipher Module
===========================================

Provides functionality to encode and decode text using the XOR cipher.

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


def encode_xor_cipher(
    text: str,
    key: str,
) -> str:
    """
    Encodes and decodes text using the XOR cipher with a key.

    Parameters:
    text (str): The text to encode or decode.
    key (str): The key for the XOR cipher.

    Returns
    -------
    str: The encoded or decoded text.
    """
    return "".join(
        chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text)
    )


def decode_xor_cipher(
    text: str,
    key: str,
) -> str:
    """
    Decodes text using the XOR cipher with a key.

    Parameters:
    text (str): The text to decode.
    key (str): The key for the XOR cipher.

    Returns
    -------
    str: The decoded text.
    """
    return encode_xor_cipher(text, key)


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_xor_cipher",
    "encode_xor_cipher",
]
