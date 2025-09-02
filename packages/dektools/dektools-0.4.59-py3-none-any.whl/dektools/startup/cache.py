import os
from pathlib import Path
from ..common import cached_property
from ..file import write_file, sure_dir, remove_path
from .base import Startup


class StartupCache(Startup):
    done_name = ''

    @cached_property
    def path_index(self):
        path = Path.home()
        subs = self.__class__.__module__.split('.')
        path /= '.' + subs[0]
        for sub in subs[1:]:
            path /= sub
        return path / self.__class__.__name__

    @cached_property
    def path_done(self):
        return self.path_index / (self.done_name + '.done')

    def _handler(self):
        sure_dir(self.path_done.parent)
        self._cache_handler()
        write_file(self.path_done, s='')

    def _is_done(self):
        return os.path.exists(self.path_done)

    def clear(self):
        remove_path(self.path_done)

    def _cache_handler(self):
        raise NotImplementedError
