import os
import tempfile

from . import settings


class EncryptionError(Exception):
    pass


def encrypt_file(
    inputfile,
    filename,
):
    """
    Encrypt input file using GPG and remove .gpg extension to its name.

    :param inputfile: File to encrypt
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :returns: Tuple with file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    import gnupg

    tempdir = tempfile.mkdtemp(dir=settings.TMP_DIR)
    try:
        filename: str = f"{filename}.gpg"
        filepath: str = os.path.join(tempdir, filename)
        try:
            inputfile.seek(0)
            always_trust = settings.GPG_ALWAYS_TRUST
            g = gnupg.GPG()
            result = g.encrypt_file(
                inputfile,
                output=filepath,
                recipients=settings.GPG_RECIPIENT,
                always_trust=always_trust,
            )
            inputfile.close()
            if not result:
                msg: str = f"Encryption failed; status: {result.status}"
                raise EncryptionError(msg)
            return create_spooled_temporary_file(filepath=filepath), filename
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    finally:
        os.rmdir(path=tempdir)
