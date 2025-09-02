import sys
import typer
from typing_extensions import Annotated
from ..typer import command_mixin

app = typer.Typer(add_completion=False)


@app.command()
def sure(path: Annotated[str, typer.Argument()] = "", url=""):
    from ..venvx.tools import find_venv_bin
    from ..shell import shell_exitcode, shell_wrapper
    from ..download import download_from_http
    from ..file import write_file

    python = find_venv_bin('python', path or None)
    if not python:
        python = sys.executable
    if shell_exitcode(f"{python} -m pip"):
        url = url or 'https://bootstrap.pypa.io/get-pip.py'
        path_pip = download_from_http(url, write_file())
        shell_wrapper(f'{python} "{path_pip}"')


@command_mixin(app)
def install(args, path=''):
    from ..venvx.tools import find_venv_bin
    from ..shell import shell_wrapper

    python = find_venv_bin('python', path or None)
    if not python:
        python = sys.executable
    shell_wrapper(f'{python} -m pip install {args}')
