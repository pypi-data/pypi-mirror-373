from .dict import is_list, is_dict


def object_path_get(obj, path, ignore=True, mode='ia'):
    keys = [x for x in (path or '').split(".")]
    cursor = obj
    for key in keys:
        if 'i' in mode:
            try:
                if is_list(cursor):
                    key = int(key)
                cursor = cursor[key]
                continue
            except (IndexError, KeyError, TypeError, ValueError):
                pass
        if 'a' in mode:
            try:
                cursor = getattr(cursor, key)
                continue
            except AttributeError:
                pass
        if not ignore:
            raise ValueError(f'Cant get value of {obj} , {path} , {mode} , {key}')
    return cursor


def object_path_set(obj, paths, value, sep='.'):
    cursor = obj
    if isinstance(paths, str):
        paths = paths.split(sep)
    length = len(paths)
    for i, path in enumerate(paths):
        if i == length - 1:
            if hasattr(cursor, '__setitem__'):
                cursor[path] = value
            else:
                setattr(cursor, path, value)
        else:
            if hasattr(cursor, '__getitem__'):
                try:
                    cursor = cursor[path]
                except KeyError:
                    v = cursor.__class__()
                    cursor[path] = v
                    cursor = v
            else:
                try:
                    cursor = getattr(cursor, path)
                except AttributeError:
                    v = cursor.__class__()
                    setattr(cursor, path, v)
                    cursor = v
    return value


def object_path_update(obj, data, sep='.'):
    for k, v in data.items():
        object_path_set(obj, k, v, sep)


class AttrsKwargs:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        return self._kwargs[item]


class AttrsKwargsAny(AttrsKwargs):
    _any = None

    def __getitem__(self, item):
        return self._kwargs.get(item, self._any)


class AttrsDict:
    def __init__(self, kwargs, final=None):
        self._kwargs = kwargs
        self._final = final

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        value = self._get_item_raw(item)
        return self._final(value) if self._final else value

    def _get_item_raw(self, item):
        return self._kwargs[item]


class AttrsDictAny(AttrsDict):
    _any = None

    def _get_item_raw(self, item):
        return self._kwargs.get(item, self._any)


class DictObj(object):
    pass


def dict_to_obj(data, cls=DictObj):
    def walk(node):
        if isinstance(node, dict):
            obj = cls()
            for k, v in node.items():
                setattr(obj, k, walk(v))
            return obj
        else:
            return node

    return walk(data)


class _ObjectWide:
    def __getattr__(self, item):
        raise AttributeError(f"type object '{self.__class__.__name__}' has no attribute '{item}'")

    def __json__(self):
        return self.__dict__


class Object(_ObjectWide):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class DeepObject(_ObjectWide):
    def __init__(self, kwargs):
        self.__dict__.update({k: self.__class__(v) if is_dict(v) else v for k, v in kwargs.items()})


class DeepObjectCall(DeepObject):
    def __call__(self, *args, **kwargs):
        return self.__dict__[None](*args, **kwargs)
