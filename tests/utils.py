import os

import xxhash


def digest(file_path):
    if os.path.islink(file_path):
        return symlink_digest(file_path)
    elif os.path.isfile(file_path):
        return file_digest(file_path)
    else:
        raise TypeError()


def file_digest(file_path):
    BLOCKSIZE = 65536
    message = xxhash.xxh64()
    with open(file_path, 'rb') as f:
        file_buffer = f.read(BLOCKSIZE)
        while len(file_buffer) > 0:
            message.update(file_buffer)
            file_buffer = f.read(BLOCKSIZE)

    return message.hexdigest()


def symlink_digest(file_path):
    message = xxhash.xxh64()
    message.update(os.readlink(file_path))

    return message.hexdigest()
