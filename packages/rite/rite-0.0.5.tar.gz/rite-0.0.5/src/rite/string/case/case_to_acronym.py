def to_acronym_case(text: str) -> str:
    """
    Convert a phrase to its acronym.
    Example: 'Random Access Memory' -> 'RAM'

    Parameters:
    text (str): The phrase to convert.

    Returns
    -------
    str: The acronym of the phrase.
    """
    return "".join(word[0].upper() for word in text.split() if word)
