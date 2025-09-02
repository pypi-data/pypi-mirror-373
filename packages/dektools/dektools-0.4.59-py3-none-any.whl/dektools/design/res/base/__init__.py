from collections import OrderedDict
from ....types import TypeBase, TypesBase, ManagerBase
from ....file import FileHitChecker, multi_ext, read_file, read_text
from ....serializer.yaml import yaml
from ....dict import dict_merge
from ...utils import split_function


class ResBase(TypeBase):
    _empty = object()
    _typed_cls_suffix = 'Res'
    _auto_load = False
    ext = None

    def __init__(self, manager, name, path):
        super().__init__(manager)
        self.name = name
        self.path = path
        if self._auto_load:
            self._content = self.load()
        else:
            self._content = self._empty

    def load(self):
        raise NotImplementedError

    def clean(self):
        self._content = self._empty

    @property
    def content(self):
        if self._content is self._empty:
            self._content = self.load()
        return self._content

    @property
    def text(self):
        return read_text(self.path)

    @property
    def bytes(self):
        return read_file(self.path)

    reflect_open = False

    @classmethod
    def reflect(cls, others):
        pass


class ResBytes(ResBase):
    def load(self):
        return self.bytes


class ResText(ResBase):
    def load(self):
        return self.text


class FunctionRes(ResBase):
    def load(self):
        return self.path


class ResYaml(ResBase):
    default_value = OrderedDict

    def yaml(self):
        value = yaml.load(self.path)
        if value is None:
            return self.default_value()
        return value

    def load(self):
        return self.yaml()


class ResYamlFunc(ResYaml):
    function_res_cls = FunctionRes
    extra_keys = []
    marker_keys = []

    def load(self):
        data_map = self.yaml()
        extras = {}
        markers = {}
        functions = {}
        for extra in self.extra_keys:
            data = data_map.pop(extra, None)
            if data is not None:
                extras[extra] = data
        for name, body in data_map.items():
            args, params, body = split_function(body)
            for marker in self.marker_keys:
                if name.endswith(marker):
                    array = markers.setdefault(marker, [])
                    name = name[:len(name) - len(marker)]
                    array.append(name)
                    break
            functions[name] = args, params, body
        return extras, markers, functions

    reflect_open = True

    @classmethod
    def reflect(cls, others):
        extras, markers, functions = {}, {}, {}
        # manager: ResManager | None = None
        manager = None
        for other in others:
            manager = other.manager
            a, b, c = other.content
            dict_merge(extras, a)
            dict_merge(markers, b)
            dict_merge(functions, c)
        typed = cls.get_typed_name()
        manager.reflections[typed] = dict(extras=extras, markers=markers)
        manager.content.pop(typed, None)
        data = manager.content.setdefault(cls.function_res_cls.get_typed_name(), {})
        for key, value in functions.items():
            data[key] = cls.function_res_cls(manager, key, value)

    @classmethod
    def on_typed_registered(cls, types):
        types.register(cls.function_res_cls)


class ResTypes(TypesBase):
    pass


class UnknownRes(ResBase):
    def load(self):
        pass


class ResManager(ManagerBase):
    types: ResTypes = None
    unknown_res_cls = UnknownRes

    def __init__(self, set_manager, ignore_files=None):
        self.set_manager = set_manager
        self.ignore_files = [] if ignore_files is None else ignore_files
        self.content = {}
        self.reflections = {}

    def load_path(self, *paths):
        def walk(fp, match, _):
            if match:
                return
            reflections.update(self.load_path_item(fp))

        reflections = set()

        for path in paths:
            FileHitChecker(path, *self.ignore_files, '.gitignore', lines=['.git']).walk(walk)

        for t in reflections:
            self.types.get(t).reflect(self.content.get(t).values())

    def load_path_item(self, path):
        def add(d, c, f):
            key = c, f
            if key not in self.set_manager.share:
                self.set_manager.share[key] = c(self, f, path)
            d[f] = self.set_manager.share[key]

        reflections = set()
        filename, ext_list = multi_ext(path)
        if ext_list:
            for typed, res_cls in self.types.items():
                is_reflection = res_cls.reflect_open
                ext = res_cls.ext
                data = self.content.setdefault(typed, {})
                if isinstance(ext, str):
                    if ext_list[-1] == ext:
                        add(data, res_cls, filename)
                elif isinstance(ext, list):
                    if ext_list[-len(ext):] == ext:
                        add(data, res_cls, filename)
                elif isinstance(ext, set):
                    if ext_list[-1] in ext:
                        add(data, res_cls, filename)
                else:
                    is_reflection = False
                if is_reflection:
                    reflections.add(typed)
        return reflections

    def get_res_map(self, typed):
        return self.content.get(typed)

    def find_res(self, name):
        for typed in self.types.keys():
            data = self.content.get(typed)
            if data:
                if name in data:
                    return data[name]
        return self.unknown_res_cls(self, name, None)

    def _get_reflections_data(self, root, typed, key):
        info = self.reflections.get(typed)
        if info:
            extras = info.get(root)
            if extras:
                return extras.get(key)

    def get_extras(self, typed, key):
        return self._get_reflections_data('extras', typed, key)

    def get_markers(self, typed, key):
        return self._get_reflections_data('markers', typed, key)
