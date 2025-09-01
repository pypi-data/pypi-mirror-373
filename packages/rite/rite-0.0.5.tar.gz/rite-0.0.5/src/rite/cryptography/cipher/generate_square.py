def generate_square(key: str):
    """
    Generate a 5x5 matrix for the Four-Square cipher using a key.
    """
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # Typically J is omitted
    key = "".join(sorted(set(key.upper()), key=lambda x: key.index(x)))
    key += "".join([c for c in alphabet if c not in key])
    return [key[i : i + 5] for i in range(0, 25, 5)]
