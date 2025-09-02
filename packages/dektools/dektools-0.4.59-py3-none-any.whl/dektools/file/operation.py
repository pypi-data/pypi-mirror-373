import os
import tempfile
import stat
import shutil
import codecs
import filecmp
import uuid
from io import BytesIO, TextIOBase
from ..crypto.rc4 import rc4
from ..common import ns2datetime
from ..format import format_file_size
from ..str import Fragment, comment_code
from .path import normal_path, new_empty_path, iglob

DEFAULT_VALUE = type('default_value', (), {})


def write_file(
        filepath=None,
        s=None, b=None, sb=None, a=None,
        m=None, mi=None,
        c=None, ci=None,
        ma=None, mo=None, mie=None, mm=None, mf=None,
        t=False, g=None,
        encoding='utf-8'):
    def _hit(*xx):
        return any(x is not None for x in xx)

    is_link = os.path.islink(filepath) if filepath else False
    if not is_link and filepath and not t and a is None and \
            mi is None and ci is None and ma is None and mo is None and mie is None:
        if os.path.exists(filepath):
            remove_path(filepath)
        else:
            sure_parent_dir(normal_path(filepath))
    if filepath is None or t:
        args = []
        kwargs = {}
        if t:
            if isinstance(t, str):
                kwargs = dict(prefix=None)
            elif isinstance(t, dict):
                kwargs = t
            elif isinstance(t, (list, tuple)):
                args = t
        pt = tempfile.mkdtemp(*args, **kwargs)
        if _hit(s, b, sb, mf):
            fp = os.path.join(pt, filepath) if filepath else new_empty_path(pt, 'temp')
            write_file(fp, s=s, b=b, sb=sb, mf=mf, g=g)
        elif _hit(m, mi, c, ci, ma, mo, mie):
            fp = os.path.join(pt, filepath or os.path.basename(m or mi or c or ci or ma or mo or mie))
            write_file(fp, m=m, mi=mi, c=c, ci=ci, ma=ma, mo=mo, mie=mie, g=g)
        else:
            fp = pt
        return fp
    elif s is not None:
        if is_link:
            filepath = os.path.realpath(filepath)
        with codecs.open(filepath, 'a' if a else 'w', encoding=encoding) as f:
            if not a and is_link:
                f.truncate()
            return f.write(s)
    elif b is not None:
        if is_link:
            filepath = os.path.realpath(filepath)
        with open(filepath, 'r+b' if a else 'wb') as f:
            if a:
                f.seek(os.path.getsize(filepath))
            elif is_link:
                f.truncate()
            f.write(b)
    elif sb is not None:
        if isinstance(sb, str):
            write_file(filepath, s=sb, a=a)
        else:
            write_file(filepath, b=sb, a=a)
    elif c is not None:
        if os.path.isdir(c):
            if g is None:
                shutil.copytree(c, filepath)
            else:
                for rp in iglob(g, root=c, file=True, relpath=True):
                    src = os.path.join(c, rp)
                    dst = os.path.join(filepath, rp)
                    sure_parent_dir(dst)
                    shutil.copyfile(src, dst)
                    shutil.copystat(src, dst)
        else:
            shutil.copyfile(c, filepath)
            shutil.copystat(c, filepath)
    elif ci is not None:
        if os.path.exists(ci):
            write_file(filepath, c=ci, g=g)
    elif m is not None:
        if g is None:
            shutil.move(m, filepath)
        else:
            for rp in iglob(g, root=m, file=True, relpath=True):
                src = os.path.join(m, rp)
                dst = os.path.join(filepath, rp)
                sure_parent_dir(dst)
                shutil.move(src, dst)
    elif mi is not None:
        if os.path.exists(mi):
            write_file(filepath, m=mi, g=g)
    elif ma is not None:
        merge_assign(filepath, ma, g)
    elif mo is not None:
        merge_overwrite(filepath, mo, g)
    elif mie is not None:
        merge_ignore_exists(filepath, mie, g)
    elif mm is not None:
        merge_move(filepath, mm, g)
    elif mf is not None:
        if is_link:
            filepath = os.path.realpath(filepath)
        if isinstance(mf, str):
            files = iter_relative_path(mf, g, False)
        else:
            files = mf
        with open(filepath, 'wb') as f:
            for file in files:
                with open(file, 'rb') as ff:
                    shutil.copyfileobj(ff, f)
    else:
        raise ValueError("Can't match a valid operation")


