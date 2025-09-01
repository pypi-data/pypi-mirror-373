def from_scytale_cipher(encoded_text: str, diameter: int) -> str:
    """
    Decodes text from the Scytale cipher.

    Parameters:
    encoded_text (str): The text to decode.
    diameter (int): The diameter used in the Scytale cipher.

    Returns
    -------
    str: The decoded text.
    """
    if diameter <= 0:
        return encoded_text

    num_columns = len(encoded_text) // diameter
    decoded_text = [""] * num_columns

    for i, char in enumerate(encoded_text):
        decoded_text[i // diameter] += char

    return "".join(decoded_text).rstrip()
