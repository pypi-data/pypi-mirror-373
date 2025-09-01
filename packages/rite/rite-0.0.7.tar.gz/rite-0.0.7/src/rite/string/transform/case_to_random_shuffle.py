import random


def to_random_shuffle_case(text: str) -> str:
    """
    Randomly shuffle the letters in each word of the text.
    Example: 'hello' -> 'lleoh' (output may vary)

    Parameters:
    text (str): The text to shuffle.

    Returns
    -------
    str: The text with letters in each word shuffled.
    """

    def shuffle_word(word):
        word_list = list(word)
        random.shuffle(word_list)
        return "".join(word_list)

    return " ".join(shuffle_word(word) for word in text.split())
