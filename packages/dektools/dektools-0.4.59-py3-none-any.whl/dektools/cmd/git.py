import os
import sys
import configparser
from io import BytesIO
from itertools import chain
from collections import OrderedDict
from ..file import read_text, remove_path, iglob, normal_path, which, path_by
from ..shell import shell_wrapper, shell_result, shell_output


def git_parse_modules(s):
    cp = configparser.ConfigParser()
    if isinstance(s, str):
        cp.read_string(s)
    else:
        if isinstance(s, bytes):
            s = BytesIO(s)
        cp.read_file(s)
    result = OrderedDict()
    for section in cp.sections():
        submodule = section.split(' ', 1)[-1][1:-1]
        options = result[submodule] = OrderedDict()
        for k in cp.options(section):
            v = cp.get(section, k)
            options[k] = v
    return result


def git_clean_dir(path, dfx=True, git=True, root=True, verbose=1):
    modules = read_text(os.path.join(path, '.gitmodules'), default=None)
    if modules:
        subs = (os.path.join(path, v['path']) for v in git_parse_modules(modules).values())
    else:
        subs = range(0)
    for p in chain(iter([path] if root else []), iter(subs)):
        path_git = os.path.join(p, '.git')
        if os.path.exists(path_git):
            if dfx:
                shell_wrapper(f'git -C "{p}" clean -dfX')
            if git:
                remove_path(path_git)
            if verbose >= 2:
                print(f'Clean git: `{normal_path(p)}`', flush=True)
        else:
            if verbose >= 1:
                print(f'Clean git: `{normal_path(p)}` is skipped as it is not a git folder', flush=True)


def git_fetch_min(url, tag, path):
    shell_wrapper(f'git -C "{path}" clone --depth 1 --branch {tag} {url} .')
    shell_wrapper(f'git -C "{path}" submodule update --depth 1 --init --recursive')


def git_remove_tag(tag, path=None, remote=None):
    if not path:
        path = os.getcwd()
    shell_wrapper(f'git -C "{path}" tag -d {tag}')
    if remote is None:
        remote = git_list_remotes(path)
    elif isinstance(remote, str):
        remote = [remote]
    for r in remote:
        shell_wrapper(f'git -C "{path}" push {r} :refs/tags/{tag}')


def git_latest_tag(path=None):
    if not path:
        path = os.getcwd()
    rc, output = shell_result(f'git -C "{path}" describe --tags --abbrev=0')
    if rc:
        return None
    return output.strip()


def git_list_remotes(path=None):
    if not path:
        path = os.getcwd()
    command = f'git -C "{path}" remote show'
    output = shell_output(command, check=True)
    return [x for x in output.splitlines() if x]


def git_apply(src, dst=None, reverse=False, status=False, ignore=False):
    def work(file):
        if not status and patch:
            shell_wrapper(f'{patch} {ig_patch} -s -p1 {rp} -i "{file}" -d "{dst}"')
        else:
            shell_wrapper(f'git -C "{dst}" apply {rp} {ig_git} {stat} "{file}"')

    if not dst:
        dst = os.getcwd()

    rp = '-R' if reverse else ''
    ig_git = '--ignore-space-change --ignore-whitespace' if ignore else ''
    ig_patch = '--ignore-whitespace' if ignore else ''
    stat = '--stat' if status else ''

    patch = None
    if which('patch'):
        patch = 'patch'
    else:
        path_git = which('git')
        if path_git and sys.platform == "win32":
            path_patch = path_by(path_git, '../usr/bin/patch.exe')
            if os.path.isfile(path_patch):
                patch = f'"{path_patch}"'

    items = None
    if os.path.isfile(src):
        items = (src for _ in range(1))
    elif os.path.isdir(src):
        items = (x for x in iglob('**/*.patch', src, True))
        if reverse:
            items = reversed(list(items))
    if items is not None:
        for item in items:
            work(item)


def git_head(head=None, path=None):
    if not path:
        path = os.getcwd()
    if head is None:
        rc, output = shell_result(f'git -C "{path}" rev-parse HEAD')
        if rc:
            return None
        return output.strip()
    else:
        shell_wrapper(f'git -C "{path}" checkout {head}')
