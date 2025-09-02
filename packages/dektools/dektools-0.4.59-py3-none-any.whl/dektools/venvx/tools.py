import os
from .constants import venv_list, venv_config_file
from ..sys import sys_paths_relative
from ..file import which, normal_path


def is_venv_path(path):
    return os.path.isfile(os.path.join(path, venv_config_file))


def find_venv_path(path=None):
    if not path:
        path = os.getcwd()
    else:
        path = normal_path(path)
    for item in venv_list:
        result = os.path.join(path, item)
        if is_venv_path(result):
            return result


def find_venv_bin(name, path=None):
    path_venv = find_venv_path(path)
    if path_venv:
        path_scripts = sys_paths_relative(path_venv)['scripts']
        path_exe = which(name, path_scripts)
        if path_exe:
            return path_exe
