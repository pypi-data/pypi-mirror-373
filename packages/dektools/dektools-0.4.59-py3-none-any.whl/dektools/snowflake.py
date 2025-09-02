import os
from snowflake import SnowflakeGenerator as SnowflakeGeneratorOrigin


class SnowflakeGenerator:
    MAX_VALUE = 2 * 64 - 1

    def __init__(self, instance=None):
        self.inner = SnowflakeGeneratorOrigin(int(os.getenv('SNOWFLAKE_INSTANCE', 0)) if instance is None else instance)

    def __getattr__(self, item):
        return getattr(self.inner, item)

    def new_id(self):
        return next(self.inner)


class SnowflakeGeneratorSet:
    sfg_cls = SnowflakeGenerator

    def __init__(self, instance=None):
        self.instance = instance
        self.set = {}

    def new_id(self, name):
        if name not in self.set:
            self.set[name] = self.sfg_cls(self.instance)
        return self.set[name].new_id()
