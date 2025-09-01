def from_playfair_cipher(encoded_text: str, key: str) -> str:
    """
    Decodes text from the Playfair cipher.

    Parameters:
    encoded_text (str): The text to decode.
    key (str): The key for the Playfair cipher.

    Returns
    -------
    str: The decoded text.
    """
    square = Cipher.create_playfair_square(key)
    decoded_text = ""

    for i in range(0, len(encoded_text), 2):
        decoded_text += Cipher.playfair_cipher_pair(
            encoded_text[i : i + 2], square, "decode"
        )

    return decoded_text
