import functools
from typing import Type
from .dict import is_list
from .common import cached_property


class Collection:
    def __init__(self, entry):
        self.entry = entry

    def append(self, name, data):
        raise NotImplementedError

    def set_data(self, data):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError


class CollectionGeneric(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data


class DictCollection(CollectionGeneric):
    def append(self, name, data):
        self.data.update(data)


class NamedCollection(CollectionGeneric):
    def append(self, name, data):
        self.data[name] = data


class NamedListCollection(NamedCollection):
    def append(self, name, data):
        if is_list(data):
            super().append(name, data)
        else:
            self.data.update(data)


class Cache:
    def __init__(self, master):
        self.master = master
        self.caches = {}

    def __getitem__(self, method):
        return functools.partial(self.__run, method)

    def __getattr__(self, method):
        return self[method]

    def __run(self, method):
        if method not in self.caches:
            self.caches[method] = getattr(self.master, method)()
        return self.caches[method]


class CollectionDataMixin:
    @cached_property
    def __collect_cache(self):
        return Cache(self)

    def _collect_data(self, entry, collection: Type[Collection]):
        result = collection(entry)
        pre_collect = f'_pre_collect_{entry}'
        post_collect = f"_post_collect_{entry}"
        if hasattr(self, pre_collect):
            result.set_data(getattr(self, pre_collect)(result.get_data()))
        prefix = f'{entry}_'
        for x in dir(self):
            if x.startswith(prefix):
                name = x[len(prefix):]
                v = getattr(self, x)
                result.append(name, self.__collect_cache[x]() if callable(v) else v)
        if hasattr(self, post_collect):
            result.set_data(getattr(self, post_collect)(result.get_data()))
        return result.get_data()
