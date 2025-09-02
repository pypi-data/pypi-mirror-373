import time
import multiprocessing


class TaskQueue:
    def __init__(self, worker, max_count=None):
        self.queue = multiprocessing.Queue()
        self.event_pause = multiprocessing.Event()
        self.pool = multiprocessing.Pool(
            max_count or multiprocessing.cpu_count(),
            self.worker_main,
            (self.queue, self.event_pause, worker)
        )
        self.resume()

    def put(self, *items):
        for item in items:
            self.queue.put(item)

    def close(self):
        self.pool.close()

    def pause(self):
        self.event_pause.clear()

    def resume(self):
        self.event_pause.set()

    def is_pausing(self):
        return not self.event_pause.is_set()

    @property
    def rest_count(self):
        return self.queue.qsize()

    @property
    def is_empty(self):
        return self.queue.empty()

    @staticmethod
    def worker_main(queue, pause, worker):
        while pause.wait():
            if queue.empty():
                time.sleep(0)
            else:
                item = queue.get(True)
                worker(item)


def __task_test(x):
    print(x)


if __name__ == '__main__':
    tq = TaskQueue(__task_test, 3)
    tq.put(*['a', 'b', 'c'])

    time.sleep(2)
    print('stop')
    tq.close()
    time.sleep(2)
