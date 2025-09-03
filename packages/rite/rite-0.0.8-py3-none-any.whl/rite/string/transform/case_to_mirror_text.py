def to_mirror_text_case(text: str) -> str:
    """
    Creates a mirrored version of the text.
    Example: 'Hello' -> 'Hello olleH'

    Parameters:
    text (str): The text to mirror.

    Returns
    -------
    str: The mirrored text.
    """
    return text + " " + text[::-1]
