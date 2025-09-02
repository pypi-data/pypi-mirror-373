import os
import sys
import json
import time
import shutil
import ctypes
import subprocess
from .file import write_file, remove_path
from .dict import list_dedup, is_list
from .str import shlex_split, shlex_quote, shlex_join
from .func import FuncAnyArgs
from .common import cached_property


class FileNotFoundProcessError(subprocess.SubprocessError):
    pass


def command_split(s):
    args = shlex_split(s)
    path_bin = args[0]
    name_bin = os.path.basename(path_bin)
    if not os.path.exists(path_bin):
        if name_bin != path_bin:
            raise FileNotFoundProcessError(path_bin)
        else:
            path = shutil.which(name_bin)
            if path:
                path_bin = path
            else:
                raise FileNotFoundProcessError(path_bin)
        args[0] = path_bin
    return args


def shell_wrapper(command, check=True, chdir=None, shell=False, env=None):
    dir_last = None
    if chdir:
        dir_last = os.getcwd()
        os.chdir(chdir)
    rc = subprocess.call(
        command if shell else command_split(command), shell=shell, env=env)  # equals to bash -c '<command>'
    if check and rc:
        if dir_last:
            os.chdir(dir_last)
        raise subprocess.CalledProcessError(rc, command)
    if dir_last:
        os.chdir(dir_last)
    return rc


def shell_retry(command, times=None, check=True, notify=True, interval=0.1, env=None):
    count = 0
    while True:
        if isinstance(command, str):
            err = subprocess.call(command_split(command), env=env)
        elif is_list(command):
            err = 0
            for c in command:
                err = subprocess.call(command_split(c), env=env)
                if err:
                    break
        else:
            try:
                err = FuncAnyArgs(command)(env=env) or 0
            except subprocess.SubprocessError:
                err = 1
        if err:
            count += 1
            if times is not None and count >= times:
                if check:
                    raise subprocess.CalledProcessError(err, command)
                else:
                    return err
            if notify:
                total = '' if times is None else f'/{times}'
                print(f"shell_retry<{count}{total}>: {command}", flush=True)
            time.sleep(interval)
        else:
            break
    return err


def shell_output(command, error=True, env=None, encode=None, check=False):
    rc, output = shell_result(command, error, env, encode)
    if check and rc:
        raise subprocess.CalledProcessError(rc, command, output)
    return output


def shell_exitcode(command, error=True, env=None, encode=None):
    return shell_result(command, error, env, encode)[0]


def shell_result(command, error=True, env=None, encode=None):
    return getstatusoutput(command, error, env, encode)


def getstatusoutput(command, error=True, env=None, encode=None):
    try:
        data = subprocess.check_output(
            command_split(command), env=env,
            stderr=subprocess.STDOUT if error else subprocess.DEVNULL)
        exitcode = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    data = data.decode(encode or 'utf-8')
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data


