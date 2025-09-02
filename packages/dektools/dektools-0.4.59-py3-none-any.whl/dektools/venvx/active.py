import os
import sys
from ..file import read_text
from ..sys import sys_paths_relative
from .tools import find_venv_path
from .constants import venv_this


def activate_venv(rootdir=None, ignore=True):
    path_venv = find_venv_path(rootdir)
    if not path_venv and ignore:
        return
    path_scripts = sys_paths_relative(path_venv)['scripts']
    this_file = os.path.join(path_scripts, venv_this)
    if not os.path.isfile(this_file) and ignore:
        return
    exec(read_text(this_file), {'__file__': this_file})


def is_venv_active(prefix=None):
    return (prefix or sys.prefix) != sys.base_prefix
