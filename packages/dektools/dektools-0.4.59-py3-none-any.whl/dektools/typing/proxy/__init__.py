# https://github.com/python/typing/issues/802#issuecomment-967793565
from typing import TypeVar, Generic

T = TypeVar("T")


class Proxy(Generic[T]):
    def __new__(cls, _cls_, target: T) -> T:
        return super().__new__(cls)

    def __init__(self, cls, target: T) -> None:
        self.custom = get_custom_attrs(cls)
        self.target: T = target

    @classmethod
    def wrap(cls, target: T) -> T:  # noqa
        # We use a factory function because you can't lie about the return type in `__new__
        return cls(cls, target)  # type: ignore

    def __str__(self):
        return str(object.__getattribute__(self, "target"))

    def __repr__(self):
        return repr(object.__getattribute__(self, "target"))

    def __getattribute__(self, name: str) -> object:
        if name in object.__getattribute__(self, "custom"):
            return object.__getattribute__(self, name)
        return getattr(object.__getattribute__(self, "target"), name)


_cache_cls_attrs = {}


def get_custom_attrs(cls):
    if cls not in _cache_cls_attrs:
        result = set()
        for c in cls.mro():
            if c is Proxy:
                break
            for k in c.__dict__.keys():
                if k in {'__module__', '__parameters__', '__doc__'} or k.startswith('_') and not k.startswith('__'):
                    continue
                result.add(k)
        _cache_cls_attrs[cls] = result
    return _cache_cls_attrs[cls]
