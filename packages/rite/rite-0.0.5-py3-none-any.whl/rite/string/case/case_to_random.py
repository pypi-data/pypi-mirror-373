import random


def to_random_case(text: str) -> str:
    """
    Randomly change the case of each character in the text.
    Example: 'Hello World' -> 'hElLO wOrLD'

    Parameters:
    text (str): The text to randomize case.

    Returns
    -------
    str: The text with randomized case.
    """
    return "".join(
        random.choice([char.upper(), char.lower()]) for char in text
    )  # noqa E501
