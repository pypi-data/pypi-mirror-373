class ProduceBase:
    @classmethod
    def wrapper(cls, name=None):
        def w(d):
            return cls(d, name)

        return w

    def __init__(self, data, name=None):
        self.data = data
        self.name = name
        self._broadcast()

    def __repr__(self):
        return repr(dict(name=self.name, data=self.data))

    def _broadcast(self):
        if isinstance(self.data, dict):
            for k in list(self.data):
                v = self.data[k]
                if hasattr(v, 'produce_notify'):
                    v.produce_notify(self, k)
