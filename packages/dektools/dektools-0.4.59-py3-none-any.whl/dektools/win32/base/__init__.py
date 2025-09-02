import win32api
import win32con
import win32gui
from ctypes import windll
from ...func import FuncAnyArgs
from ...str import hex_random
from ...attr import DictObj
from ...timer import TimerInLoop

SetTimer = windll.user32.SetTimer

windll.user32.SetProcessDPIAware()
win32gui.InitCommonControls()


class Window:
    wnd_class_name = None
    h_module_ins = win32api.GetModuleHandle(None)
    share_cls = DictObj
    timer_cls = TimerInLoop

    def __init__(self, main=True, timer=False):
        self._main = main
        self._share = self.share_cls()
        self.hwnd = None
        self._class_atom = None
        self.timer = self.timer_cls() if timer else None

    def create(self, title='', rect=None, cs=None, es=None, ws=None, show=True):
        cs = win32con.CS_GLOBALCLASS | win32con.CS_VREDRAW | win32con.CS_HREDRAW \
            if cs is None else cs
        ws = win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_SYSMENU \
            if ws is None else ws
        class_name = hex_random(32) if self.wnd_class_name is None else self.wnd_class_name
        wc = win32gui.WNDCLASS()
        wc.style = cs
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        # wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = self.collect_messages_handlers()
        wc.lpszClassName = class_name
        self._class_atom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindowEx(
            0 if es is None else es,
            self._class_atom,
            title,
            ws,
            *self.normalize_rect(rect),
            0,
            0,
            self.h_module_ins,
            None
        )
        if self.timer is not None:
            SetTimer(self.hwnd, 0, 1, None)
        self.on_created()
        if show:
            self.show()
        return self

    def on_created(self):
        pass

    def show(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def collect_messages_handlers(self):
        result = {}
        for attr in dir(self):
            if attr.startswith('wm_'):
                prefix, name = attr.split('_', 1)
                name = name.replace('_', '')
                message_name = f'{prefix}_{name}'.upper()
                result[getattr(win32con, message_name)] = self.__pack_message_handler(attr)
        return result

    def __pack_message_handler(self, attr):
        def wrapper(hwnd, message, wparam, lparam):
            return FuncAnyArgs(getattr(self, attr))(wparam, lparam, message) or 0

        return wrapper

    def wm_close(self, wparam, lparam, message):
        win32gui.DestroyWindow(self.hwnd)
        if self._class_atom is not None:
            win32gui.UnregisterClass(self._class_atom, None)
        if self._main:
            self.quit_loop()

    def wm_timer(self):
        self.timer.peek()

    @staticmethod
    def loop():
        win32gui.PumpMessages()

    @staticmethod
    def loop_peek(func=None):
        msg = win32gui.MSG()
        while True:
            if win32gui.PeekMessage(msg, 0, 0, 0, win32con.PM_REMOVE):
                if msg.message == win32con.WM_QUIT:
                    break
                win32gui.TranslateMessage(msg)
                win32gui.DispatchMessage(msg)
            else:
                if func:
                    func()

    @staticmethod
    def quit_loop(exit_code=0):
        win32gui.PostQuitMessage(exit_code)

    @staticmethod
    def normalize_rect(rect):
        default = win32con.CW_USEDEFAULT
        if rect is None:
            rect = []
        elif isinstance(rect, str):
            rect = [int(float(x)) for x in rect.split(',')]
        elif isinstance(rect, (int, float)):
            rect = [int(rect)]
        length = len(rect)
        if length == 0:
            return [default] * 4
        elif length == 1:
            return [default] * 2 + [rect[0]] * 2
        elif length == 2:
            return [default] * 2 + list(rect)
        elif length == 3:
            return list(rect) + [default]
        return rect[:4]
