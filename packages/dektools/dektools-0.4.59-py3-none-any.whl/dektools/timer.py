import time
import threading
from .func import FuncAnyArgs


class Timer:
    def __init__(self, func, interval, count=1):
        self.interval = interval  # seconds
        self.count = 0
        self.limit_count = count  # None for inf
        self.func_set = [func] if func else []
        self.valid = True
        self.stop_event = threading.Event()
        threading.Thread(target=self.__callback).start()

    def _get_interval(self):
        if callable(self.interval):
            return self.interval(self)
        else:
            return self.interval

    def __callback(self):
        now = time.perf_counter()
        next_time = now + self._get_interval()
        while not self.stop_event.wait(next_time - now):
            for func in self.func_set:
                func(self)
            self.count += 1
            if self.limit_count is not None and self.limit_count <= self.count:
                self.end()
            else:
                next_time += self._get_interval()
        self.valid = False

    def add_func(self, func):
        self.func_set.append(func)

    def remove_func(self, func):
        self.func_set.remove(func)
        if not self.func_set:
            self.end()

    def end(self):
        self.stop_event.set()


class TimerInLoop:
    def __init__(self):
        self._id_cursor = 0
        self._records = {}

    def __len__(self):
        return len(self._records)

    def _new_id(self):
        self._id_cursor += 1
        return self._id_cursor

    def set_interval(self, func, interval, count=1):  # seconds
        self._records[self._new_id()] = [func, interval, time.time(), count, 0]

    def clear_interval(self, uid):
        return bool(self._records.pop(uid, None))

    def has_interval(self, uid):
        return uid in self._records

    def find_interval(self, func):
        for uid, record in self._records.items():
            if record[0] is func:
                yield uid

    def peek(self):
        remove = set()
        times = 10 ** 7
        tn = time.time()
        for uid in self._records.keys():
            func, interval, ts, count, index = record = self._records[uid]
            if interval == 0:
                idx = index + 1
            else:
                idx = int((tn - ts) * times) // int(interval * times)
            if idx > index:
                FuncAnyArgs(func)()
                if count is not None:
                    count -= 1
                    if count <= 0:
                        remove.add(uid)
                        continue
                    else:
                        record[-2] = count
                record[-1] = idx
        for uid in remove:
            self._records.pop(uid, None)
