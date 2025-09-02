import os
import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)


@app.command()
def clean(path):
    from ..cmd.git import git_clean_dir
    git_clean_dir(path)


@app.command()
def fetch_min(url, tag, path):
    from ..cmd.git import git_fetch_min
    git_fetch_min(url, tag, path)


@app.command()
def remove_tag(tag, path: Annotated[str, typer.Argument()] = ""):
    from ..cmd.git import git_remove_tag
    git_remove_tag(tag, path)


@app.command()
def latest_tag(path: Annotated[str, typer.Argument()] = ""):
    from ..cmd.git import git_latest_tag
    print(git_latest_tag(path) or '', end='')


@app.command()
def apply(
        src, dst,
        reverse: bool = typer.Option(False, "--reverse", "-r"),
        status: bool = typer.Option(False, "--status", "-s"),
        ignore: bool = typer.Option(False, "--ignore", "-i")):
    from ..cmd.git import git_apply
    git_apply(src, dst, reverse, status, ignore)


@app.command()
def gh_wf(path: Annotated[str, typer.Argument()] = ""):
    from ..serializer.yaml import Yaml, Resolver
    from ..file import normal_path
    yaml = Yaml(resolvers=Resolver.ordereddict, dumper=dict(ignore_aliases=Resolver.attrs.ignore_aliases))
    path = normal_path(path or os.getcwd())
    path_src = os.path.join(path, '.github', '.workflows')
    path_dest = os.path.join(path, '.github', 'workflows')
    for base, _, files in os.walk(path_src):
        for file in files:
            p = os.path.join(base, file)
            if os.path.splitext(p)[-1] in ['.yml', '.yaml']:
                yaml.dump(path_dest + p[len(path_src):], yaml.load(p))
