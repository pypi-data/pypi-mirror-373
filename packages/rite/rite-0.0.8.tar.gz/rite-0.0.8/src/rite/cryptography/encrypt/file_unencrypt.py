import os
import tempfile
from getpass import getpass

from . import settings


class DecryptionError(Exception):
    pass


def unencrypt_file(
    inputfile,
    filename,
    passphrase=None,
):
    """
    Unencrypt input file using GPG and remove .gpg extension to its name.

    :param inputfile: File to encrypt
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :param passphrase: Passphrase of GPG key, if equivalent to False, it will
                       be asked to user. If user answer an empty pass, no
                       passphrase will be used.
    :type passphrase: ``str`` or ``None``

    :returns: Tuple with file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    import gnupg

    def get_passphrase(
        passphrase=passphrase,
    ):
        """
        Get passphrase from user or return the one passed as argument.
        """
        return passphrase or getpass("Input Passphrase: ") or None

    temp_dir = tempfile.mkdtemp(dir=settings.TMP_DIR)
    try:
        new_basename = os.path.basename(filename).replace(".gpg", "")
        temp_filename = os.path.join(temp_dir, new_basename)
        try:
            inputfile.seek(0)
            g = gnupg.GPG()
            result = g.decrypt_file(
                fileobj_or_path=inputfile,
                passphrase=get_passphrase(),
                output=temp_filename,
            )
            if not result:
                raise DecryptionError(
                    "Decryption failed; status: %s" % result.status
                )
            outputfile = create_spooled_temporary_file(temp_filename)
        finally:
            if os.path.exists(path=temp_filename):
                os.remove(path=temp_filename)
    finally:
        os.rmdir(path=temp_dir)
    return outputfile, new_basename
