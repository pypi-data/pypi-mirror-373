class AttrBase:
    new_cls = None

    def __init__(self, *attrs):
        self.attrs = attrs

    def __getattr__(self, attr):
        return (self.new_cls or self.__class__)(*self.attrs, (attr, True))

    def __getitem__(self, attr):
        return (self.new_cls or self.__class__)(*self.attrs, (attr, False))


class Attr(AttrBase):
    def __call__(self, instance):
        cursor = instance
        for attr, ga in self.attrs:
            if not ga:
                cursor = cursor[attr]
            else:
                if hasattr(cursor, attr):
                    cursor = getattr(cursor, attr)
                else:
                    cursor = cursor[attr]
        return cursor


class AttrProxy(AttrBase):
    new_cls = Attr
