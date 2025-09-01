def to_autokey_cipher(text: str, key: str) -> str:
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
        return chr(((ord(c) - 97 + (ord(k) - 97)) % 26) + 97)

    key = key.lower() + text.lower()
    encoded_text = ""

    for i, char in enumerate(text.lower()):
        if char.isalpha():
            encoded_text += char_shift(char, key[i])
        else:
            encoded_text += char

    return encoded_text
