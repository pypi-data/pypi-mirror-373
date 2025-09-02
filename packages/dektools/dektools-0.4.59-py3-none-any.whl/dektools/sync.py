# https://github.com/xloem/async_to_sync
import os
import asyncio
import atexit
import threading
import random
from types import FunctionType


class Env:
    def __init__(self, event_loop_policy=None):
        self._event_loop_policy = event_loop_policy or asyncio.get_event_loop_policy()
        self._loop = None
        self._thread = None
        atexit.register(self.stop)

    @property
    def is_exist(self):
        return bool(self._loop and self._thread)

    def get_event_loop(self):
        if self._thread is None:
            if self._loop is None:
                self._loop = self._event_loop_policy.new_event_loop()
            if not self._loop.is_running():
                self._thread = threading.Thread(
                    target=self._loop.run_forever,
                    daemon=True)
                self._thread.start()
        return self._loop

    def start(self):
        self.get_event_loop()

    def stop(self):
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def set_event_loop(self, loop):
        self.stop()
        self._loop = loop

    def coroutine(self, coroutine, wait=True):
        future = asyncio.run_coroutine_threadsafe(coroutine, self.get_event_loop())
        if wait:
            return future.result()
        else:
            return future


default_env = Env()


class EnvSet:
    env_cls = Env
    event_loop_policy_cls = asyncio.DefaultEventLoopPolicy

    def __init__(self, num=None):
        if num is None:
            num = os.cpu_count()
        self.env_set = [self.env_cls(self.event_loop_policy_cls()) for _ in range(num)]

    def __len__(self):
        return len(self.env_set)

    def start(self):
        for env in self.env_set:
            env.start()

    def coroutine(self, coroutine, uid=None, wait=True):
        if uid is None:
            index = random.randrange(0, len(self))
        else:
            index = uid % len(self)
        return self.env_set[index].coroutine(coroutine, wait)


def as_async(func_or_env=None):
    from asgiref.sync import sync_to_async

    def wrapper(func, env, *args, **kwargs):
        @sync_to_async
        def inner(*args_, **kwargs_):
            return func(*args_, **kwargs_)

        return env.coroutine(inner(*args, **kwargs))

    if isinstance(func_or_env, FunctionType):
        return lambda *args, **kwargs: wrapper(func_or_env, default_env, *args, **kwargs)
    else:
        return lambda func: lambda *args, **kwargs: wrapper(func, func_or_env or default_env, *args, **kwargs)


def new_as_async(env_set_cls=EnvSet, num=None):
    env_set = env_set_cls(num)
    env_set.start()
    return as_async(env_set), env_set