def read_file(filepath, default=DEFAULT_VALUE):
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            return f.read()
    else:
        if default is not DEFAULT_VALUE:
            return default
        else:
            raise FileNotFoundError(filepath)


def write_file_(filepath, content):
    sure_dir(os.path.dirname(normal_path(filepath)))
    with open(filepath, 'wb') as f:
        f.write(content)


def read_chunked(filepath, chunked_size=64 * 2 ** 10, default=DEFAULT_VALUE):
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunked_size), b""):
                yield chunk
    else:
        if default is not DEFAULT_VALUE:
            yield default
        else:
            raise FileNotFoundError(filepath)


def read_text(filepath, default=DEFAULT_VALUE, encoding='utf-8'):  # default: str | type
    if filepath and os.path.isfile(filepath):
        with codecs.open(filepath, encoding=encoding) as f:
            return f.read()
    else:
        if default is not DEFAULT_VALUE:
            return default
        else:
            raise FileNotFoundError(filepath)


def iter_file_obj_lines(file):
    wrap = '\n' if isinstance(file, TextIOBase) else b'\n'
    for line in file:
        if line[-1:] == wrap:
            yield line[:-1]
        else:
            yield line


def iter_lines(filepath, default=DEFAULT_VALUE, encoding='utf-8'):  # default: str | type
    if filepath and os.path.isfile(filepath):
        with codecs.open(filepath, encoding=encoding) as f:
            yield from iter_file_obj_lines(f)
    else:
        if default is not DEFAULT_VALUE:
            yield from default.splitlines()
        else:
            raise FileNotFoundError(filepath)


def write_text(filepath, content, encoding='utf-8'):
    sure_dir(os.path.dirname(normal_path(filepath)))
    with codecs.open(filepath, 'w', encoding=encoding) as f:
        return f.write(content)


def read_lines(
        filepath, default=DEFAULT_VALUE, encoding='utf-8',
        skip_empty=False, strip=True, comment=None, trace=False):
    for i, line in enumerate(iter_lines(filepath, default=default, encoding=encoding)):
        if strip:
            line = line.strip()
        if skip_empty and not line:
            continue
        if comment is not None and line.startswith(comment):
            continue
        yield (filepath, i + 1, line) if trace else line


def remove_path(path, ignore=False):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, onerror=_remove_readonly)
        elif os.path.isfile(path):
            try:
                os.remove(path)
            except PermissionError:
                _remove_readonly(os.remove, path, None)
        return True
    except PermissionError as e:
        if not ignore:
            raise e from e
        return False


def _remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def come_real_path(path):
    def come_real_file(p):
        if os.path.islink(p):
            pp = os.path.realpath(p)
            os.remove(p)
            shutil.copyfile(pp, p)
            shutil.copystat(pp, p)

    if os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                come_real_file(os.path.join(root, filename))
    elif os.path.isfile(path):
        come_real_file(path)


def replace_file(entries, reverse=False):
    for path, replace in entries.items():
        content = read_text(path)
        content = Fragment.replace_safe_again(content, replace, reverse)
        if content is not None:
            write_file(path, sb=content)


def comment_file(entries, comment, reverse=False):
    for path, replace in entries.items():
        content = read_text(path)
        content = Fragment.replace_safe_again(
            content, [[code, comment_code(code, comment, again=True)][::-1 if reverse else 1] for code in replace])
        if content is not None:
            write_file(path, sb=content)


def clear_dir(path, ignore=False):
    for file in os.scandir(path):
        remove_path(os.path.join(path, file.name), ignore)


