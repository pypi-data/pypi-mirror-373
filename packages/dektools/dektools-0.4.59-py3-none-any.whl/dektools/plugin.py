import sys
from typing import Union
from .attr import Object
from .typing import NoneType

if sys.version_info[:2] >= (3, 10):
    from importlib import metadata

    entry_points = metadata.entry_points
else:
    from importlib_metadata import entry_points


def iter_plugins(name: str, group: str = 'plugins', ignore: Union[set, NoneType] = None, **kwargs):
    for ep in entry_points(group=name.partition('.')[0] + '.' + group, **kwargs):
        if not ignore or ep.name not in ignore:
            yield Object(name=ep.name, module=ep.module, value=ep.load())

# group format: package_name.sub_name
# pdm format:
# [project.entry-points."$group"]
# $ep.name(package_name) = "$ep.module(package_name.module_path):attr_name"
