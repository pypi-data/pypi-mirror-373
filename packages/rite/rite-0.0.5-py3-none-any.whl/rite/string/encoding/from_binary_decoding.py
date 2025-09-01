def from_binary_decoding(binary_text: str) -> str:
    """
    Decodes binary to text.

    Parameters:
    binary_text (str): The binary text to decode.

    Returns
    -------
    str: The decoded text.
    """
    return "".join(chr(int(binary, 2)) for binary in binary_text.split())
