import inspect
from .dict import assign_list, AssignEmpty


class FuncSet:
    def __init__(self, result, *func_list):
        self.func_list = list(func_list)
        self.result = result or None

    def __call__(self, *args, **kwargs):
        result = []
        for func in self.func_list:
            result.append(func(*args, **kwargs))
        if self.result:
            return self.result(result)
        return result

    def append(self, func):
        self.func_list.append(func)


class FuncAnyArgs:
    def __init__(self, func, default=None):
        self.func = func
        self.default = default
        args, kwargs = get_args_kwargs(func)
        self.args_count = len(args)
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        kwargs = {k: kwargs.get(k, v) for k, v in self.kwargs.items()}
        args = [args[i] if i < len(args) else self.default for i in range(self.args_count)]
        return self.func(*args, **kwargs)


class FuncCache:
    def __init__(self):
        self._items = {}

    def __call__(self, func):
        if func not in self._items:
            self._items[func] = func()
        return self._items[func]

    def __getattr__(self, item):
        def wrapper(func):
            if item not in self._items:
                self._items[item] = func()
            return self._items[item]

        return wrapper


class Arguments:
    Empty = AssignEmpty

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f'{self.__class__.__name__}(*{repr(self.args)}, **{repr(self.kwargs)})'

    def __call__(self, __placeholder__func, *args, **kwargs):
        if args:
            args = assign_list(self.args, args)
        if kwargs:
            kwargs = self.kwargs | kwargs
        return __placeholder__func(*args, **kwargs)


def get_args_kwargs(func):
    args = []
    kwargs = {}
    for key, value in inspect.signature(func).parameters.items():
        if value.default is inspect.Signature.empty:
            args.append(key)
        else:
            kwargs[key] = value.default
    return args, kwargs


if __name__ == "__main__":
    FuncAnyArgs(lambda x, y: print(x, y), 'default')(0)

    import random

    fc = FuncCache()
    print([(lambda x: fc(lambda: x + random.randint(0, 100)))(i) for i in range(10)])
    print([(lambda x: fc.test(lambda: x + random.randint(0, 100)))(i) for i in range(10)])


    def test(): return random.randint(0, 100)


    print([(lambda x: fc(test))(i) for i in range(10)])
