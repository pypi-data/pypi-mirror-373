def create_playfair_square(key: str):
    """
    Create a Playfair square with a given key.
    """
    alphabet = (
        "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J is omitted in traditional Playfair
    )
    key = "".join(sorted(set(key.upper()), key=lambda x: key.index(x)))
    key += "".join([c for c in alphabet if c not in key])
    return [key[i : i + 5] for i in range(0, 25, 5)]
