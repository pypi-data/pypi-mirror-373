from itertools import chain


class SetManager:
    managers = []

    def __init__(self):
        self._share = {}
        self._node_managers = [new_node_manager(self) for new_node_manager in self.managers]

    def load_path(self, *paths):
        for node_manager in self._node_managers:
            node_manager.load_path(*paths)

    def load_path_item(self, path):
        for node_manager in self._node_managers:
            node_manager.load_path_item(path)

    def get_node(self, manager, name):
        for node_manager in chain([manager], (x for x in self._node_managers if x is not manager)):
            node = node_manager.get_node(name)
            if node is not None:
                return node

    def trans(self, manager, node, result, args, params, attrs):
        method = f"trans_{self._node_managers.index(manager)}_{self._node_managers.index(node.manager)}"
        func = getattr(self, method, None)
        if func:
            return func(manager, node, result, args, params, attrs)
        return result

    @property
    def share(self):
        return self._share

    @property
    def manager(self):
        return self._node_managers[0]
