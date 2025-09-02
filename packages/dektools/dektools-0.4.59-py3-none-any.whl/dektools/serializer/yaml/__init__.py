import re
import yaml as pyyaml
import yamlloader
from ...attr import DeepObject
from ..base import SerializerBase
from .tags import StrTag


class Yaml(SerializerBase):
    dump_kwargs = dict(
        allow_unicode=True,
        indent=2,
    )

    def __init__(self, resolvers, loader=None, dumper=None, encoding=None):
        super().__init__(encoding)
        resolvers = Resolver.clone(resolvers, loader or {}, dumper or {})
        self.loder = resolvers[0]
        self.dumper = resolvers[1]
        self.register_list = []

    def register(self, cls):
        if cls.yaml_tag_multi:
            self.loder.add_multi_constructor(cls.yaml_tag, cls.from_yaml_multi)
        else:
            self.loder.add_constructor(cls.yaml_tag, cls.from_yaml)
        self.dumper.add_multi_representer(cls, cls.to_yaml)
        self.register_list.append(cls)
        return cls

    def reg_batch(self, *cls_list):
        for cls in cls_list:
            self.register(cls)

    def reg_other(self, yml):
        self.reg_batch(*yml.register_list)

    def data_final(self, data):
        for cls in self.register_list:
            data = cls.data_final(data)
        return data

    def _load_file(self, file, kwargs):
        return self.data_final(pyyaml.load(file, Loader=self.loder))

    def _dump_file(self, obj, file, kwargs):
        pyyaml.dump(obj, file, Dumper=self.dumper, **(self.dump_kwargs | kwargs))


class Resolver:
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    basic = (Loader, Dumper)
    ordereddict = (yamlloader.ordereddict.CLoader, yamlloader.ordereddict.CDumper)

    attrs = DeepObject(dict(
        ignore_aliases=lambda *args: True
    ))

    @classmethod
    def clone(cls, resolvers, loader_kwargs, dumper_kwargs):
        loader, dumper = resolvers
        implicit_resolver_items = {
            'tag:yaml.org,2009:bool': [
                loader.construct_yaml_bool,
                (
                    re.compile(r'''^(?:true|True|TRUE|false|False|FALSE)$''', re.X),
                    list('tTfF')
                )
            ]
        }
        for tag, args in implicit_resolver_items.items():
            constructor, implicit_resolver = args
            loader.add_implicit_resolver(tag, *implicit_resolver)
            loader.add_constructor(tag, constructor)
        return type('loader', (loader,), dict(
            **cls.removed_implicit_resolver(loader, {'tag:yaml.org,2002:timestamp', 'tag:yaml.org,2002:bool'}),
            yaml_constructors=getattr(loader, 'yaml_constructors', {}).copy(),
            yaml_multi_constructors=getattr(loader, 'yaml_multi_constructors', {}).copy(),
            **loader_kwargs
        )), type('dumper', (dumper,), dict(
            **cls.removed_implicit_resolver(loader, {'tag:yaml.org,2002:bool'}),
            yaml_representers=getattr(dumper, 'yaml_representers', {}).copy(),
            yaml_multi_representers=getattr(dumper, 'yaml_multi_representers', {}).copy(),
            **dumper_kwargs
        ))

    @staticmethod
    def removed_implicit_resolver(cls, tag_set):
        # https://stackoverflow.com/questions/34667108/ignore-dates-and-times-while-parsing-yaml/37958106#37958106
        key = 'yaml_implicit_resolvers'
        data = getattr(cls, key, {}).copy()
        for first_letter, mappings in data.items():
            data[first_letter] = [(tag, regexp) for tag, regexp in mappings if tag not in tag_set]
        return {key: data}


yaml = Yaml(resolvers=Resolver.ordereddict)
yaml.reg_batch(StrTag)
