import sys
import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)


@app.command()
def fetch(url, path: Annotated[str, typer.Argument()] = "", username: str = None, password: str = None):
    from ..fetch import download_file
    download_file(url, path or None, username, password)


@app.command()
def download(url, path: Annotated[str, typer.Argument()] = "", username: str = None, password: str = None):
    from ..download import download_from_http
    download_from_http(url, path or None, username, password)


@app.command()
def git(url, path):
    from ..download import download_from_git
    download_from_git(url, path)


@app.command()
def exists(url, username: str = None, password: str = None):
    from ..download import download_http_exist
    if download_http_exist(url, username, password):
        sys.exit(0)
    else:
        sys.exit(1)
