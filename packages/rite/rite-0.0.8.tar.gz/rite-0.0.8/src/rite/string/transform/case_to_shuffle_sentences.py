import random


def to_shuffle_sentences_case(text: str) -> str:
    """
    Randomly shuffles the sentences in the text.
    Example: 'This is sentence one. This is sentence two.' -> 'This is
    sentence two. This is sentence one.'

    Parameters:
    text (str): The text to shuffle.

    Returns
    -------
    str: The text with shuffled sentences.
    """
    sentences = text.split(". ")
    random.shuffle(sentences)
    return ". ".join(sentences)
