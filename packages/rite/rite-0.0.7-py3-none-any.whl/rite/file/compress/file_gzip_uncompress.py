def uncompress_file(
    inputfile,
    filename,
):
    """
    Uncompress this file using gzip and change its name.

    :param inputfile: File to compress
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :returns: Tuple with file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    zipfile = gzip.GzipFile(fileobj=inputfile, mode="rb")
    try:
        inputfile.seek(0)
        outputfile = create_spooled_temporary_file(fileobj=zipfile)
    finally:
        zipfile.close()
    new_basename = os.path.basename(filename).replace(".gz", "")
    return outputfile, new_basename
