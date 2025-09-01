def to_rainbow_case(text: str) -> str:
    """
    Assigns a different color code to each letter.
    Note: Actual color cannot be represented in plain text; using symbolic
    representation.

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with symbolic color codes.
    """
    colors = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
    return "".join(
        f"{colors[i % len(colors)]}{char}" for i, char in enumerate(text)
    )  # noqa E501
