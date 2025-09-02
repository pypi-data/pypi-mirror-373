import json
from .module import get_module_attr


def _get_cls_path(cls):
    return f'{cls.__module__}.{cls.__name__}'


def obj_like_json(obj):
    try:
        json.dumps(obj)
        return True
    except TypeError:
        return False


def obj_dump_text(obj):
    if obj_like_json(obj):
        return repr(obj)
    else:
        if isinstance(obj, type):
            return _get_cls_path(obj)
        else:
            r = repr(obj)
            args = r.split('(', 1)[1]
            return f'{_get_cls_path(obj.__class__)}({args}'


def text_load_obj(text):
    if not isinstance(text, str):
        return text
    if text.find('(') > 0 and text[-1:] == ')':
        path_attr, args = text.split('(', 1)
        cls = get_module_attr(path_attr)
        return eval(f'{cls.__name__}({args}', {cls.__name__: cls})
    else:
        return eval(text)


class TextLoadObj:
    @staticmethod
    def locals():
        return {
            text_load_obj.__name__: text_load_obj
        }

    def __init__(self, args):
        self.args = args

    def __repr__(self):
        return f'{text_load_obj.__name__}({self.args})'
