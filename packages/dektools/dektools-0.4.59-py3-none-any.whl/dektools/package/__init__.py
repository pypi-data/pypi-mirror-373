import os.path
import sys
from ..shell import shell_result
from ..sys import sys_paths_relative


def get_package_version(name, venv=None):
    if venv:
        executable = os.path.join(sys_paths_relative(venv)['scripts'], os.path.basename(sys.executable))
    else:
        executable = sys.executable
    exitcode, data = shell_result(
        f"""{executable} -c "from importlib import metadata;print(metadata.metadata('{name}')['Version'])" """
    )
    return None if exitcode else data
