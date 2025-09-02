from .base import TagBase


class StrTag(TagBase):
    yaml_tag = '!s'

    @classmethod
    def from_yaml(cls, loader, node):
        return str(cls.node_to_data_raw(node))
