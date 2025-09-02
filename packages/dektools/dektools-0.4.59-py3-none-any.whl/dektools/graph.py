import networkx
from .func import FuncAnyArgs


class Graph:
    def __init__(self, graph=None):
        self.core = (graph or networkx.DiGraph)()

    def load_from_data(self, nodes, edges, node=None, label=None, ns=None, es=None):
        if isinstance(edges, list):
            edges_parents = self.layer(edges, True, node)
            edges_flat = list(self.translate_flat_edges(edges, node))
        else:
            edges_parents = self.translate_layer_edges(edges, node)
            edges_flat = self.flat(edges, True, node)
        ns = FuncAnyArgs(ns) if ns is not None else ns
        es = FuncAnyArgs(es) if es is not None else es
        for _node in nodes:
            ln = None
            if label is not None:
                ln = label(_node)
            if ln is None:
                ln = _node
                if not isinstance(ln, str):
                    ln = str(ln)
            node_ = self.translate(_node, node)
            _ns = {}
            if ns is not None:
                _ns = ns(_node, edges_parents.get(node_), node_) or _ns
            self.core.add_node(node_, label=ln, **_ns)
        for edge in edges_flat:
            _es = {}
            if es is not None:
                _es = es(*edge) or _es
            self.core.add_edge(*edge, **_es)
        return self

    @staticmethod
    def translate(node, func=None):
        if func is not None:
            _node_ = func(node)
            if _node_ is not None:
                node = _node_
        return node

    @classmethod
    def translate_flat_edges(cls, edges, func=None):
        for (x, y) in edges:
            yield cls.translate(x, func), cls.translate(y, func)

    @classmethod
    def translate_layer_edges(cls, edges, func=None):
        result = {}
        for y, xx in edges.items():
            z = result.setdefault(cls.translate(y, func), set())
            for x in xx:
                z.add(cls.translate(x, func))
        return result

    @classmethod
    def flat(cls, edges, parents=True, func=None):
        result = []
        for x, xx in edges.items():
            x = cls.translate(x, func)
            for y in xx:
                y = cls.translate(y, func)
                result.append((y, x) if parents else (x, y))
        return result

    @classmethod
    def layer(cls, edges, parents=True, func=None):
        result = {}
        for (x, y) in cls.translate_flat_edges(edges, func):
            xx = result.setdefault(y if parents else x, set())
            xx.add(x if parents else y)
        return result

    def to_svg(self):
        return networkx.drawing.nx_pydot.to_pydot(self.core).create_svg()

    def get_cycles(self):
        return networkx.recursive_simple_cycles(self.core)

    def get_depths(self):
        result = {}
        for _, m in networkx.shortest_path_length(self.core):
            for node, depth in m.items():
                result[node] = result.get(node, 0) + depth
        return result
