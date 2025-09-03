def to_numeronym_case(text: str) -> str:
    """
    Converts a word into a numeronym.
    Example: 'Internationalization' -> 'i18n'

    Parameters:
    text (str): The word to convert.

    Returns
    -------
    str: The word converted into a numeronym.
    """
    if len(text) <= 3:
        return text
    return text[0] + str(len(text) - 2) + text[-1]
