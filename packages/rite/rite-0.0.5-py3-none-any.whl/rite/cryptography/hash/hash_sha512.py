import hashlib
import hmac

ASCII_NOT_CONFUSABLE = "ABCEFGHJKLMNPQRSTUWXYZ123456789"


def sha512_hash(
    key,
    msg,
) -> str:
    """
    SHA512 hexdigest of `msg` salted with `key`. UTF-8 Encoded.
    """
    return hmac.new(
        key=key.encode("utf-8") if isinstance(key, str) else key,
        msg=msg.encode("utf-8") if isinstance(msg, str) else msg,
        digestmod=hashlib.sha512,
    ).hexdigest()
