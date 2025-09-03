from rite.time.date_format_to_regex import date_format_to_regex


def filename_to_datestring(filename, date_format="%Y-%m-%d-%H%M%S"):
    """
    Return the date part of a file name.

    :param date_format: strftime format string, ``settings.DATE_FORMAT`` is used
                    if is ``None``
    :type date_format: ``str`` or ``None``

    :returns: Date part or nothing if not found
    :rtype: ``str`` or ``NoneType``
    """
    regex = date_format_to_regex(date_format)
    search = regex.search(filename)
    if search:
        return search.groups()[0]
