def timestamp(value):
    """
    Return the timestamp of a datetime.datetime object.

    :param value: a datetime object
    :type value: datetime.datetime

    :return: the timestamp
    :rtype: str
    """
    value = value if timezone.is_naive(value) else timezone.localtime(value)
    return value.strftime(settings.DATE_FORMAT)
