import json
import typer
from typing import Optional
from configparser import ConfigParser
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)

typed_map = {'json': {'.json'}, 'yaml': {'.yaml', '.yml'}, 'cfg': {'.ini', '.cfg'}}
typed_map_reversed = {ext: t for t, s in typed_map.items() for ext in s}


@app.command()
def echo(
        filepath,
        expression: Annotated[str, typer.Argument()] = '',
        typed: Annotated[Optional[str], typer.Option('--type')] = ''):
    from ..output import print_data_or_value

    print_data_or_value(_get_data(filepath, typed), expression)


@app.command()
def trans(
        filepath,
        fmt: Annotated[str, typer.Argument()] = None,
        out='',
        typed: Annotated[Optional[str], typer.Option('--type')] = ''):
    from ..shell import output_data
    from ..serializer.dyna.utils.finder import find_dyna_prefix

    if fmt == 'dyna.prefix':
        print(find_dyna_prefix(filepath) or '', end='', flush=True)
    else:
        output_data(_get_data(filepath, typed), out, fmt)


def _get_data(filepath, typed=None):
    from ..file import read_file, path_ext
    if not typed:
        ext = path_ext(filepath)
        typed = typed_map_reversed[ext]
    if typed == 'json':
        d = json.loads(read_file(filepath))
    elif typed == 'yaml':
        from ..serializer.yaml import yaml
        d = yaml.load(filepath)
    elif typed == 'cfg':
        parser = ConfigParser()
        parser.read(filepath)
        d = {section: dict(parser.items(section)) for section in parser.sections()}
    else:
        raise TypeError(f"Invalid type{filepath}: {typed}")
    return d
