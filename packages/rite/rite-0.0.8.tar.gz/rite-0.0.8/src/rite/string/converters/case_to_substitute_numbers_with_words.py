def to_substitute_numbers_with_words_case(text: str) -> str:
    """
    Replaces numbers in the text with their word equivalents.
    Example: 'I have 2 dogs and 3 cats' -> 'I have two dogs and three cats'

    Parameters:
    text (str): The text to process.

    Returns
    -------
    str: The text with numbers replaced by words.
    """
    num_to_word_dict = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
    }
    return " ".join(num_to_word_dict.get(word, word) for word in text.split())
