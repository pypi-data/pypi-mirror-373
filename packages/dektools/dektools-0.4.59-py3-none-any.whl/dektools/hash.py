import hashlib
from .file import sure_read, iter_file_content

algorithms = hashlib.algorithms_guaranteed


def hash_file(algorithm, path, block_size=64 * 2 ** 10, args=None):  # algorithm: hashlib.__always_supported
    hs = getattr(hashlib, algorithm)()
    file = sure_read(path)
    for chunk in iter_file_content(file, block_size):
        hs.update(chunk)
    return hs.hexdigest(*(args or ()))
