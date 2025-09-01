# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Baconian Cipher Module
============================================

Provides functionality to encode and decode text using the Baconian cipher.

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
# Constants
# =============================================================================

BACON_DICT = {
    "a": "aaaaa",
    "b": "aaaab",
    "c": "aaaba",
    "d": "aaabb",
    "e": "aabaa",
    "f": "aabab",
    "g": "aabba",
    "h": "aabbb",
    "i": "abaaa",
    "j": "abaab",
    "k": "ababa",
    "l": "ababb",
    "m": "abbaa",
    "n": "abbab",
    "o": "abbba",
    "p": "abbbb",
    "q": "baaaa",
    "r": "baaab",
    "s": "baaba",
    "t": "baabb",
    "u": "babaa",
    "v": "babab",
    "w": "babba",
    "x": "babbb",
    "y": "bbaaa",
    "z": "bbaab",
}

# =============================================================================
# Functions
# =============================================================================


def encode_baconian_cipher(
    text: str,
) -> str:
    """
    Encodes text using the Baconian cipher. Non-alphabetic characters are
    ignored.

    Parameters:
    text (str): The text to encode.

    Returns
    -------
    str: The encoded text using the Baconian cipher.
    """

    return "".join(
        BACON_DICT.get(char.lower(), "") for char in text if char.isalpha()
    )


# =============================================================================


def decode_baconian_cipher(encoded_text: str) -> str:
    """
    Decodes text from the Baconian cipher. Assumes the text contains
    only 'a' and 'b'.

    Parameters:
    encoded_text (str): The text to decode.

    Returns
    -------
    str: The decoded text from the Baconian cipher.
    """
    bacon_dict = {
        v: k
        for k, v in encode_baconian_cipher(
            "abcdefghijklmnopqrstuvwxyz"
        ).split()
    }

    return "".join(
        bacon_dict.get(encoded_text[i : i + 5], "")
        for i in range(0, len(encoded_text), 5)
    )


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_baconian_cipher",
    "encode_baconian_cipher",
]
