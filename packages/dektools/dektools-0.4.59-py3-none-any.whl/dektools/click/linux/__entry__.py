from . import app
from . import ppa as ppa_command

app.add_typer(ppa_command.app, name='ppa')
