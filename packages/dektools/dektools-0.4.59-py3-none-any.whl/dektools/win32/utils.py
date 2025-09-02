import win32process
import win32ui
import win32gui
import win32con
import win32api
import winxpgui
import pywintypes
from functools import partial
from ctypes import windll, c_ulong, byref, wintypes, create_string_buffer
from ..common import xvalue

try:
    from PIL import Image
except ImportError:
    pass

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi


def close_handle(handle):
    kernel32.CloseHandle(handle)


def get_wnd_fg():
    return user32.GetForegroundWindow()


def get_wnd_focus():
    try:
        wnd = user32.GetForegroundWindow()
        tid_self = win32api.GetCurrentThreadId()
        tid, pid = win32process.GetWindowThreadProcessId(wnd)
        if tid != tid_self:
            win32process.AttachThreadInput(tid, tid_self, True)
            hwnd = win32gui.GetFocus()
            win32process.AttachThreadInput(tid, tid_self, False)
            return hwnd
        return win32gui.GetFocus()
    except pywintypes.error:
        return 0


def get_wnd_top_list():
    def enum(wnd, _):
        if not win32gui.GetParent(wnd) and win32gui.IsWindowVisible(wnd) and win32gui.GetWindowText(wnd):
            top_list.append(wnd)

    top_list = []
    win32gui.EnumWindows(enum, None)
    return top_list


def enum_wnd(cb):
    def enum(wnd, _):
        nonlocal end
        if not end:
            end = cb(wnd)
            if not end:
                win32gui.EnumChildWindows(wnd, enum_child, None)

    def enum_child(wnd, _):
        nonlocal end
        if not end:
            end = cb(wnd)

    end = None
    win32gui.EnumWindows(enum, None)
    return end


def get_wnd_rect(wnd):
    ratio_x, ratio_y = 1, 1
    left, top, right, bottom = win32gui.GetWindowRect(wnd)
    width = int((right - left) * ratio_x)
    height = int((bottom - top) * ratio_y)
    return left, top, width, height


def get_wnd_title(wnd):
    text = win32gui.GetWindowText(wnd)
    if text:
        return text
    else:
        buf = win32gui.PyMakeBuffer(255)
        length = win32gui.SendMessage(wnd, win32con.WM_GETTEXT, 255, buf)
        result = buf.tobytes()[:length * 2:2]
        try:
            return result.decode("utf-8")
        except UnicodeDecodeError:
            return ''


def query_wnd(query, limit=None):
    """
    :param query: {'parent': {...query}, index: None, caption:None, class:None}
    :param limit: set(), pick from limit if limit is not empty
    :return: None,set(),int->wnd
    """

    def cb_caption(caption_, limit_, wnd_):
        if get_wnd_title(wnd_) == caption_:
            if not limit_ or wnd_ in limit_:
                result.add(wnd_)

    def cb_cls(cls_, limit_, wnd_):
        if win32gui.GetClassName(wnd_) == cls_:
            if not limit_ or wnd_ in limit_:
                result.add(wnd_)

    def get_children(wnd__):
        def enum_child(wnd_, _):
            s.append(wnd_)

        s = []
        win32gui.EnumChildWindows(wnd__, enum_child, None)
        return s

    if not limit:
        limit = set()
    if isinstance(query, str):
        query = {'caption': query}
    result = set()
    caption = query.get('caption')
    if caption:
        limit = set(limit)
        result = set()
        enum_wnd(partial(cb_caption, caption, limit))
        limit = result
    cls = query.get('cls')
    if cls:
        limit = set(limit)
        result = set()
        enum_wnd(partial(cb_cls, cls, limit))
        limit = result
    parent = query.get('parent')
    index = query.get('index')
    if parent:
        limit = set(limit)
        result = set()
        ps = query_wnd(parent)
        if not ps:
            return None
        elif isinstance(ps, set):
            for p in ps:
                children = get_children(p)
                if index is None:
                    if wnd in children:
                        if not limit or wnd in limit:
                            result.add(wnd)
                else:
                    try:
                        wnd = children[index]
                    except IndexError:
                        wnd = None
                    if wnd:
                        if not limit or wnd in limit:
                            result.add(wnd)
    return list(result)


