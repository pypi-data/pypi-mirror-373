import random


def to_zalgo_text_case(text: str) -> str:
    """
    Add a glitch-like effect to the text with Zalgo characters.
    Note: This is a simplified version for demonstration.

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with Zalgo effect.
    """
    zalgo_chars = [chr(i) for i in range(0x0300, 0x036F)]
    return "".join(
        char + "".join(random.choices(zalgo_chars, k=2)) for char in text
    )  # noqa E501
