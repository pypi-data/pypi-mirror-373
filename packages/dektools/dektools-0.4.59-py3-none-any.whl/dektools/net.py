import time
import socket


def is_port_in_use(port, host=None):
    host = 'localhost' if host is None else host
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def get_available_port(port=None, host=None, step=1):
    port = 1023 if port is None else port
    host = 'localhost' if host is None else host
    while True:
        if not is_port_in_use(port, host):
            return port
        port += step


def get_ip_next(ip, step=1):
    pre, last = ip.rsplit(".", 1)
    number = int(last) + step
    if number > 255 or number < 0:
        raise ValueError(f'Invalid number of part: {ip} =>  {number}')
    return f'{pre}.{number}'


def get_mac_next(mac, index):
    step = 6
    v = int("".join(mac.split(':')), 16) + index
    s = "%0.2x" % v
    s = "0" * (step * 2 - len(s)) + s
    a = []
    for i in range(step):
        a.append(s[i * 2:i * 2 + 2])
    return ':'.join(a)


def get_local_ip_list():
    return socket.gethostbyname_ex(socket.gethostname())[-1]


def get_interface_ip(ipv6: bool = False) -> str:
    """Get the IP address of an external interface. Used when binding to
    0.0.0.0 or ::1 to show a more useful URL.

    :meta private:
    """
    # werkzeug/serving.py
    family: socket.AddressFamily = socket.AF_INET6 if ipv6 else socket.AF_INET
    # arbitrary private address
    host = "fd31:f903:5ab5:1::1" if family == socket.AF_INET6 else "10.253.155.219"

    with socket.socket(family, socket.SOCK_DGRAM) as s:
        try:
            s.connect((host, 58162))
        except OSError:
            return "::1" if family == socket.AF_INET6 else "127.0.0.1"

        return s.getsockname()[0]  # type: ignore


class Internet:
    times_max = 10

    def __init__(self, host="8.8.8.8", port=53, timeout=1):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._times = []
        self._time_last = None

    def _add_time(self, interval):
        self._times.append(interval)
        if len(self._times) > self.times_max:
            self._times.pop(0)

    def _cache_is_connected(self, begin):
        if self._times:
            if begin - self._time_last < sum(self._times) / len(self._times):
                return True
        return False

    @property
    def is_connected(self):
        begin = time.time()
        if self._cache_is_connected(begin):
            return True
        try:
            socket.setdefaulttimeout(self.timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            end = time.time()
            self._add_time(end - begin)
            self._time_last = end
            return True
        except socket.error:
            return False


internet = Internet()
