import threading


class Startup:
    def __init__(self):
        if self._is_done():
            self._lock = None
        else:
            self._lock = threading.Lock()
            self.start()

    def __enter__(self):
        if self._lock:
            self._lock.acquire()
        return self

    def __exit__(self, t, v, tb):
        if self._lock:
            self._lock.release()

    def start(self):
        threading.Thread(target=self.__target).start()

    def __target(self):
        with self._lock:
            self._handler()
        self._lock = None

    def _handler(self):
        raise NotImplementedError

    def _is_done(self):
        raise NotImplementedError
