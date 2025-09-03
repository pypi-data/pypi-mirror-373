def to_nato_phonetic_alphabet_case(text: str) -> str:
    """
    Translates each letter to its corresponding NATO phonetic alphabet
    word.
    Example: 'AB' -> 'Alpha Bravo'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in NATO phonetic alphabet.
    """
    nato_dict = {
        "A": "Alpha",
        "B": "Bravo",
        "C": "Charlie",
        "D": "Delta",
        "E": "Echo",
        "F": "Foxtrot",
        "G": "Golf",
        "H": "Hotel",
        "I": "India",
        "J": "Juliett",
        "K": "Kilo",
        "L": "Lima",
        "M": "Mike",
        "N": "November",
        "O": "Oscar",
        "P": "Papa",
        "Q": "Quebec",
        "R": "Romeo",
        "S": "Sierra",
        "T": "Tango",
        "U": "Uniform",
        "V": "Victor",
        "W": "Whiskey",
        "X": "X-ray",
        "Y": "Yankee",
        "Z": "Zulu",
        " ": " ",
    }
    return " ".join(nato_dict.get(char.upper(), "") for char in text)
