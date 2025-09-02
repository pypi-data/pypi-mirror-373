import typing
import typer

app = typer.Typer(add_completion=False)


@app.command()
def generate(out, env=None, prefix=None, file: typing.Optional[typing.List[str]] = typer.Option(None)):
    from ..serializer.yaml import yaml
    from ..file import read_text
    from ..cfg import AssignCfg

    if env:
        env = read_text(env)
    data = AssignCfg(prefix=prefix, dotenv=env, *(yaml.load(f) for f in file)).generate()
    yaml.dump(out, data)
