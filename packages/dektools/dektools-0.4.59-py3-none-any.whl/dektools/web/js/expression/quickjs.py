from quickjs import Function
from dektools.file import read_text
from ..polyfill import atob


def exec_js(s, codes=None, paths=None):
    items = []
    if codes:
        for code in codes:
            items.append(code)
    if paths:
        for path in paths:
            items.append(read_text(path))

    f = Function("f", """%s\n function f(){%s}""" % ('\n'.join(items), s))
    f.add_callable('atob', atob)
    return f()
