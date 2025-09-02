import os
import sys
import re
import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)


@app.command(name='port')
def port_(port, host: Annotated[str, typer.Argument()] = ""):
    from ..net import is_port_in_use
    if is_port_in_use(int(port), host or None):
        print('using', end='', flush=True)
    else:
        print('free', end='', flush=True)


@app.command()
def get_port(port: Annotated[int, typer.Argument()] = None, host: Annotated[str, typer.Argument()] = ""):
    from ..net import get_available_port
    print(get_available_port(port or None, host or None), end='', flush=True)


@app.command()
def ips():
    from ..net import get_local_ip_list
    print(' '.join(get_local_ip_list()), end='', flush=True)


@app.command()
def ip(ipv6: bool = typer.Option(False, "--ipv6", "-6")):
    from ..net import get_interface_ip
    print(get_interface_ip(ipv6), end='', flush=True)


_serve_fetch_port = 8880


@app.command()
def serve(
        path: Annotated[str, typer.Argument()] = "",
        safe: bool = False,
        host: str = '', port: int = _serve_fetch_port):
    from ..net import get_interface_ip
    from ..shell import shell_wrapper
    path = path or os.getcwd()
    cmd = f'{sys.executable} -m http.server -d "{path}" '
    if host:
        cmd += f'-b {host}'
    else:
        if safe:
            cmd += '-b 127.0.0.1'
        else:
            cmd += '-b 0.0.0.0'
    cmd += f" {port}"
    print('Local ip list:')
    print(get_interface_ip(), flush=True)
    shell_wrapper(cmd)


@app.command()
def fetch(
        server: Annotated[str, typer.Argument()] = "",
        path: Annotated[str, typer.Argument()] = "",
        port: int = _serve_fetch_port):
    from ..file import sure_dir, normal_path
    from ..fetch import download_content, download_file
    server = server or 'localhost'
    if server == 'localhost' or re.fullmatch('[0-9]+.[0-9]+.[0-9]+.[0-9]+', server):
        server = f"http://{server}:{port}"
    server = server.rstrip('/')
    server += '/'
    path = normal_path(path or os.getcwd())
    sure_dir(path)

    def walk(node):
        index = download_content(node).decode('utf-8')
        items = re.findall(r'<a href="([\s\S]+?)">', index)
        files = []
        dirs = []
        for item in items:
            if item.endswith('/'):
                dirs.append(item)
            else:
                files.append(item)
        for f in files:
            download_file(node + f, os.path.join(path, node[len(server):], f))
        for d in dirs:
            walk(node + d)

    walk(server)
