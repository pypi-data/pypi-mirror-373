def to_emoji_case(text: str) -> str:
    """
    Replace certain words with corresponding emojis.
    Note: This is a limited implementation; only a few words are replaced.

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with words replaced by emojis.
    """
    emoji_dict = {
        "love": "❤️",
        "happy": "😊",
        "sad": "😢",
        "dog": "🐶",
        "cat": "🐱",
        "tree": "🌳",
    }
    return " ".join(emoji_dict.get(word, word) for word in text.split())
