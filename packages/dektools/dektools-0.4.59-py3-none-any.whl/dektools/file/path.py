import os
import sys
import uuid
import glob
from pathlib import Path
from ..format import format_file_size

glob_support_root = sys.version_info[:2] >= (3, 10)


def join_path(*args):
    return os.path.normpath(os.path.join(*(args[0], *(x.strip('\\/') for x in args[1:]))))


def normal_path(path, unix=False):
    path = os.path.normpath(os.path.abspath(os.path.expanduser(os.fspath(path))))
    if unix and os.name == 'nt':
        path = path.replace('\\', '/')
    return path


def new_empty_path(*paths):
    while True:
        np = f"{os.path.join(*paths)}.{uuid.uuid4().hex}"
        if not os.path.exists(np):
            return np


def first_path(path):
    for item in os.scandir(path):
        return os.path.join(path, item)


def split_ext(path):
    file, ext = os.path.splitext(os.path.basename(path))
    if not ext and file.startswith('.'):
        return '', file
    return file, ext


def path_ext(path):
    return split_ext(path)[-1]


def multi_ext(path, limit=None, case=False):
    filename = os.path.basename(path)
    result = []
    while True:
        index = filename.rfind('.')
        if index != -1:
            ext = filename[index:]
            if case is None:
                pass
            elif case:
                ext = ext.upper()
            else:
                ext = ext.lower()
            result.insert(0, ext)
            filename = filename[:index]
            if limit is not None and len(result) >= limit:
                break
        else:
            break
    return filename, result


def path_parent(path, deep=None):
    deep = 1 if deep is None else deep
    cursor = normal_path(path)
    for i in range(deep):
        cursor = os.path.dirname(cursor)
    return cursor


def path_by(path, relative):
    path = normal_path(path)
    if os.path.isfile(path):
        path = os.path.dirname(path)
    return normal_path(os.path.join(path, relative))


def list_env_paths():
    path = os.environ.get("PATH", None)
    if path is None:
        try:
            path = os.confstr("CS_PATH")
        except (AttributeError, ValueError):
            # os.confstr() or CS_PATH is not available
            path = os.defpath
    path = os.fsdecode(path)
    return path.split(os.pathsep)


def iter_exe_paths(path=None):
    if sys.platform == "win32":
        if not path:
            path = os.getcwd()
        yield path
    yield from list_env_paths()


def where(file, paths, exe=True):
    def _access_check(fn, m):
        return (os.path.exists(fn) and os.access(fn, m)
                and not os.path.isdir(fn))

    if exe and sys.platform == "win32":
        _WIN_DEFAULT_PATHEXT = ".COM;.EXE;.BAT;.CMD;.VBS;.JS;.WS;.MSC"
        pathext_source = os.getenv("PATHEXT") or _WIN_DEFAULT_PATHEXT
        pathext = [ext for ext in pathext_source.split(os.pathsep) if ext]
        if any(file.lower().endswith(ext.lower()) for ext in pathext):
            files = [file]
        else:
            files = [file + ext for ext in pathext]
    else:
        files = [file]

    seen = set()
    for d in paths:
        np = os.path.normcase(d)
        if np not in seen:
            seen.add(np)
            for f in files:
                name = os.path.join(d, f)
                mode = os.F_OK
                if exe:
                    mode |= os.X_OK
                if _access_check(name, mode):
                    return name


def which(file, *paths, exe=True):
    if not paths:
        paths = iter_exe_paths()
    return where(file, paths, exe)


def those(file, exe=True):
    result = []
    seen = set()
    for path in iter_exe_paths():
        p = where(file, [path], exe=exe)
        if p:
            np = os.path.normcase(p)
            if np not in seen:
                seen.add(np)
                result.append(p)
    return result


def tree(root=None, depth=None, size=False, top=True):
    # prefix components:
    symbol_space = '    '
    symbol_branch = '│   '
    # pointers:
    symbol_tee = '├── '
    symbol_last = '└── '
    # type
    symbol_folder = '📁 '
    # info
    symbol_size = ' 📦 '

    def _tree(dir_path: Path, prefix, dir_depth):
        if depth is not None and dir_depth > depth:
            return
        contents = sorted(dir_path.iterdir(), key=lambda item: 1 if os.path.isfile(dir_path / item) else 0)
        # contents each get pointers that are ├── with a final └── :
        pointers = [symbol_tee] * (len(contents) - 1) + [symbol_last]
        for pointer, path in zip(pointers, contents):
            is_dir = path.is_dir()
            typed = symbol_folder if is_dir and depth is not None and dir_depth == depth else ''
            item = prefix + pointer + typed + path.name
            if size and not is_dir:
                item += symbol_size + format_file_size(os.path.getsize(path))
            yield item
            if is_dir:  # extend the prefix and recurse:
                extension = symbol_branch if pointer == symbol_tee else symbol_space
                # i.e. space because last, └── , above so no more |
                yield from _tree(path, prefix + extension, dir_depth + 1)

    root = root or os.getcwd()
    if top:
        print(normal_path(root), flush=True)
    for line in _tree(Path(root), '', 0):
        print(line, flush=True)


def iglob(pattern, root=None, file=None, relpath=False):
    if root is None:
        root = os.getcwd()
    else:
        root = normal_path(root)
    if isinstance(pattern, str):
        cache = None
        pattern = [pattern]
    else:
        if len(pattern) > 1:
            cache = set()
        else:
            cache = None
    path = Path(root)
    for p in pattern:
        for full in path.glob(p):
            pa = str(full)
            item = pa[len(root) + len(os.path.sep):]
            if relpath is None:
                pp = item, pa
            else:
                pp = item if relpath else pa
            if cache is not None:
                if pa in cache:
                    continue
                cache.add(pa)
            if file is None:
                yield pp
            elif file:
                if os.path.isfile(pa):
                    yield pp
            else:
                if os.path.isdir(pa):
                    yield pp


# This func will ignore those folder which startswith dot
def iglob2(pattern, root=None, file=None, relpath=False):
    if root is None:
        root = os.getcwd()
    else:
        root = normal_path(root)
    if isinstance(pattern, str):
        cache = None
        pattern = [pattern]
    else:
        if len(pattern) > 1:
            cache = set()
        else:
            cache = None
    if not glob_support_root:
        kwargs = dict(recursive=True)
        last_dir = os.getcwd()
        os.chdir(root)
    else:
        kwargs = dict(root_dir=root, recursive=True)
    for p in pattern:
        for item in glob.iglob(p, **kwargs):
            pa = os.path.join(root, item)
            if relpath is None:
                pp = item, pa
            else:
                pp = item if relpath else pa
            if cache is not None:
                if pa in cache:
                    continue
                cache.add(pa)
            if file is None:
                yield pp
            elif file:
                if os.path.isfile(pa):
                    yield pp
            else:
                if os.path.isdir(pa):
                    yield pp
    if not glob_support_root:
        os.chdir(last_dir)


def seek_py_module_path(path):
    path = normal_path(path)
    if os.path.isfile(path):
        path = os.path.dirname(path)
    cursor = path
    step = 0
    last = None
    while True:
        if any(os.path.exists(os.path.join(cursor, f'__init__{ext}')) for ext in ('.py', '.pyc')):
            if step == 0:
                step = 1
        else:
            if step == 1:
                return last
        last = cursor
        cursor = os.path.dirname(cursor)
        if last == cursor:
            break
    return None
