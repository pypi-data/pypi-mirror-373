import sys
from . import app
from . import hash as hash_command
from . import file as file_command
from . import net as net_command
from . import version as version_command
from . import cfg as cfg_command
from . import url as url_command
from . import utils as utils_command
from . import cmd as cmd_command
from . import data as data_command
from . import fetch as fetch_command
from .win32 import __entry__ as win32_command
from .linux import __entry__ as linux_command

from ..typer import command_version, command_mixin

command_version(app, __name__)
app.add_typer(hash_command.app, name='hash')
app.add_typer(file_command.app, name='file')
app.add_typer(net_command.app, name='net')
app.add_typer(version_command.app, name='version')
app.add_typer(cfg_command.app, name='cfg')
app.add_typer(url_command.app, name='url')
app.add_typer(utils_command.app, name='utils')
app.add_typer(cmd_command.app, name='cmd')
app.add_typer(data_command.app, name='data')
app.add_typer(fetch_command.app, name='fetch')
app.add_typer(win32_command.app, name='win32')
app.add_typer(linux_command.app, name='linux')


@command_mixin(app)
def echo(args):
    print(args, file=sys.stdout, flush=True)


@command_mixin(app)
def echox(args):
    print(args, file=sys.stderr, flush=True)


def main():
    app()