def shell_with_input_once(command, inputs, env=None):
    p = subprocess.Popen(
        command_split(command), env=env, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if isinstance(inputs, str):
        inputs = inputs.encode('utf-8')
    outs, errs = p.communicate(input=inputs)
    return p.returncode, outs, errs


def shell_with_input(command, handler, env=None):
    p = subprocess.Popen(
        command_split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
        bufsize=0, env=env)
    if not callable(handler):
        handler = ShellInputHandler(handler)
    handler(p, None)
    buffer = ''
    while p.poll() is None:
        char = p.stdout.read(1).decode(sys.stdout.encoding)
        if char in '\r\n':
            print(buffer, end=char, flush=True)
            buffer = ''
        else:
            buffer += char
            handler(p, buffer)
    if buffer:
        print(buffer, end='', flush=True)
    return p.returncode


class ShellInputHandler:
    def __init__(self, data, reduce=True, order=True):
        self.data = data
        self.reduce = reduce
        self.order = order

    def __call__(self, p, text):
        if isinstance(self.data, str):
            if text is None:
                self.input(p, self.data)
                return True
        else:
            if text is not None:
                return self.run(p, text)
        return False

    def run(self, p, text):
        key = None
        for k, v in self.data.items():
            if isinstance(k, str):
                match = text.endswith(k)
            else:
                match = k.match(text)
            if match:
                key = k
                self.input(p, v)
                break
            if self.order:
                break
        if key is not None:
            if self.reduce:
                self.data.pop(key)
            return True
        return False

    @staticmethod
    def input(p, s):
        p.stdin.write(s.encode(sys.stdout.encoding))
        p.stdin.write(b'\n')


def shell_stdout(command, write=None, env=None):
    proc = subprocess.Popen(command_split(command),
                            env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True
                            )
    write = write or sys.stdout.write
    while proc.poll() is None:
        stdout = proc.stdout.readline()
        write(stdout)


def shell_tee(command, env=None):
    def write(s):
        nonlocal result
        result += s
        sys.stdout.write(s)

    result = ''
    shell_stdout(command, write=write, env=env)
    return result


def shell_command(command, sync=True, headless=False, quiet=False, check=True, env=None, embed=False):
    result = None
    try:
        if os.name == 'nt' and headless:
            result = shell_command_nt_headless(command, sync, check, env=env)
        else:
            if not sync:
                if embed:
                    subprocess.Popen(command_split(command), env=env)
                else:
                    subprocess.run(_cmd_to_not_sync(command), check=True, shell=True, env=env)
            elif quiet:
                rc, output = shell_output(command, env=env)
                if rc:
                    result = subprocess.CalledProcessError(rc, command, output)
            else:
                subprocess.run(command_split(command), check=True, env=env)
    except subprocess.SubprocessError as e:
        result = e
    return result if check else None


def _cmd_to_not_sync(command):
    command = shlex_join(command_split(command))
    if os.name == 'nt':
        title = command.replace('"', '')
        command = f'start "{title}" ' + command
    else:
        command = 'nohup ' + command + ' &'
    return command


def run_vbs(s, sync=True, check=True, env=None):
    fp = write_file('run.vbs', s=s, t=True)
    try:
        args = command_split(f'wscript {shlex_quote(fp)}')
        if sync:
            subprocess.run(args, check=check, env=env)
        else:
            subprocess.Popen(args)
    except subprocess.SubprocessError as e:
        if check:
            raise
        else:
            return e
    finally:
        if sync:
            remove_path(fp)
        else:
            subprocess.Popen([sys.executable, '-c', f'''import time;import os;time.sleep(1);os.remove(r"{fp}")'''])


def escape_vbs(s):
    return s.replace('"', '""')


def shell_command_nt_headless(command, sync=True, check=True, env=None):
    if not env:
        env = os.environ.copy()
    marker = __name__.partition(".")[0].upper() + '_VBS_ENV'
    if env.get(marker) == 'true':  # As vbs call deep bug
        if sync:
            return shell_command(command, sync, headless=False, check=check, env=env)
    env[marker] = "true"

    vbs = f"""
Dim Wsh
Set Wsh = WScript.CreateObject("WScript.Shell")
Wsh.Run "{escape_vbs(command)}",0,{'true' if sync else 'false'}
Set Wsh=NoThing
WScript.quit
    """
    return run_vbs(vbs, sync, check, env)


def shell_command_nt_as_admin(command, sync=True, check=True, env=None):
    if not env:
        env = os.environ.copy()
    cs = command_split(command)
    exe = cs[0]
    params = shlex_join(cs[1:])
    vbs = f"""
Dim Wsh
Set Wsh = WScript.CreateObject("Shell.Application")
Wsh.ShellExecute "{exe}", "{escape_vbs(params)}", , "runas", 1
Set Wsh=NoThing
WScript.quit
    """
    return run_vbs(vbs, sync, check, env)


def shell_timeout(command, timeout, env=None, check=True):
    if os.name == 'nt':
        rc = _shell_timeout_windows(command, timeout, env)
    else:
        rc = _shell_timeout_unix(command, timeout, env)
    if check and rc:
        raise subprocess.CalledProcessError(rc, command)
    return rc


def _shell_timeout_windows(command, timeout, env=None):
    # https://github.com/ungoogled-software/ungoogled-chromium-windows/blob/134.0.6998.88-1.1/build.py#L74
    with subprocess.Popen(
            ('cmd.exe', '/k'), encoding='utf-8', stdin=subprocess.PIPE, env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP) as proc:
        proc.stdin.write(f'{command}\nexit\n')
        proc.stdin.close()
        try:
            proc.wait(timeout)
            return proc.returncode
        except subprocess.TimeoutExpired:
            import time
            import ctypes
            for _ in range(3):
                ctypes.windll.kernel32.GenerateConsoleCtrlEvent(1, proc.pid)
                time.sleep(1)
            try:
                proc.wait(10)
            except:
                proc.kill()
            print(flush=True)
            return None


def _shell_timeout_unix(command, timeout, env=None):
    # https://stackoverflow.com/a/72135833/15543185
    with subprocess.Popen(command_split(command), env=env, preexec_fn=os.setsid) as process:
        try:
            process.communicate(None, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            import signal
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            try:
                import msvcrt
            except ModuleNotFoundError:
                _mswindows = False
            else:
                _mswindows = True
            if _mswindows:
                # Windows accumulates the output in a single blocking
                # read() call run on child threads, with the timeout
                # being done in a join() on those threads.  communicate()
                # _after_ kill() is required to collect that and add it
                # to the exception.
                exc.stdout, exc.stderr = process.communicate()
            else:
                # POSIX _communicate already populated the output so
                # far into the TimeoutExpired exception.
                process.wait()
            process.communicate()
            return None
        except:  # Including KeyboardInterrupt, communicate handled that.
            process.kill()
            # We don't call process.wait() as .__exit__ does that for us.
            process.communicate()
        return process.returncode


def show_win_msg(msg=None, title=None):
    if os.name == 'nt':
        import ctypes
        mb = ctypes.windll.user32.MessageBoxW
        mb(None, msg or 'Message', title or 'Title', 0)


class Cli:
    def __init__(self, list_or_dict, path=None):
        if is_list(list_or_dict):
            self.recon = {k: None for k in list_or_dict}
        else:
            self.recon = list_or_dict
        self.path = path

    @cached_property
    def cur(self):
        if self.path:
            bin_list = [k for k, v in self.recon.items() if not v or os.path.exists(os.path.join(self.path, v))]
        else:
            bin_list = []
        bin_list = list_dedup([*bin_list, *self.recon])
        for cli in bin_list:
            if shutil.which(cli):
                return cli


def output_data(data, out=None, fmt=None):
    def get_fmt_args():
        ff = fmt.split('=', 1)
        if len(ff) == 1:
            return ff, None
        return ff

    data = data or {}
    fmt = fmt or 'env'
    if fmt == 'env':
        s = "\n".join(f'{k}="{v}"' for k, v in data.items())
    elif fmt == 'json':
        s = json.dumps(data)
    elif fmt == 'yaml':
        from .serializer.yaml import yaml
        s = yaml.dumps(data)
    elif fmt.startswith('dyna.json'):
        from .serializer.dyna import dyna
        fmt, prefix = get_fmt_args()
        s = dyna.dumps(data, prefix=prefix, json=True)
    elif fmt.startswith('dyna'):
        from .serializer.dyna import dyna
        fmt, prefix = get_fmt_args()
        s = dyna.dumps(data, prefix=prefix)
    else:
        raise TypeError(f'Please provide a correct format: {fmt}')
    if out:
        write_file(out, s=s)
    else:
        print(write_file(f'.{fmt}', s=s, t=True), end='', flush=True)


def get_current_sys_exe():
    return shutil.which(os.path.basename(sys.argv[0]))


def associate(ext, filetype, command):
    shell_wrapper(f"assoc {ext}={filetype}")
    shell_wrapper(f"ftype {filetype}={command}")


def associate_remove(ext, filetype):
    shell_wrapper(f"ftype {filetype}=")
    shell_wrapper(f"assoc {ext}=")


def associate_console_script(ext, _name_, sub, content, is_code=False):
    name = _name_.partition('.')[0]
    if is_code:
        path_pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        command = fr'''"{path_pythonw}" -c "{content}"'''
    else:
        command = fr'''"{get_current_sys_exe()}" {content} "%1" %*'''
    associate(ext, f"Python.ConsoleScript.{name}.{sub}", command)


def associate_console_script_remove(ext, _name_, sub):
    name = _name_.partition('.')[0]
    associate_remove(ext, f"Python.ConsoleScript.{name}.{sub}")


def is_user_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
