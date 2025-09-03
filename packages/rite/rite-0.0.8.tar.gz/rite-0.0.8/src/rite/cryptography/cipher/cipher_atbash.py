# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Atbash Cipher Module
===========================================

Provides functionality to encode and decode text using the Atbash cipher.

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


def encode_atbash_cipher(
    text: str,
) -> str:
    """
    Encodes and decodes text using the Atbash cipher (reversible).

    Parameters:
    text (str): The text to encode or decode.

    Returns
    -------
    str: The encoded or decoded text.
    """
    return text.translate(
        str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba",
        )
    )


def decode_atbash_cipher(
    text: str,
) -> str:
    """
    Decodes text using the Atbash cipher (reversible).

    Parameters:
    text (str): The text to decode.

    Returns
    -------
    str: The decoded text.
    """
    return encode_atbash_cipher(text)


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "encode_atbash_cipher",
    "decode_atbash_cipher",
]
