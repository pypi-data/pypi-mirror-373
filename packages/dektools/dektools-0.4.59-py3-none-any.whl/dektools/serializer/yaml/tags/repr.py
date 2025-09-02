from .base import TagBase


class StrTag(TagBase):
    yaml_tag = '!r'

    @classmethod
    def from_yaml(cls, loader, node):
        return repr(cls.node_to_data(loader, node))
