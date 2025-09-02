import json
from collections import OrderedDict
from io import StringIO
from ..base import SerializerBase

try:
    from .utils._load import load_from_env
    from dynaconf.vendor.dotenv import dotenv_values
except ImportError as e:
    if "'dynaconf'" in e.args[0]:
        pass
    else:
        raise


class Dyna(SerializerBase):
    def _load_file(self, file, kwargs):
        return load_dyna(src=file, **kwargs)

    def _dump_file(self, obj, file, kwargs):
        add = kwargs.get('add')
        prefix = kwargs.get('prefix')
        json_ = kwargs.get('json')
        if add:
            obj = {f'{add}_{k}': v for k, v in obj.items()}
        obj = data_to_dyna(obj, prefix)
        if json_:
            json.dump(obj, file)
        else:
            file.write('\n'.join(f'{k}="{v}"' for k, v in obj.items()))


dyna = Dyna()


def data_to_dyna(data, prefix=None):
    raw_keys = {k for k in data if prefix and not k.startswith(prefix)}
    return {k: v if k in raw_keys else repr(v) for k, v in data.items()}


def load_dyna(data=None, prefix=None, src=None, **kwargs):
    data = data or OrderedDict()
    environ = None
    if src is not None:
        if isinstance(src, dict):
            environ = src
        elif hasattr(src, 'read') and not isinstance(src, StringIO):
            environ = dotenv_values(StringIO(src.read()))
        else:
            environ = dotenv_values(src)
    kwargs = {**dict(key=None, prefix=prefix or False, silent=True), **kwargs, **dict(environ=environ)}
    load_from_env(data, **kwargs)
    for key in ('loader_identifier', 'validate'):
        data.pop(key)
    return data
