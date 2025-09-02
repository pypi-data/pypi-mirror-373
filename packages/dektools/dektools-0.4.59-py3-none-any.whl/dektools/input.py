import sys
import threading
import traceback
from .module import ModuleProxy
from .output import obj2str


class InputEval:
    eval = eval
    recommend_variables = {
        'mp': ModuleProxy(),
        'o2s': obj2str,
    }

    def __init__(self, variables=None, stdin=None):
        self._need_quit = False
        self._stdin = stdin or sys.stdin
        self._variables = variables or {}
        input_thread = threading.Thread(target=self.__read_input, args=(), daemon=True)
        input_thread.start()

    def quit(self):
        self._need_quit = True

    def __read_input(self):
        while not self._need_quit:
            code = self._stdin.readline()
            code = code.strip()
            if code:
                try:
                    result = self.eval(code, self._variables)
                except Exception as e:
                    print(''.join(traceback.format_exception(e)), file=sys.stderr, flush=True)
                    continue
                if result is not None:
                    print(result, flush=True)


try:
    from async_eval import eval as eval_async
except ImportError as e:
    if "'async_eval'" in e.args[0]:
        pass
    else:
        raise
    eval_async = None

if eval_async:
    class AsyncInputEval:
        eval = eval_async
