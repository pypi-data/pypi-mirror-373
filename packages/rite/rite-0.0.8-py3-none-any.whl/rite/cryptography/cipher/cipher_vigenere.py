# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Vigenère Cipher Module
============================================

Provides functionality to encode and decode text using the Vigenère cipher.

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


def encode_vigenere_cipher(text: str, key: str) -> str:
    """
    Encodes text using the Vigenère cipher.

    Parameters:
    text (str): The text to encode.
    key (str): The keyword used for encoding.

    Returns
    -------
    str: The encoded text.
    """

    key = key.lower()
    key_length = len(key)
    key_as_int = [ord(i) for i in key]
    text_int = [ord(i) for i in text]
    encoded = ""

    for i in range(len(text_int)):
        if text[i].isalpha():
            value = (text_int[i] + key_as_int[i % key_length]) % 26
            encoded += (
                chr(value + 65) if text[i].isupper() else chr(value + 97)
            )
        else:
            encoded += text[i]

    return encoded


# =============================================================================


def decode_vigenere_cipher(encoded_text: str, key: str) -> str:
    """
    Decodes text from the Vigenère cipher.

    Parameters:
    encoded_text (str): The text to decode.
    key (str): The keyword used for encoding.

    Returns
    -------
    str: The decoded text.
    """
    key = key.lower()
    key_length = len(key)
    key_as_int = [ord(i) for i in key]
    text_int = [ord(i) for i in encoded_text]
    decoded = ""

    for i in range(len(text_int)):
        if encoded_text[i].isalpha():
            value = (text_int[i] - key_as_int[i % key_length]) % 26
            decoded += (
                chr(value + 65)
                if encoded_text[i].isupper()
                else chr(value + 97)
            )
        else:
            decoded += encoded_text[i]

    return decoded


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_vigenere_cipher",
    "encode_vigenere_cipher",
]
