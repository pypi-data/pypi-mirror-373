# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Autokey Cipher Module
===========================================

Provides functionality to encode and decode text using the Autokey cipher.

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


def encode_autokey_cipher(
    text: str,
    key: str,
) -> str:
    """
    Encodes text using the Autokey cipher.

    Parameters:
    text (str): The text to encode.
    key (str): The key for the Autokey cipher.

    Returns
    -------
    str: The encoded text.
    """

    def char_shift(c, k):
        """
        Shifts a character 'c' by the value of the key character 'k'.
        """
        return chr(((ord(c) - 97 + (ord(k) - 97)) % 26) + 97)

    key = key.lower() + text.lower()
    encoded_text = ""

    for i, char in enumerate(text.lower()):
        if char.isalpha():
            encoded_text += char_shift(char, key[i])
        else:
            encoded_text += char

    return encoded_text


# =============================================================================


def decode_autokey_cipher(
    encoded_text: str,
    key: str,
) -> str:
    """
    Decodes text from the Autokey cipher.

    Parameters:
    encoded_text (str): The text to decode.
    key (str): The key for the Autokey cipher.

    Returns
    -------
    str: The decoded text.
    """

    def char_shift(c, k):
        return chr(((ord(c) - 97 - (ord(k) - 97)) % 26) + 97)

    key = key.lower()
    decoded_text = ""
    key_index = 0

    for char in encoded_text.lower():
        if char.isalpha():
            decoded_char = char_shift(char, key[key_index])
            decoded_text += decoded_char
            key += decoded_char  # Append the decoded char to the key
            key_index += 1
        else:
            decoded_text += char

    return decoded_text


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_autokey_cipher",
    "encode_autokey_cipher",
]
