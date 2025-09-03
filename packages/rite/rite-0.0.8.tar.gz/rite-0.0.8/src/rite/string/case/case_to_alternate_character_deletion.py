def to_alternate_character_deletion_case(text: str) -> str:
    """
    Deletes every alternate character in the text.
    Example: 'Hello' -> 'Hlo'

    Parameters:
    text (str): The text to process.

    Returns
    -------
    str: The text with every alternate character deleted.
    """
    return text[::2]
