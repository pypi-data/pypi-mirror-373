import os
from .file import read_text


def get_whl_name(path):
    return os.path.basename(path).rsplit('-', 4)[0]


def eval_lines(s, context=None):
    globals_ = {} if context is None else context
    locals_ = {}
    exec(s, globals_, locals_)
    return locals_


def eval_file(filepath, context=None):
    return eval_lines(read_text(filepath, default=''), context)
