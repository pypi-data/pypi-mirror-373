# https://github.com/odoo/odoo/blob/fa6a577cc95b604ae3684010107cf5d04a3ce078/odoo/tools/safe_eval.py
# RestrictedPython
# evalidate
import builtins
from RestrictedPython import compile_restricted_eval, compile_restricted_exec, safe_builtins, limited_builtins, \
    utility_builtins
from .match import GeneralMatcher
from .common import cached_property

tool_builtins = {name: getattr(builtins, name) for name in (
    'dict', 'enumerate', 'filter', 'getattr', 'hasattr', 'iter',
    'list', 'map', 'max', 'min', 'sum', 'all', 'any')}


class ExprExecutor:
    import_checker_cls = GeneralMatcher

    builtins_map = {
        'safe': safe_builtins,
        'limited': limited_builtins,
        'utility': utility_builtins,
        'tool': tool_builtins,
    }

    def __init__(self, builtins=None, imports=None):
        self.builtins = builtins
        self.import_match = self.import_checker_cls('.', imports).new_match()

    def guarded_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if self.import_match(name):
            module = __import__(name, globals, locals, fromlist, level)
            return module
        raise ImportError(f"Import not allowed: {name}")

    @cached_property
    def safe_globals(self):
        all_builtins = {}
        if self.builtins:
            keys = self.builtins
        else:
            keys = self.builtins_map.keys()
        for key in keys:
            all_builtins.update(self.builtins_map[key])
        return {'__builtins__': {**all_builtins, '__import__': self.guarded_import}}

    def eval_safe(self, code, globals=None, locals=None, delay=False):
        def func():
            return eval(code.code, restricted_globals, locals)

        restricted_globals = dict(**self.safe_globals, **(globals or {}))
        code = compile_restricted_eval(code)
        if code.errors:
            return None, code.errors
        if not delay:
            try:
                return func(), None
            except Exception as e:
                return None, e
        return func, None

    @staticmethod
    def eval_unsafe(code, globals=None, locals=None, delay=False):
        def func():
            return eval(code, globals, locals)

        if not delay:
            try:
                return func(), None
            except Exception as e:
                return None, e
        return func, None

    def exec_safe(self, code, result, globals=None, locals=None, delay=False):
        def func():
            exec(code.code, restricted_globals, locals)
            if locals and result:
                if isinstance(result, str):
                    return locals[result]
                else:
                    return [locals[name] for name in result]

        restricted_globals = dict(**self.safe_globals, **(globals or {}))
        code = compile_restricted_exec(code)
        if code.errors:
            return None, code.errors
        if not delay:
            try:
                return func(), None
            except Exception as e:
                return None, e
        return func, None

    @staticmethod
    def exec_unsafe(code, result, globals=None, locals=None, delay=False):
        def func():
            exec(code, globals, locals)
            if locals and result:
                if isinstance(result, str):
                    return locals[result]
                else:
                    return [locals[name] for name in result]

        if not delay:
            try:
                return func(), None
            except Exception as e:
                return None, e
        return func, None
