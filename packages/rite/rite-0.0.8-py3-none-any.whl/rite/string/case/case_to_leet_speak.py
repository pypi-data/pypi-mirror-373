def to_leet_speak_case(text: str) -> str:
    """
    Convert the text to leet speak (1337) case.
    Example: 'Leet Speak' -> '1337 5p34k'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in leet speak.
    """
    leet_dict = {
        "a": "4",
        "e": "3",
        "l": "1",
        "o": "0",
        "s": "5",
        "t": "7",
        "i": "1",
        "g": "9",
    }
    return "".join(leet_dict.get(char.lower(), char) for char in text)
