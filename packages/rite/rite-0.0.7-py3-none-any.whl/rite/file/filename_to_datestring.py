from . import settings


def filename_to_datestring(filename, datefmt=None):
    """
    Return the date part of a file name.

    :param datefmt: strftime format string, ``settings.DATE_FORMAT`` is used
                    if is ``None``
    :type datefmt: ``str`` or ``None``

    :returns: Date part or nothing if not found
    :rtype: ``str`` or ``NoneType``
    """
    datefmt = datefmt or settings.DATE_FORMAT
    regex = datefmt_to_regex(datefmt)
    search = regex.search(filename)
    if search:
        return search.groups()[0]
