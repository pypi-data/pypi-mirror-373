def to_xor_cipher(text: str, key: str) -> str:
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
