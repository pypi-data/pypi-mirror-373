import os
import sys
import time
import shlex
import psutil
import getpass
from tabulate import tabulate
from ...format import format_duration_hms
from ...output import obj2str
from ...attr import Object

process_attrs = psutil._as_dict_attrnames  # noqa


def process_print_all():
    table = []
    headers = ['PID', 'USER', 'TIME', 'COMMAND']
    for proc in psutil.process_iter(['pid', 'name', 'username', 'create_time', 'cmdline']):
        x = proc.info
        command = shlex.join(x['cmdline']) if x['cmdline'] else f"<{x['name']}>"
        ts = format_duration_hms(int(time.time() - x['create_time']) * 1000) if x['create_time'] else ''
        table.append(
            [x['pid'], x['username'], ts, command])
    print(tabulate(table, headers=headers), flush=True)


def process_print_detail(p=None):
    if not isinstance(p, psutil.Process):
        p = psutil.Process(p)
    print(obj2str(p.as_dict()), flush=True)


def process_detail(pid):
    return psutil.Process(pid)


def process_query(func):
    for proc in psutil.process_iter(process_attrs):
        if func(Object(**proc.info)):
            yield proc


def process_username(username=None):
    if not username:
        username = getpass.getuser()
    if sys.platform == "win32":
        ud = os.getenv('USERDOMAIN')
        if ud:
            return ud + os.sep + username
    return username
