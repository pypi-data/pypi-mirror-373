def to_scytale_cipher(text: str, diameter: int) -> str:
    """
    Encodes text using the Scytale cipher.

    Parameters:
    text (str): The text to encode.
    diameter (int): The diameter (number of characters per turn) of the Scytale.

    Returns
    -------
    str: The encoded text.
    """
    if diameter <= 0:
        return text

    padded_text = text + " " * ((diameter - len(text) % diameter) % diameter)
    encoded_text = [""] * diameter

    for i, char in enumerate(padded_text):
        encoded_text[i % diameter] += char

    return "".join(encoded_text)
