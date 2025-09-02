import os
import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)

path_sources_list = '/etc/apt/sources.list.d'
host_origin = 'ppa.launchpadcontent.net'
host_mirror = 'launchpad.proxy.ustclug.org'


def _get_release():
    from ...shell import shell_output

    return shell_output('lsb_release -cs')


@app.command()
def replace(mirror: Annotated[str, typer.Argument()] = '', origin='', path=''):
    from ...file import write_file, read_text, iter_relative_path

    path = path or path_sources_list
    origin = origin or host_origin
    mirror = mirror or host_mirror

    for _, fp in iter_relative_path(path):
        txt = read_text(fp)
        if origin in txt:
            write_file(fp, s=txt.replace(origin, mirror))


@app.command()
def add(name, host: Annotated[str, typer.Argument()] = '', components='', path=''):
    from ...file import write_file

    path = path or path_sources_list
    host = host or host_mirror
    components = components or 'main'

    namespace, software = name.split('/')
    release = _get_release()
    target = os.path.join(path, f'{namespace}-ubuntu-{software}-{release}.list')
    url = f"https://{host}/{namespace}/{software}/ubuntu/ {release} {components}"

    write_file(target, s=f'deb {url}\n# deb-src {url}')


@app.command()
def remove(name, path: Annotated[str, typer.Argument()] = ''):
    from ...file import remove_path

    path = path or path_sources_list
    namespace, software = name.split('/')
    release = _get_release()
    target = os.path.join(path, f'{namespace}-ubuntu-{software}-{release}.list')

    remove_path(target)
