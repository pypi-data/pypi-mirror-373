import re
import unicodedata


def sanitize_name(name) -> str:
    """
    Sanitize a string by normalizing it and replacing non-alphanumeric
    characters.

    Args:
        name: The input string to sanitize.

    Returns:
        A sanitized version of the input string.
    """

    # Normalize to ASCII
    name: str = (
        unicodedata.normalize("NFKD", name)
        .encode(
            "ascii",
            "ignore",
        )
        .decode("ascii")
    )

    # Replace any non-alphanumeric characters with underscores
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)

    # Remove multiple underscores in a row
    name = re.sub(r"_{2,}", "_", name)

    # Strip leading or trailing underscores
    return name.strip("_")
