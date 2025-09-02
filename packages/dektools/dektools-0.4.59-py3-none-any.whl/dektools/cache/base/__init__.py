class Cache:
    def set(self, key, value):
        raise NotImplemented()

    def get(self, key, timeout=None):
        raise NotImplemented()

    def delete(self, key):
        raise NotImplemented()

    def clear(self):
        raise NotImplemented()
