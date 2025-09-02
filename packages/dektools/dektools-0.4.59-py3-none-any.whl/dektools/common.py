import datetime

try:
    from functools import cached_property
except ImportError:
    # Python < 3.8
    class cached_property(object):

        def __init__(self, func):
            self.func = func
            # for attr in ('__name__', '__module__', '__doc__'):
            #     setattr(self, attr, getattr(func, attr, None))

        def __get__(self, obj, cls=None):
            if obj is None:
                return self
            value = self.func(obj)
            object.__setattr__(obj, self.func.__name__, value)
            # obj.__dict__[self.func.__name__] = value = self.func(obj)
            return value


class classproperty:
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.
    """

    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class cached_classproperty(classproperty):
    def get_result_field_name(self):
        return self.fget.__name__ + "__property_result__" if self.fget else None

    def __get__(self, instance, cls=None):
        result_field_name = self.get_result_field_name()

        if hasattr(cls, result_field_name):
            return getattr(cls, result_field_name)

        if not cls or not result_field_name:
            return self.fget(cls)

        setattr(cls, result_field_name, self.fget(cls))
        return getattr(cls, result_field_name)


try:
    from contextlib import aclosing
except ImportError:
    class aclosing:
        def __init__(self, agen):
            self._aiter = agen

        async def __aenter__(self):
            return self._aiter

        async def __aexit__(self, *args):
            await self._aiter.aclose()


def rect_split(total, col_max):
    for i in range(col_max):
        col = col_max - i
        rest = total % col
        if rest == 0:
            row = total // col
            return [col for _ in range(row)]
        elif rest * 2 >= col:
            row = total // col + 1
            return [col for _ in range(row - 1)] + [rest]


def find(array, func, start=None, end=None, reverse=False):
    from .func import FuncAnyArgs
    start = 0 if start is None else max(0, start)
    end = len(array) if end is None else min(end, len(array))
    func = FuncAnyArgs(func)
    r = range(start, end)
    if reverse:
        r = reversed(r)
    for i in r:
        if func(array[i], i, array):
            return i
    return -1


def ns2datetime(t):
    return datetime.datetime.fromtimestamp(t / 1000000000)


def xvalue(x, y):
    if y is None:
        return x
    elif isinstance(y, float):
        return x.__class__(x * y)
    else:
        return y


if __name__ == '__main__':
    print(rect_split(13, 5))
    print(rect_split(11, 5))
    print(rect_split(4, 5))
