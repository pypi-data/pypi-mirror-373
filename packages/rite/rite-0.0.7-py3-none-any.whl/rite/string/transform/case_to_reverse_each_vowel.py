def to_reverse_each_vowel_case(text: str) -> str:
    """
    Reverses the order of vowels in each word.
    Example: 'Hello' -> 'Holle'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with vowels in each word reversed.
    """
    vowels = "aeiouAEIOU"

    def reverse_vowels(word):
        vowel_list = [char for char in word if char in vowels]
        return "".join(
            vowel_list.pop() if char in vowels else char for char in word
        )

    return " ".join(reverse_vowels(word) for word in text.split())
