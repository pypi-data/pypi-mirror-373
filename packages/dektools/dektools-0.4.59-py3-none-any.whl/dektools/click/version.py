import typer

app = typer.Typer(add_completion=False)


@app.command()
def extract(version):
    from ..version import version_extract
    print(version_extract(version), end='', flush=True)
