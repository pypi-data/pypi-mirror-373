def to_vigenere_cipher(text: str, key: str) -> str:
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
            )  # noqa E501
        else:
            encoded += text[i]
    return encoded
