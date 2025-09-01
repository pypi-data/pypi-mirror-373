def to_abbreviation_case(text: str) -> str:
    """
    Converts text to its abbreviation.
    Example: 'As Soon As Possible' -> 'ASAP'

    Parameters:
    text (str): The text to abbreviate.

    Returns
    -------
    str: The abbreviation of the text.
    """
    return "".join(word[0].upper() for word in text.split() if word.isalpha())
