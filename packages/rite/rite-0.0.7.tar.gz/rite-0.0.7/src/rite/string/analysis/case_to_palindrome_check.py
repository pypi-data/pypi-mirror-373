def to_palindrome_check_case(text: str) -> bool:
    """
    Checks if the text is a palindrome.
    Example: 'racecar' -> True

    Parameters:
    text (str): The text to check.

    Returns
    -------
    bool: True if the text is a palindrome, False otherwise.
    """
    cleaned_text = "".join(char.lower() for char in text if char.isalnum())
    return cleaned_text == cleaned_text[::-1]
