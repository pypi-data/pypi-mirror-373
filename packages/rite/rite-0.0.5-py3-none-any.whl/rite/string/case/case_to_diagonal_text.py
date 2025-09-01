def to_diagonal_text_case(text: str) -> str:
    """
    Creates a diagonal representation of the text.
    Note: This is a symbolic representation.
    Example: 'Hello' -> 'H\n e\n  l\n   l\n    o'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in a diagonal representation.
    """
    return "\n".join(" " * i + char for i, char in enumerate(text))
