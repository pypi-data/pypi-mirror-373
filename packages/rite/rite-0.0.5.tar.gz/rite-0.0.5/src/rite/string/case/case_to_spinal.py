def to_spinal_case(text: str) -> str:
    """
    Convert the text to spinal case (similar to kebab case).
    Lowers the case of each word and joins them with hyphens.
    Example: 'Hello World' -> 'hello-world'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to spinal case.
    """
    words = text.split()
    return "-".join(word.lower() for word in words)
