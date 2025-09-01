import secrets
import string

ASCII_NOT_CONFUSABLE = "ABCEFGHJKLMNPQRSTUWXYZ123456789"


def random_string_generator(
    size=16,
    chars=string.ascii_lowercase + string.ascii_uppercase + string.digits,
) -> str:
    """
    Generate a secure random string with length `size` out of the defined
    charset `chars`.
    """
    choice = secrets.SystemRandom().choice
    return "".join(choice(chars) for _ in range(size))
