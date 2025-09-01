def to_mocking_spongebob_case(text: str) -> str:
    """
    Convert the text to 'Mocking Spongebob' case (alternating case).
    Example: 'Hello World' -> 'hElLo wOrLd'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in 'Mocking Spongebob' case.
    """
    return "".join(
        char.lower() if i % 2 else char.upper() for i, char in enumerate(text)
    )  # noqa E501
