import random


def to_scramble_middle_letters_case(text: str) -> str:
    """
    Scrambles the middle letters of each word, keeping the first and last
    letter intact.
    Example: 'Hello' -> 'Hlelo' (output may vary)

    Parameters:
    text (str): The text to scramble.

    Returns
    -------
    str: The text with middle letters of each word scrambled.
    """

    def scramble_middle(word):
        if len(word) > 3:
            middle = list(word[1:-1])
            random.shuffle(middle)
            return word[0] + "".join(middle) + word[-1]
        return word

    return " ".join(scramble_middle(word) for word in text.split())
