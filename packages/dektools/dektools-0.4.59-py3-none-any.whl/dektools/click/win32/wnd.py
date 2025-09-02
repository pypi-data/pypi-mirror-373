import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)


@app.command()
def alpha(title: str, a: float):
    from ...win32.utils import set_wnd_layered, query_wnd
    hwnd_list = query_wnd(title)
    if hwnd_list:
        set_wnd_layered(hwnd_list[0], alpha=a)


@app.command(name='list')
def list_(title: Annotated[str, typer.Argument()] = ''):
    from ...win32.utils import enum_wnd, get_wnd_title

    def cb(hwnd):
        t = get_wnd_title(hwnd)
        if t and (not title or title in t):
            print(t, flush=True)

    enum_wnd(cb)


@app.command()
def top(title: str):
    from ...win32.utils import query_wnd, set_wnd_top

    hwnd_list = query_wnd(title)
    if hwnd_list:
        set_wnd_top(hwnd_list[0])


@app.command()
def picker():
    from dektools.win32.text import PickerWindow

    wind = PickerWindow().create()
    wind.loop()
