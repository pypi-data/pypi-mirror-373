class MapChain:
    EMPTY = type('empty', (), {})

    class DelayMap:
        def __init__(self, func):
            self.func = func

        def flat(self, data):
            return self.func(data)

    def __init__(self, data=None, parents=None):
        self.parents = parents or []
        self.data = data or {}

    def __json__(self):
        return self.flat()

    def __contains__(self, key):
        return self.has(key)

    def derive(self, data=None):
        return self.__class__(data=data, parents=[self])

    def dependency(self):
        self.parents = []

    def add_item(self, key, value):
        self.data[key] = value

    def remove_item(self, key):
        self.data.pop(key, None)

    def update(self, data):
        for k, v in data.items():
            self.add_item(k, v)

    def clear(self):
        self.data.clear()

    def get_pointer(self, key):
        if key in self.data:
            return self.data
        for parent in self.parents:
            pointer = parent.get_pointer(key)
            if pointer is not None:
                return pointer

    def has(self, key):
        return self.get_pointer(key) is not None

    def get_item(self, key, default=EMPTY):
        pointer = self.get_pointer(key)
        if pointer is None:
            if default is not self.EMPTY:
                return default
            raise ValueError(f"Can't find the key: {key}")
        return pointer[key]

    def flat(self, init=None):
        def walk(node):
            nonlocal data
            data = {**node.data, **data}
            for parent in node.parents:
                walk(parent)

        data = {}
        walk(self)
        data_normal = {} if init is None else init
        delay_list = []
        for k, v in data.items():
            if isinstance(v, self.DelayMap):
                delay_list.append(v)
            else:
                data_normal[k] = v
        data_result = {}
        for delay in delay_list:
            data_result.update(delay.flat(data_normal))
        return {**data_normal, **data_result}


class MapChainContext(MapChain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._global = set()
        self._nonlocal = set()

    def iter_tops(self):
        if self.parents:
            for parent in self.parents:
                yield from parent.iter_tops()
        else:
            yield self

    def mark_global(self, name):
        self._global.add(name)

    def mark_nonlocal(self, name):
        self._nonlocal.add(name)

    def add_item(self, key, value):
        if key in self._global:
            for top in self.iter_tops():
                if key in top.data:
                    top.data[key] = value
                    break
            else:
                raise ValueError(f"Can't match global by the key: {key}")
        elif key in self._nonlocal:
            for parent in self.parents:
                pointer = parent.get_pointer(key)
                if pointer is not None:
                    pointer[key] = value
                    break
            else:
                raise ValueError(f"Can't match nonlocal by the key: {key}")
        else:
            super().add_item(key, value)
