from .dict import is_dict, dict_merge


class DeriveValue:
    def __init__(self, value):
        self.value = value


def trans_context(context):
    result = {}
    for k in sorted(context.keys(), key=lambda x: len(x) if isinstance(x, str) else -1):
        value = context[k]
        cursor = result
        key = k
        if k is not None:
            keys = k.split('.')
            for key in keys[:-1]:
                cursor = cursor.setdefault(key, {})
            key = keys[-1]
        if is_dict(value):
            cursor = cursor.setdefault(key, {})
            dict_merge(cursor, trans_context(value))
        else:
            cursor[key] = value
    return result


def derive_cls(cls, context):
    return _derive_cls(cls, trans_context(context))


def _derive_cls(cls, context):
    attrs = {}
    for k, v in context.items():
        if is_dict(v):
            cls_child = v.pop(None, None)
            if cls_child is None:
                cls_child = getattr(cls, k)
            cls_new = _derive_cls(cls_child, v)
        else:
            if isinstance(v, DeriveValue):
                v = v.value
            cls_new = v
        attrs[k] = cls_new
    return type(cls.__name__, (cls,), attrs)


def extend_cls_list(array, *cls_list):
    array = array[:]
    for cls in cls_list:
        for i in range(len(array)):
            if issubclass(cls, (array[i],)):
                array[i] = cls
                break
        else:
            array.insert(0, cls)
    return array


if __name__ == '__main__':
    class A:
        pass


    class AA:
        pass


    class B:
        a_cls = A
        aa_cls = AA


    class C:
        b_cls = B
        aa_cls = AA


    class A1:
        pass


    class A2:
        pass


    class B1(B):
        a_cls = A2


    test = derive_cls(C, {
        'b_cls': B1,
        'b_cls.a_cls': A1,
        'b_cls.aa_cls': A2,
        'aa_cls': A2,
    })

    print(test.b_cls)
    print(test.b_cls.a_cls)
    print(test.aa_cls)
