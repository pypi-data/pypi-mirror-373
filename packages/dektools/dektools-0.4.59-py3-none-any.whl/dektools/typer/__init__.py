import os
import inspect
import typing
import typer
import click
import typing_extensions
from importlib import metadata
from ..typing import NoneType


def command_mixin(app, **kwargs):
    def wrapper(func):
        args = ''
        kw = ''
        kw_body = ''
        is_args = True  # skip first which is args
        for name, param in inspect.signature(func).parameters.items():
            if is_args:
                is_args = False
                continue
            if param.default is inspect.Parameter.empty:
                args += f',{name}'
            else:
                annotation = ''
                if param.annotation is not inspect.Parameter.empty:
                    annotation = ':' + repr(param.annotation)
                kw += f',{name}{annotation}={repr(param.default)}'
                kw_body += f',{name}={name}'
        locals_ = dict(
            typer=typer,
            typing_extensions=typing_extensions,
            NoneType=NoneType,
            click=click,
            typing=typing,
            func=func,
            trans=lambda xl: [x if x.strip() else f'"{x}"' for x in xl]
        )
        func_first_arg = "" if is_args else "' '.join(trans(ctx.args))"
        func_doc = '' if func.__doc__ is None else f'\n    """{func.__doc__}"""'
        func_return = f'return func({func_first_arg}{args}{kw_body})'
        exec(f'def {func.__name__}(ctx: typer.Context{args}{kw}):{func_doc}\n    {func_return}', locals_)
        return app.command(
            **{
                'context_settings': {"allow_extra_args": True, "ignore_unknown_options": True},
                **kwargs
            }
        )(locals_[func.__name__])

    return wrapper


def command_version(app, name):
    def main(ctx: typer.Context, version: bool = typer.Option(False, "--version", "-v")):
        if ctx.invoked_subcommand is not None:
            return
        if version:
            print(metadata.version(name.partition(".")[0]), end='')
            return

    return app.callback(invoke_without_command=True)(main)


def multi_options_to_dict(array, split='.'):
    result = {}
    for item in array:
        items = item.split('=', 1)
        k = items[0].strip()
        if split:
            kl = k.split(split)
        else:
            kl = [k]
        if len(items) == 1:
            v = ''
        else:
            v = items[1].strip()
        cursor = result
        for k in kl[:-1]:
            if k not in cursor:
                cursor[k] = {}
            cursor = cursor[k]
        cursor[kl[-1]] = v
    return result


def filter_files(files):
    if files:
        for f in files:
            strict = True
            if f.startswith('?'):
                f = f[1:]
                strict = False
            if not strict and not os.path.isfile(f):
                continue
            yield f


def load_yaml_files(files):
    from ..dict import dict_merge
    from ..serializer.yaml import yaml

    data = {}
    for file in filter_files(files):
        dict_merge(data, yaml.load(file) or {})
    return data

#############################################################
# no sub command
# @app.callback(invoke_without_command=True)
# def show(ctx: typer.Context, visible=False):
#     if ctx.invoked_subcommand is None:
#         typer.echo(f"Just for no subcommand")

#############################################################
# no accepting args, get args from sys.argv
# @app.command(
#     context_settings=dict(resilient_parsing=True)
# )

#############################################################
# https://typer.tiangolo.com/tutorial/commands/one-or-multiple/#one-command-and-one-callback
# one command and one callback
# @app.callback()
# def callback():
#     pass

#############################################################
# default option
# @app.command()
# def show(
#     index: Annotated[int, typer.Option()] = 0
# ):
#     pass

#############################################################
# boolean option
# @app.command()
# def show(
#     visible: Annotated[bool, typer.Option("--visible/--no-visible")] = True
# ):
#     pass
#
# @app.command()
# def show(
#     visible: bool = True,
# ):
#     pass
#

#############################################################
# one option for multi times
# @app.command()
# def push(paths: Annotated[Optional[List[str]], typer.Option('--path')] = None):
#     pass

#############################################################
# one argument accepted multi times
# @app.command()
# def pull(paths: Annotated[List[str], typer.Argument()] = None):
#     pass
#
# *Required arguments
# @app.command()
# def pull(paths: List[str]):
#     pass

#############################################################
# default arguments
# @app.command()
# def show(
#     name: Annotated[str, typer.Argument()] = "tests"
# ):
#     pass

#############################################################
# supporting verbose
# @app.command()
# def log(verbose: bool = typer.Option(False, "--verbose", "-v")):
#     if verbose:
#         logging.basicConfig(level=logging.DEBUG)
#
