from collections import OrderedDict
from .str import to_var_format, to_var_format_classname


class TypeBase:
    _typed_cls_suffix = None
    _typed_name = None

    def __init__(self, manager):
        self.manager = manager

    @classmethod
    def get_typed_name(cls):
        if cls._typed_name:
            return cls._typed_name
        return cls.__name__[:-len(cls._typed_cls_suffix)]

    @classmethod
    def on_typed_registered(cls, types):
        pass

    @classmethod
    def is_my_typed(cls, obj):
        if isinstance(obj, type):
            return issubclass(obj, cls)
        else:
            return cls.is_my_typed(obj.__class__)

    @classmethod
    def recognize(cls, data):
        return False


class TypesBase:
    def __init__(self, *others):
        self._others = others
        self._maps = OrderedDict()

    def __getitem__(self, item):
        if isinstance(item, type) and issubclass(item, TypeBase):
            item = item.get_typed_name()
        return self._maps[item]

    def keys(self):
        return self._maps.keys()

    def values(self):
        return self._maps.values()

    def items(self):
        return self._maps.items()

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def register(self, cls):
        if self._others:
            bases = [x for x in (x.get(cls) for x in self._others) if x is not None]
            if bases:
                cls = type[TypeBase](cls.__name__, (*bases, cls), {})
        return self.register_raw(cls)

    def register_raw(self, cls):
        self._maps[cls.get_typed_name()] = cls
        cls.on_typed_registered(self)
        return cls

    @staticmethod
    def to_label(s):
        return '-'.join(to_var_format(s))

    @staticmethod
    def to_classname(s):
        return to_var_format_classname(to_var_format(s))

    @staticmethod
    def to_pairs(s):
        array = to_var_format(s)
        return '-'.join(array), to_var_format_classname(array)


class ManagerBase:
    types: TypesBase = None
