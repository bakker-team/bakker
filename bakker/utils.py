from datetime import datetime
import os

import xxhash


def get_file_digest(file_path):
    assert os.path.isfile(file_path)
    assert not os.path.islink(file_path)

    BLOCKSIZE = 65536

    message = xxhash.xxh64()
    with open(file_path, 'rb') as f:
        file_buffer = f.read(BLOCKSIZE)
        while len(file_buffer) > 0:
            message.update(file_buffer)
            file_buffer = f.read(BLOCKSIZE)

    return message.hexdigest()


def get_symlink_digest(symlink_path):
    assert os.path.islink(symlink_path)

    message = xxhash.xxh64()
    message.update(os.readlink(symlink_path))

    return message.hexdigest()


def get_directory_digest(*child_digests):
    message = xxhash.xxh64()
    for child_digest in child_digests:
        message.update(child_digest)
    return message.hexdigest()


def datetime_from_iso_format(string):
    TIME_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
    TIME_ISO_FORMAT_MILLISECONDS = '%Y-%m-%dT%H:%M:%S.%f'

    if len(string) == 19:
        return datetime.strptime(string, TIME_ISO_FORMAT)
    elif 19 < len(string) <= 26:
        return datetime.strptime(string, TIME_ISO_FORMAT_MILLISECONDS)
