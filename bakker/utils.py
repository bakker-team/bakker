from datetime import datetime


def datetime_from_iso_format(string):
    TIME_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
    TIME_ISO_FORMAT_MILLISECONDS = '%Y-%m-%dT%H:%M:%S.%f'

    if len(string) == 19:
        return datetime.strptime(string, TIME_ISO_FORMAT)
    elif 19 < len(string) <= 26:
        return datetime.strptime(string, TIME_ISO_FORMAT_MILLISECONDS)
