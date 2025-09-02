import json
from ...dict import assign
from ..res import path_js
from .polyfill import btoa

try:
    from .expression.quickjs import exec_js

    exec_js_safe = exec_js
except ImportError as e:
    if "'quickjs'" not in e.args[0]:
        raise
    from .expression.playwright import exec_js, exec_js_safe


def minify_js(s, kwargs=None, safe=False):
    func = exec_js_safe if safe else exec_js
    kwargs = assign({"output": {"comments": False}}, kwargs or {})
    return func(
        """var result = minify_sync(atob('%s'), %s);return result.code""" % (btoa(s), json.dumps(kwargs)),
        paths=[path_js / 'terser.js'])