def set_wnd_layered(hwnd, alpha=None, color=None):
    mask = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if not mask & win32con.WS_EX_LAYERED:
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED
        )
    a = 0
    b = 0
    flag = 0
    if color is not None:
        a = color
        flag |= win32con.LWA_COLORKEY
    if alpha is not None:
        b = int(alpha * 255)
        flag |= win32con.LWA_ALPHA
    if flag:
        winxpgui.SetLayeredWindowAttributes(hwnd, a, b, flag)


def set_wnd_top(hwnd, value=None):
    x, y, w, h = get_wnd_rect(hwnd)
    mask = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if value is None:
        if mask & win32con.WS_EX_TOPMOST:
            value = win32con.HWND_NOTOPMOST
        else:
            value = win32con.HWND_TOPMOST
    else:
        value = win32con.HWND_TOPMOST if value else win32con.HWND_NOTOPMOST
    win32gui.SetWindowPos(hwnd, value, x, y, w, h, 0)
    return value == win32con.HWND_TOPMOST


def get_proc_id_by_wnd(hwnd):
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    return pid  # pid.value is the integer value of process ID


def get_proc(pid, flags=0x400 | 0x10):
    return kernel32.OpenProcess(flags, False, pid)


def get_proc_id(handle_proc):
    return kernel32.GetProcessId(handle_proc)


def get_proc_name(handle_proc, length=512, encoding='utf-8'):
    proc_name = create_string_buffer(b'\x00' * length)
    psapi.GetModuleBaseNameA(handle_proc, None, byref(proc_name), length)
    return proc_name.value.decode(encoding)


def get_work_area_rect():
    work_area = wintypes.RECT()
    if windll.user32.SystemParametersInfoA(win32con.SPI_GETWORKAREA, 0, byref(work_area), 0):
        return work_area.left, work_area.top, work_area.right - work_area.left, work_area.bottom - work_area.top


def get_default_taskbar_rect():
    cx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    cy = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    wa = get_work_area_rect()
    height = max(abs(cx - wa[2]), abs(cy - wa[3]))
    return 0, cy - height, cx, height


def get_wnd_fold(hwnd=None):
    _GetDpiForWindow = getattr(windll.user32, 'GetDpiForWindow', None)
    if _GetDpiForWindow and hwnd:
        return _GetDpiForWindow(hwnd) / 96
    else:
        dm = win32api.EnumDisplaySettings(
            win32api.EnumDisplayDevices(DevNum=0).DeviceName, win32con.ENUM_CURRENT_SETTINGS)
        cx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        return dm.PelsWidth / cx


def bitmap2pil(bitmap):
    info = bitmap.GetInfo()
    return Image.frombuffer('RGB', (info['bmWidth'], info['bmHeight']), bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)


def get_wnd_image(hwnd=None, w=None, h=None):
    if hwnd is None:
        hwnd = win32gui.GetDesktopWindow()

    fold = 1  # get_wnd_fold(hwnd)

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    bitmap_w = int(width * fold)
    bitmap_h = int(height * fold)
    img_w = xvalue(bitmap_w, w)
    img_h = xvalue(bitmap_h, h)

    dc = win32gui.GetWindowDC(hwnd)
    dc_fh = win32ui.CreateDCFromHandle(dc)
    dc_c = dc_fh.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(dc_fh, bitmap_w, bitmap_h)
    dc_c.SelectObject(bitmap)
    dc_c.StretchBlt((0, 0), (img_w, img_h), dc_fh, (0, 0), (bitmap_w, bitmap_h), win32con.SRCCOPY)
    img = bitmap2pil(bitmap)
    dc_c.DeleteDC()
    dc_fh.DeleteDC()
    win32gui.DeleteObject(bitmap.GetHandle())
    win32gui.ReleaseDC(hwnd, dc)
    return img
