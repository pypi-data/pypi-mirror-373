def from_vigenere_cipher(encoded_text: str, key: str) -> str:
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
            )  # noqa E501
        else:
            decoded += encoded_text[i]
    return decoded
