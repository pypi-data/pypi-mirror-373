import yaml as pyyaml
from yaml.nodes import SequenceNode, MappingNode


class TagBase(pyyaml.YAMLObject):
    yaml_tag_multi = False
    yaml_tag = None

    def __repr__(self):
        raise NotImplementedError

    @classmethod
    def data_final(cls, data):
        return data

    @classmethod
    def from_yaml(cls, loader, node):
        # return cls.node_to_data(node)
        # return cls.node_to_data_raw(node)
        # return cls(node.value)
        raise NotImplementedError

    @classmethod
    def from_yaml_multi(cls, loader, tag_suffix, node):
        raise NotImplementedError

    @classmethod
    def to_yaml(cls, dumper, instance):
        # return dumper.represent_scalar(cls.yaml_tag, instance.)
        raise NotImplementedError

    @classmethod
    def node_to_data_raw(cls, node, sequence=list, mapping=dict):
        if isinstance(node, SequenceNode):
            return sequence(cls.node_to_data_raw(x) for x in node.value)
        elif isinstance(node, MappingNode):
            d = mapping()
            for k, v in node.value:
                d[cls.node_to_data_raw(k)] = cls.node_to_data_raw(v)
            return d
        return node.value

    @classmethod
    def node_to_data(cls, loader, node):
        if isinstance(node, SequenceNode):
            return loader.construct_sequence(node)
        elif isinstance(node, MappingNode):
            return loader.construct_mapping(node)
        return node.value
