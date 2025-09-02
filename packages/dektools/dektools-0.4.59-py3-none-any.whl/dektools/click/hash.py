import os
import sys
import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)

default_args = {
    'shake_128': (32,),
    'shake_256': (32,)
}


@app.command()
def summary(path: Annotated[str, typer.Argument()] = ".", deep: bool = False):
    from ..file import normal_path
    from ..hash import hash_file, algorithms

    path = normal_path(path)
    if os.path.isdir(path):
        for fn in os.listdir(path):
            pfn = os.path.join(path, fn)
            if deep or os.path.isfile(pfn):
                summary(pfn)
    else:
        sys.stdout.write(os.path.basename(path) + ' :\n')
        for algorithm in algorithms:
            sys.stdout.write(f'   {algorithm}: {hash_file(algorithm, path, args=default_args.get(algorithm))}\n')
        sys.stdout.flush()


@app.command()
def file(path: Annotated[str, typer.Argument()] = ".", algorithm: Annotated[str, typer.Argument()] = 'sha256'):
    from ..file import normal_path
    from ..hash import hash_file

    print(hash_file(algorithm, normal_path(path), args=default_args.get(algorithm)), end='', flush=True)