def merge_dir(dest, src):
    for fn in os.scandir(src):
        write_file(os.path.join(dest, fn.name), ci=os.path.join(src, fn.name))


def copy_path(src, dest):
    remove_path(dest)
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    elif os.path.isfile(src):
        shutil.copyfile(src, dest)
        shutil.copystat(src, dest)


def copy_file_stable(src, dest, cache=None):
    sure_parent_dir(dest, cache)
    shutil.copyfile(src, dest)
    shutil.copystat(src, dest)


def sure_parent_dir(path, cache=None):
    return sure_dir(os.path.dirname(path), cache)


def sure_dir(path, cache=None):
    if cache and path in cache:
        return path
    if not os.path.exists(path):
        os.makedirs(path)
        if cache is not None:
            cache.add(path)
    return path


def sure_read(path_or_content):
    if isinstance(path_or_content, (bytes, memoryview)):
        return BytesIO(path_or_content)
    else:
        return path_or_content


def content_cmp(a, b):
    return filecmp.cmp(a, b, False)


def list_relative_path(src, glob=None):
    result = {}
    for rp, fp in iter_relative_path(src, glob):
        result[rp] = fp
    return result


def iter_relative_path(src, glob=None, relpath=None):
    def result(fp):
        if relpath is None:
            return fp[len(str(src)) + 1:], fp
        elif relpath:
            return fp[len(str(src)) + 1:]
        else:
            return fp

    def walk(p):
        for fn in os.scandir(p):
            fp = os.path.join(p, fn.name)
            if os.path.isfile(fp):
                yield result(fp)
            elif os.path.isdir(fp):
                yield from walk(fp)

    src = normal_path(src)

    if os.path.isdir(src):
        if glob is None:
            yield from walk(src)
        else:
            yield from iglob(glob, root=src, file=True, relpath=relpath)


def iter_relative_path_complete(src):
    def walk(p):
        empty = True
        for fn in os.scandir(p):
            empty = False
            fp = os.path.join(p, fn.name)
            if os.path.isfile(fp):
                yield fp[len(str(src)) + 1:], fp, True
            elif os.path.isdir(fp):
                yield from walk(fp)
        if empty:
            yield p[len(str(src)) + 1:], p, False

    if os.path.isdir(src):
        yield from walk(src)


def iter_dir(path, full=False):
    if os.path.isdir(path):
        path = normal_path(path)
        for item in os.scandir(path):
            fullpath = os.path.join(path, item.name)
            if full:
                yield fullpath, item.name
            else:
                yield fullpath


list_dir = iter_dir


def iter_dir_type(path='.', file=None):
    if os.path.isdir(path):
        path = normal_path(path)
        for item in os.scandir(path):
            result = os.path.join(path, item.name)
            if file is None:
                yield result
            elif file:
                if os.path.isfile(result):
                    yield result
            else:
                if os.path.isdir(result):
                    yield result


def iter_dir_type_one(path='.', file=None, default=None):
    return next(iter_dir_type(path, file), default)


def new_temp_path(file):
    while True:
        target = f"{file}.{uuid.uuid4().hex}"
        if not os.path.exists(target):
            break
    return target


def iter_file_content(file, block_size=64 * 2 ** 10):
    def core(x):
        for chunk in iter(lambda: x.read(block_size), b""):
            yield chunk

    if hasattr(file, 'read'):
        yield from core(file)
    else:
        with open(file, 'rb') as f:
            yield from core(f)


def merge_assign(dest, src, glob=None):
    cache = set()
    if os.path.isfile(src):
        copy_file_stable(src, normal_path(dest), cache)
    else:
        for rp, fp in iter_relative_path(src, glob):
            copy_file_stable(fp, os.path.join(dest, rp), cache)


def merge_ignore_exists(dest, src, glob=None):
    cache = set()
    if os.path.isfile(src):
        if not os.path.exists(dest):
            copy_file_stable(src, normal_path(dest), cache)
    else:
        for rp, fp in iter_relative_path(src, glob):
            p = os.path.join(dest, rp)
            if not os.path.exists(p):
                copy_file_stable(fp, p, cache)


