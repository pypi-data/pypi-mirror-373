def from_transposition_cipher(encoded_text: str, key: int) -> str:
    """
    Decodes text from a simple columnar transposition cipher.

    Parameters:
    encoded_text (str): The text to decode.
    key (int): The number of columns.

    Returns
    -------
    str: The decoded text.
    """
    num_rows = len(encoded_text) // key
    remainder = len(encoded_text) % key
    text = [""] * num_rows

    for col in range(key):
        start_index = (num_rows + 1) * min(col, remainder) + num_rows * max(
            0, col - remainder
        )
        end_index = start_index + (
            num_rows + 1 if col < remainder else num_rows
        )
        for row, char in enumerate(encoded_text[start_index:end_index]):
            text[row] += char

    return "".join(text)
