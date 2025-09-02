import time
import typer

app = typer.Typer(add_completion=False)


@app.command()
def sleep(seconds: float):
    time.sleep(seconds)
