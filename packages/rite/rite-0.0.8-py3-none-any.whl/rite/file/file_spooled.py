def create_spooled_temporary_file(
    filepath=None,
    fileobj=None,
):
    """
    Create a spooled temporary file. if ``filepath`` or ``fileobj`` is
    defined its content will be copied into temporary file.

    :param filepath: Path of input file
    :type filepath: str

    :param fileobj: Input file object
    :type fileobj: file

    :returns: Spooled temporary file
    :rtype: :class:`tempfile.SpooledTemporaryFile`
    """
    spooled_file = tempfile.SpooledTemporaryFile(
        max_size=settings.TMP_FILE_MAX_SIZE, dir=settings.TMP_DIR
    )
    if filepath:
        fileobj = open(file=filepath, mode="r+b")
    if fileobj is not None:
        fileobj.seek(0)
        copyfileobj(
            fsrc=fileobj,
            fdst=spooled_file,
            length=settings.TMP_FILE_READ_SIZE,
        )
    return spooled_file