def merge_overwrite(dest, src, glob=None):
    # Equals to copy, Causing minimal impact, usually used to the served folder(dev mode)
    cache = set()
    if os.path.isfile(src):
        copy_file_stable(src, normal_path(dest), cache)
    else:
        src_info = list_relative_path(src, glob)
        for rp, fp in src_info.items():
            copy_file_stable(fp, os.path.join(dest, rp), cache)
        for rp, fp in iter_relative_path(dest, glob):
            if rp not in src_info:
                remove_path(fp)


def merge_move(dest, src, glob=None):
    cache = set()
    for rp, fp in iter_relative_path(src, glob):
        dp = os.path.join(dest, rp)
        remove_path(dp)
        sure_dir(os.path.dirname(dp), cache)
        os.rename(fp, dp)


def remove_empty_dir(path):
    empty_set = set()
    for root, dirs, filenames in os.walk(path, topdown=False):
        if not filenames and all(os.path.join(root, d) in empty_set for d in dirs):
            empty_set.add(root)
            os.rmdir(root)


def path_is_empty(path, strict=False):
    if strict:
        return not next(os.scandir(path), None)
    else:
        return not os.path.exists(path) or not next(os.scandir(path), None)


def desc_path(path):
    if os.path.isfile(path):
        st = os.stat(path)
        return st.st_size, st.st_ctime_ns, st.st_mtime_ns
    elif os.path.isdir(path):
        e, f, g = 0, 0, 0
        count = 0
        for base, _, files in os.walk(path):
            for file in files:
                p = os.path.join(base, file)
                st = os.stat(p)
                e += st.st_size
                f = max(st.st_ctime_ns, f)
                g = max(st.st_mtime_ns, g)
                count += 1
        return e, f, g, count


def format_path_desc(path, sep=None):
    def ts(t):
        return ns2datetime(t).strftime('%Y-%m-%d/%H:%M:%S')

    def fs(a, b, c, d=None):
        s = f"{format_file_size(a)}{sep}{ts(b)}{sep}{ts(c)}"
        if d is not None:
            s = f'{s}{sep}{d}'
        return s

    sep = ' - ' if sep is None else sep
    desc = desc_path(path)
    if desc:
        return fs(*desc)
    return ''


def __of_dir(src, target=None, remove=True):
    src = normal_path(src)
    if target is not None:
        if remove:
            remove_path(target)
    else:
        target = new_temp_path(src)
    return src, target


def status_of_dir(src, target=None):
    src, target = __of_dir(src, target)
    for base, _, files in os.walk(src):
        for file in files:
            p = os.path.join(base, file)
            pp = target + p[len(src):]
            os.makedirs(os.path.dirname(pp), exist_ok=True)
            try:
                t = str(os.path.getmtime(p))
            except FileNotFoundError:
                continue
            with open(pp, 'w') as f:
                f.write(t)
    return target


def diff_of_dir(src, status, target=None, skip=False):
    src, target = __of_dir(src, target, False)
    for base, _, files in os.walk(src):
        for file in files:
            p = os.path.join(base, file)
            try:
                t = str(os.path.getmtime(p))
            except FileNotFoundError:
                continue
            rp = p[len(src):]
            ps = status + rp
            if os.path.exists(ps):
                with open(ps, 'r') as f:
                    tt = f.read()
            else:
                tt = None
            if t != tt:
                pt = target + rp
                os.makedirs(os.path.dirname(pt), exist_ok=True)
                if not os.path.exists(pt) or not skip:
                    shutil.copyfile(p, pt)
                    shutil.copystat(p, pt)
    return target


def rc4_file(filepath, key, block_size=64 * 2 ** 10):
    if isinstance(key, str):
        key = key.encode('utf-8')
    target = new_temp_path(filepath)
    with open(target, 'wb') as f:
        for chunk in iter_file_content(filepath, block_size=block_size):
            f.write(rc4(chunk, key))
    shutil.copystat(filepath, target)
    os.remove(filepath)
    shutil.move(target, filepath)
