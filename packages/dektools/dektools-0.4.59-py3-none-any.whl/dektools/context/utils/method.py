class Method:
    def __getattr__(self, method):
        return Method2(method)


class Method2:
    def __init__(self, method):
        self.method = method
        self.args = []
        self.kwargs = {}

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return Method3(self)


class Method3:
    def __init__(self, m2):
        self.m2 = m2

    def __call__(self, instance):
        return getattr(instance, self.m2.method)(*self.m2.args, **self.m2.kwargs)


class MethodSimple:
    def __getattr__(self, method):
        return Method3(Method2(method))
