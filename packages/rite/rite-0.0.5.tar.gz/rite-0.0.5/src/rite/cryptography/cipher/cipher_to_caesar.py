def to_caesar_cipher(text: str, shift: int) -> str:
    """
    Encodes the text using a Caesar cipher with a given shift.
    Only alphabetic characters are shifted, others remain unchanged.

    Parameters:
    text (str): The text to encode.
    shift (int): The shift for the Caesar cipher.

    Returns
    -------
    str: The encoded text.
    """
    encoded_text = []
    for char in text:
        if char.isalpha():
            start = 65 if char.isupper() else 97
            encoded_text.append(chr((ord(char) - start + shift) % 26 + start))
        else:
            encoded_text.append(char)
    return "".join(encoded_text)
