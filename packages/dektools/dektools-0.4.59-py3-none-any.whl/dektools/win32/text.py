import win32gui
import win32con
import win32api
import win32ui
from .base import Window
from .utils import get_default_taskbar_rect, set_wnd_top, set_wnd_layered


class WindowText(Window):
    def __init__(self, color=None, **kwargs):
        super().__init__(timer=True, **kwargs)
        self._color = win32api.RGB(*((236, 76, 140) if color is None else color))
        self._text = ''
        self._rect = get_default_taskbar_rect()

    def create(self, **kwargs):
        return super().create(
            cs=0,
            es=win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW,
            ws=win32con.WS_POPUP,
            rect=self._rect,
            **kwargs)

    def set_text(self, text):
        if text != self._text:
            self._text = text
            return True
        return False

    def wm_paint(self):
        hdc, ps = win32gui.BeginPaint(self.hwnd)
        win32gui.FillRect(hdc, win32gui.GetClientRect(self.hwnd), win32gui.GetSysColorBrush(win32con.COLOR_WINDOW))
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
        win32gui.SetTextColor(hdc, self._color)
        hfont = win32ui.CreateFont({"height": int(self._rect[3] / 2 * 0.75)})
        win32gui.SelectObject(hdc, hfont.GetSafeHandle())
        w, h = win32gui.GetTextExtentPoint32(hdc, self._text)
        x = self._rect[2] // 2 - w // 2
        y = self._rect[3] // 2 - h // 2
        win32gui.ExtTextOut(hdc, x, y, win32con.ETO_OPAQUE, (0, 0, 0, 0), self._text)
        win32gui.EndPaint(self.hwnd, ps)
        win32gui.DeleteObject(hfont.GetSafeHandle())


class PickerWindow(WindowText):
    def on_created(self):
        def timer_top():
            set_wnd_top(self.hwnd, False)
            set_wnd_top(self.hwnd, True)

        def timer_redraw():
            pos = win32api.GetCursorPos()
            hdc = win32gui.GetDC(win32gui.GetDesktopWindow())
            color = win32gui.GetPixel(hdc, *pos)
            win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)
            text = f"{pos[0]},{pos[1]} #{'%X' % color}"
            if self.set_text(text):
                win32gui.RedrawWindow(self.hwnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_INTERNALPAINT)

        set_wnd_layered(self.hwnd, 0.5, win32api.RGB(255, 255, 255))
        self.timer.set_interval(timer_redraw, 0.01, None)
        self.timer.set_interval(timer_top, 1, None)
