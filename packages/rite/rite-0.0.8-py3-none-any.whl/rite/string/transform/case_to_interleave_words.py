def to_interleave_words_case(text1: str, text2: str) -> str:
    """
    Interleaves two different strings word by word.
    Example: ('abc def', 'ghi jkl') -> 'abc ghi def jkl'

    Parameters:
    text1 (str): The first text to interleave.
    text2 (str): The second text to interleave.

    Returns
    -------
    str: The interleaved text.
    """
    words1 = text1.split()
    words2 = text2.split()
    interleaved = [val for pair in zip(words1, words2) for val in pair]
    interleaved.extend(words1[len(words2) :] or words2[len(words1) :])
    return " ".join(interleaved)
