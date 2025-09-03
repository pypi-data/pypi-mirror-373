def compress_file(
    inputfile,
    filename,
):
    """
    Compress input file using gzip and change its name.

    :param inputfile: File to compress
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :returns: Tuple with compressed file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    outputfile = create_spooled_temporary_file()
    new_filename: str = f"{filename}.gz"
    zipfile = gzip.GzipFile(filename=filename, fileobj=outputfile, mode="wb")
    try:
        inputfile.seek(0)
        copyfileobj(inputfile, zipfile, settings.TMP_FILE_READ_SIZE)
    finally:
        zipfile.close()
    return outputfile, new_filename


def compress_file(
    inputfile,
    filename,
):
    """
    Compress input file using gzip and change its name.

    :param inputfile: File to compress
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :returns: Tuple with compressed file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    outputfile = create_spooled_temporary_file()
    new_filename: str = f"{filename}.gz"
    zipfile = gzip.GzipFile(filename=filename, fileobj=outputfile, mode="wb")
    try:
        inputfile.seek(0)
        copyfileobj(inputfile, zipfile, settings.TMP_FILE_READ_SIZE)
    finally:
        zipfile.close()
    return outputfile, new_filename
