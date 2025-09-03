from collections import Counter


def to_character_frequency_count_case(text: str) -> dict:
    """
    Counts the frequency of each character in the text.
    Example: 'hello' -> {'h': 1, 'e': 1, 'l': 2, 'o': 1}

    Parameters:
    text (str): The text to analyze.

    Returns
    -------
    dict: A dictionary with the frequency count of each character.
    """
    return dict(Counter(text))
