import os
import json
import shutil
import subprocess
from sysconfig import get_paths
from importlib import metadata, import_module


def path_sys_exe():  # Used by system python Scripts bin
    versions = []
    for path in (shutil.which('python'), shutil.which('python3')):
        if path:
            version = subprocess.getoutput(f'{path} -c "import sys;print(sys.version_info.major)"')
            versions.append((version, path))
    _, exe = max(versions, key=lambda x: x[0])
    return subprocess.getoutput(f'{exe} -c "import sys;print(sys.executable)"')


def paths_sys():
    exe = path_sys_exe()
    sd = subprocess.getoutput(f'{exe} -c "import json;from sysconfig import get_paths;print(json.dumps(get_paths()))"')
    return json.loads(sd)


def sys_paths_relative(path, raw=False):  # sys_paths_relative('./.venv')
    if not raw:
        path = os.path.normpath(os.path.abspath(path))
    path = path.rstrip('/\\')
    result = {}
    paths = get_paths()
    prefix = paths['data'] + os.sep
    for k, p in paths.items():
        if p.startswith(prefix):
            result[k] = path + os.sep + p[len(prefix):]
        else:
            result[k] = p
    result['data'] = paths['data']
    return result


def get_console_scripts_exe(name, cmd=None):
    eps = metadata.entry_points(group='console_scripts')
    try:
        ep = eps[name]
    except KeyError:
        return None
    try:
        filepath = import_module(ep.module.split('.')[0]).__file__
        path_pkg = os.path.dirname(filepath)
        if os.path.splitext(os.path.basename(filepath))[0] == '__init__':
            path_pkg = os.path.dirname(path_pkg)
    except (ImportError, ModuleNotFoundError):
        return None
    cmd = cmd or name
    for file in ep.dist.files:
        fp = os.path.abspath(os.path.join(path_pkg, os.path.sep.join(file.parts)))
        if os.path.isfile(fp) and os.path.splitext(os.path.basename(fp))[0].lower() == cmd.lower():
            return fp
    return None
