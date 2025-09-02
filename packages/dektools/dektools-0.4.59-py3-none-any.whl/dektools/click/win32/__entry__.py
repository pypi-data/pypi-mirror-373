from . import app
from . import wnd as wnd_command

app.add_typer(wnd_command.app, name='wnd')
