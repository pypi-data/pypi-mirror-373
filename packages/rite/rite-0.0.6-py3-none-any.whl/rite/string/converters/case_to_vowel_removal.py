def to_vowel_removal_case(text: str) -> str:
    """
    Remove all vowels from the text.
    Example: 'Hello World' -> 'Hll Wrld'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with all vowels removed.
    """
    vowels = "aeiouAEIOU"
    return "".join(char for char in text if char not in vowels)
