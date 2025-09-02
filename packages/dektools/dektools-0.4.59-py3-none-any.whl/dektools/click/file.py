import os
import glob
import typer
from typing import Optional, List
from typing_extensions import Annotated
from ..typer import command_mixin

app = typer.Typer(add_completion=False)


@app.command()
def hit_remove(path, ignore='.rmignore'):
    from ..file import normal_path, remove_path, FileHitChecker

    def walk(fp, is_hit, _):
        if not is_hit:
            remove_path(fp)

    path = normal_path(path)
    if os.path.isdir(path):
        FileHitChecker(path, ignore).walk(walk)
    elif os.path.isfile(path):
        if not FileHitChecker(os.path.dirname(path), ignore).new_match()(path):
            remove_path(path)


@app.command()
def merge(dest, src, ignore=None):
    from ..file import merge_assign, FileHitChecker

    if ignore:
        FileHitChecker(src, ignore).merge_dir(dest)
    else:
        merge_assign(dest, src)


@app.command(name='hash')
def _hash(path, name='sha256'):
    from ..hash import hash_file
    print(hash_file(name, path), end='', flush=True)


@app.command()
def desc(path):
    from ..file import format_path_desc, normal_path
    print(normal_path(path) + ' : ' + format_path_desc(path), flush=True)


@app.command()
def remove(filepath):
    from ..file import remove_path
    remove_path(filepath)


@app.command()
def clear(filepath):
    from ..file import clear_dir
    clear_dir(filepath)


@app.command()
def sure(filepath):
    from ..file import sure_dir, normal_path
    sure_dir(normal_path(filepath))


@app.command()
def write(
        filepath,
        s=None, b=None, sb=None, a=None,
        m=None, mi=None,
        c=None, ci=None,
        ma=None, mo=None, mie=None,
        t: bool = typer.Option(False, "--temp", "-t"),
        g=None,
        encoding='utf-8'):
    from ..file import write_file
    write_file(
        filepath,
        s=s, b=b, sb=sb, a=a,
        m=m, mi=mi,
        c=c, ci=ci,
        ma=ma, mo=mo, mie=mie,
        t=t, g=g,
        encoding=encoding
    )


@command_mixin(app, name='glob')
def glob_(args, path):
    from ..shell import shell_wrapper
    result = glob.glob(path, recursive=True)
    if result:
        shell_wrapper(args.format(filepath=result[-1]))


@command_mixin(app)
def globs(args, path):
    from ..shell import shell_wrapper
    result = glob.glob(path, recursive=True)
    for file in result:
        shell_wrapper(args.format(filepath=file))


@app.command()
def compress(src, dest):
    from ..zip import compress_files
    compress_files(src, dest)


@app.command()
def decompress(src, dest, combine: Annotated[bool, typer.Option("--combine/--no-combine")] = False):
    from ..zip import decompress_files
    decompress_files(src, dest, combine)


@app.command()
def backup(src, dest, ignore: Annotated[Optional[List[str]], typer.Option()] = None):
    from ..file import remove_path, copy_recurse_ignore
    from ..zip import compress_files
    path_out = copy_recurse_ignore(src, ignores=['.gitignore', *ignore])
    compress_files(path_out, dest)
    remove_path(path_out)


@app.command()
def real(path):
    from ..file import come_real_path
    come_real_path(path)


@app.command()
def split(path, limit: int):
    from ..file import split_file
    split_file(path, limit)


@app.command()
def meta_split(path):
    from ..file import meta_split_file, normal_path
    parts, checksum, total_size, path_meta = meta_split_file(path)
    print(f"Path: {normal_path(path)}", flush=True)
    print(f"Total size: {total_size} bytes", flush=True)
    print(f'Sh256: {checksum}', flush=True)
    print("All parts:", flush=True)
    print(path_meta, flush=True)
    for path_part in parts:
        print(path_part, flush=True)


@app.command()
def remove_split(path):
    from ..file import remove_split_files
    remove_split_files(path)


@app.command(name='combine')
def _combine(path, clear_: Annotated[bool, typer.Option("--clear/--no-clear")] = False):
    from ..file import combine_split_files
    combine_split_files(path, clear_)


@app.command()
def rc4(filepath, key):
    from ..file import rc4_file
    rc4_file(filepath, key)
