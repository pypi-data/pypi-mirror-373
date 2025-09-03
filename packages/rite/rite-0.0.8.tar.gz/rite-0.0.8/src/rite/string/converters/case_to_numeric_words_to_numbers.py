def to_numeric_words_to_numbers_case(text: str) -> str:
    """
    Converts numeric words to their numeral equivalents.
    Example: 'one two three' -> '1 2 3'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with numeric words converted to numbers.
    """
    num_dict = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "zero": "0",
    }
    return " ".join(num_dict.get(word, word) for word in text.split())
