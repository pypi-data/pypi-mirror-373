def to_vowel_concatenation_case(text: str) -> str:
    """
    Concatenates all vowels from the text.
    Example: 'Hello World' -> 'eoo'

    Parameters:
    text (str): The text to process.

    Returns
    -------
    str: A string of all vowels concatenated.
    """
    vowels = "aeiouAEIOU"
    return "".join(char for char in text if char in vowels)
