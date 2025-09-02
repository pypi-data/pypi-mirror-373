from collections import OrderedDict
from .value import ProxyValue


class Storage:
    def __init__(self):
        self.value = OrderedDict()

    def __repr__(self):
        return repr(self.value)

    def reset(self):
        self.value = self.value.__class__()

    def add_item(self, key, value):
        if value is not ProxyValue.NOT_EXIST:
            self.value[key] = value

    def flush(self, wrapper, reset=True):
        ret = wrapper(self.value)
        if reset:
            self.reset()
        return ret
