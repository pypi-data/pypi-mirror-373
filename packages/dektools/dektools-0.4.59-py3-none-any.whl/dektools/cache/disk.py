import os
import json
import datetime
import shutil
from zoneinfo import ZoneInfo
from ..file.operation import write_file, read_file, read_text
from .base import Cache


class CacheDisk(Cache):
    EMPTY = type('empty', (), {})

    def __init__(self, path_root):
        self.path_root = path_root

    def key2path(self, key):
        path = os.path.join(self.path_root, key)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def path_content(self, key):
        return os.path.join(self.key2path(key), 'content')

    def path_meta(self, key):
        return os.path.join(self.key2path(key), 'meta')

    @property
    def now(self):
        return datetime.datetime.now(tz=ZoneInfo('UTC')).timestamp()

    @staticmethod
    def normalize_key(key):
        if isinstance(key, str):
            return key
        else:
            return os.path.join(*key)

    def set(self, key, value):
        key = self.normalize_key(key)
        meta = dict(
            timestamp=self.now
        )
        if isinstance(value, bytes):
            meta['type'] = 'bytes'
            write_file(self.path_content(key), b=value)
        else:
            meta['type'] = 'json'
            write_file(self.path_content(key), s=json.dumps(value))
        write_file(self.path_meta(key), s=json.dumps(meta))

    def get(self, key, timeout=None):
        key = self.normalize_key(key)
        path_meta = self.path_meta(key)
        path_content = self.path_content(key)
        if os.path.exists(path_meta) and os.path.exists(path_content):
            with open(path_meta, 'r') as f:
                meta = json.load(f)
                if timeout is None or meta['timestamp'] + timeout > self.now:
                    if meta['type'] == 'json':
                        return json.loads(read_text(path_content))
                    else:
                        return read_file(path_content)
        return self.EMPTY

    def delete(self, key):
        key = self.normalize_key(key)
        path_meta = self.path_meta(key)
        path_content = self.path_content(key)
        if os.path.exists(path_meta):
            os.remove(path_meta)
        if os.path.exists(path_content):
            os.remove(path_content)

    def clear(self):
        if os.path.exists(self.path_root):
            shutil.rmtree(self.path_root)
