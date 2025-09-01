def to_alphabet_position_case(text: str) -> str:
    """
    Replaces each letter with its position in the alphabet.
    Example: 'ab' -> '1 2'

    Parameters:
    text (str): The text to process.

    Returns
    -------
    str: A string with each letter replaced by its alphabet position.
    """
    return " ".join(
        str(ord(char.lower()) - 96) for char in text if char.isalpha()
    )
