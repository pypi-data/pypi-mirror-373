import os
import codecs
from io import BytesIO, StringIO, TextIOBase
from ...file import sure_parent_dir, normal_path

DEFAULT_VALUE = type('default_value', (), {})


class SerializerBase:
    _persist_str = True

    def __init__(self, encoding=None):
        self.encoding = encoding or "utf-8"

    def loads(self, s, encoding=None, **kwargs):
        if self._persist_str:
            if isinstance(s, (bytes, memoryview)):
                s = str(s, encoding or self.encoding)
        else:
            if isinstance(s, str):
                s = s.encode(encoding or self.encoding)
        return self.load(StringIO(s) if self._persist_str else BytesIO(s), **kwargs)

    def load(self, f, encoding=None, default=DEFAULT_VALUE, **kwargs):
        if not hasattr(f, 'read'):
            if not os.path.isfile(f) and default is not DEFAULT_VALUE:
                return default
            if self._persist_str:
                with codecs.open(f, encoding=encoding or self.encoding) as ff:
                    return self._load_file(ff, kwargs)
            else:
                with open(f, 'rb') as ff:
                    return self._load_file(ff, kwargs)
        else:
            if self._persist_str and not isinstance(f, TextIOBase):
                f = StringIO(f.read().decode(encoding or self.encoding))
            return self._load_file(f, kwargs)

    def _load_file(self, file, kwargs):
        raise NotImplementedError

    def dumps(self, o, **kwargs):
        file = StringIO() if self._persist_str else BytesIO()
        self.dump(file, o, **kwargs)
        return file.getvalue()

    def dump(self, f, o, encoding=None, **kwargs):
        if not hasattr(f, 'write'):
            f = normal_path(f)
            sure_parent_dir(f)
            if self._persist_str:
                with codecs.open(f, 'w', encoding=encoding or self.encoding) as ff:
                    self._dump_file(o, ff, kwargs)
            else:
                with open(f, 'wb') as ff:
                    self._dump_file(o, ff, kwargs)
        else:
            self._dump_file(o, f, kwargs)

    def _dump_file(self, obj, file, kwargs):
        raise NotImplementedError
