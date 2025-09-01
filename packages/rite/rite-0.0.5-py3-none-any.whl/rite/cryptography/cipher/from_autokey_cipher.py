def from_autokey_cipher(encoded_text: str, key: str) -> str:
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
