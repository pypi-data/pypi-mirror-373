def to_first_letter_of_each_word_case(text: str) -> str:
    """
    Takes the first letter of each word to form a new string.
    Example: 'Hello World' -> 'HW'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: A string formed by the first letter of each word.
    """
    return "".join(word[0] for word in text.split() if word)
