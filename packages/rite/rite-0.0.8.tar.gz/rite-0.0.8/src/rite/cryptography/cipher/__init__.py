# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cipher Cryptography Module
=================================

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
from .cipher_atbash import decode_atbash_cipher, encode_atbash_cipher
from .cipher_autokey import decode_autokey_cipher, encode_autokey_cipher
from .cipher_baconian import decode_baconian_cipher, encode_baconian_cipher
from .cipher_caesar import decode_caesar_cipher, encode_caesar_cipher
from .cipher_four_square import (
    decode_four_square_cipher,
    encode_four_square_cipher,
    four_square_cipher_pair,
)
from .cipher_playfair import decode_playfair_cipher, encode_playfair_cipher
from .cipher_rail_fence import (
    decode_rail_fence_cipher,
    encode_rail_fence_cipher,
)
from .cipher_rot13 import decode_rot13_cipher, encode_rot13_cipher
from .cipher_scytale import decode_scytale_cipher, encode_scytale_cipher
from .cipher_transposition import (
    decode_transposition_cipher,
    encode_transposition_cipher,
)
from .cipher_vigenere import decode_vigenere_cipher, encode_vigenere_cipher
from .cipher_xor import decode_xor_cipher, encode_xor_cipher

# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_atbash_cipher",
    "encode_atbash_cipher",
    "decode_autokey_cipher",
    "encode_autokey_cipher",
    "decode_baconian_cipher",
    "encode_baconian_cipher",
    "decode_caesar_cipher",
    "encode_caesar_cipher",
    "four_square_cipher_pair",
    "encode_four_square_cipher",
    "decode_four_square_cipher",
    "decode_playfair_cipher",
    "encode_playfair_cipher",
    "decode_rail_fence_cipher",
    "encode_rail_fence_cipher",
    "decode_rot13_cipher",
    "encode_rot13_cipher",
    "decode_scytale_cipher",
    "encode_scytale_cipher",
    "decode_transposition_cipher",
    "encode_transposition_cipher",
    "decode_vigenere_cipher",
    "encode_vigenere_cipher",
    "decode_xor_cipher",
    "encode_xor_cipher",
]
