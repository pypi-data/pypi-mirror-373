def to_pig_latin_case(text: str) -> str:
    """
    Translates text into Pig Latin.
    Example: 'hello' -> 'ellohay'

    Parameters:
    text (str): The text to translate.

    Returns
    -------
    str: The text in Pig Latin.
    """

    def convert_word(word):
        if word[0] in "aeiou":
            return word + "way"
        return word[1:] + word[0] + "ay"

    return " ".join(convert_word(word) for word in text.split())
