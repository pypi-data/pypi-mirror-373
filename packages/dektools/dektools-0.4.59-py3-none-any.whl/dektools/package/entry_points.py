import os
import codecs
from importlib.metadata import EntryPoints as EntryPoints_
from ..file import normal_path, sure_dir

DEFAULT_VALUE = type('default_value', (), {})


class EntryPoints:
    def __init__(self, encoding=None):
        self.encoding = encoding or "utf-8"

    def load(self, file, encoding=None, default=DEFAULT_VALUE):
        if not hasattr(file, 'read'):
            if not os.path.isfile(file) and default is not DEFAULT_VALUE:
                return default
            with codecs.open(file, encoding=encoding or self.encoding) as f:
                return self.loads(f.read())
        else:
            return self.loads(file.read())

    def loads(self, s):
        if isinstance(s, bytes):
            s = s.decode(self.encoding)
        result = {}
        for ep in EntryPoints_._from_text(s):
            if not ep.group in result:
                result[ep.group] = {}
            result[ep.group][ep.name] = ep.value
        return result

    def dump(self, file, obj, encoding=None):
        if not hasattr(file, 'write'):
            file = normal_path(file)
            sure_dir(os.path.dirname(file))
            with open(file, 'wb') as f:
                f.write(self.dumps(obj, encoding=encoding or self.encoding))
        else:
            return file.write(self.dumps(obj, encoding=encoding or self.encoding))

    def dumps(self, obj, encoding=False):
        result = ''
        for group, info in obj.items():
            result += f'[{group}]\n'
            for name, value in info.items():
                result += f'{name} = {value}\n'
            result += '\n'
        if encoding is None:
            encoding = self.encoding
        return result.encode(encoding) if encoding else result


entry_points = EntryPoints()
