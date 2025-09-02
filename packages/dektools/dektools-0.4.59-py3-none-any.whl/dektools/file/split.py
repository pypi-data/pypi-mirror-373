import os
import math
import hashlib
from .path import normal_path
from .operation import remove_path, read_file


def split_file(path, limit, chunked_size=64 * 2 ** 10):
    size = os.stat(path).st_size
    count = math.ceil(size / limit)
    chunked_size = min(chunked_size, limit)
    hs = hashlib.sha256()
    with open(path, 'rb') as file:
        for i in range(count):
            with open(path + f'.{i + 1}', 'wb') as f:
                total = 0
                for chunk in iter(lambda: file.read(chunked_size), b""):
                    total += chunked_size
                    f.write(chunk)
                    hs.update(chunk)
                    if total + chunked_size > limit:
                        rest = limit - total
                        if rest > 0:
                            chunk = file.read(rest)
                            f.write(chunk)
                            hs.update(chunk)
                        break
    with open(path + '.0', 'wb') as f:
        f.write(size.to_bytes(8, 'big', signed=False))
        f.write(hs.digest())


def meta_split_file(path):
    if callable(path):
        getter = path
    else:
        def getter(index):
            try:
                return f"{normal_path(path)}.{index}"
            except FileNotFoundError:
                return None
    path_meta = getter(0)
    if path_meta is None:
        raise FileNotFoundError(f"Can't find meta file: `{path_meta}`")
    bs = read_file(path_meta)
    total_size = int.from_bytes(bs[:8], 'big', signed=False)
    i = 1
    size = 0
    parts = []
    while size < total_size:
        path_part = getter(i)
        if not path_part:
            raise FileNotFoundError(f"Can't find part file: `{path_part}`")
        size_part = os.stat(path_part).st_size
        parts.append(path_part)
        size += size_part
        i += 1
    if size > total_size:
        raise ValueError(f"Can't match total size: {size} > {total_size}")
    return parts, bs[8:].hex(), total_size, path_meta


def remove_split_files(path):
    parts, _, _, path_meta = meta_split_file(path)
    remove_path(path_meta)
    for path_part in parts:
        remove_path(path_part)


def combine_split_files(path, clear=False, chunked_size=64 * 2 ** 10):
    parts, checksum_correct, _, path_meta = meta_split_file(path)
    if parts:
        hs = hashlib.sha256()
        with open(path_meta.rsplit('.', 1)[0], 'wb') as file:
            if clear:
                remove_path(path_meta)
            for path_part in parts:
                with open(path_part, 'rb') as f:
                    for chunk in iter(lambda: f.read(chunked_size), b""):
                        file.write(chunk)
                        hs.update(chunk)
                if clear:
                    remove_path(path_part)
        checksum = hs.hexdigest()
        if checksum != checksum_correct:
            raise ValueError(f"Can't match Crc results: {checksum} != {checksum_correct}")
