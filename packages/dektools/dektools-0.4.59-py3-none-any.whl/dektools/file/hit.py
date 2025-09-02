import os
import shutil
import tempfile
from .path import normal_path, new_empty_path
from .operation import read_lines, merge_move, remove_path, write_file, list_dir, remove_empty_dir
from ..match import Matcher


class FileHitChecker(Matcher):
    append_records = {
        '.gitignore': ['.git']
    }

    def __init__(self, path, *ignore_file_list, lines=None):
        path = normal_path(path)
        all_lines = []
        for ignore_file in ignore_file_list:
            full_path = os.path.join(path, ignore_file)
            records = self.append_records.get(ignore_file)
            if records:
                all_lines.extend((full_path, -i - 1, line) for i, line in enumerate(records))
            all_lines.extend(read_lines(full_path, default='', skip_empty=False, strip=False, trace=True))
        if lines:
            all_lines.extend(lines)
        super().__init__(all_lines, {'base_path': path})

    @property
    def base_path(self):
        return self.kwargs.get('base_path')

    @staticmethod
    def shutil_ignore(base_dir, file_names, match, reverse=False):
        """
        Ignore function for shutil.copy_tree
        """
        ignore_files = set()
        for file in file_names:
            path = os.path.join(base_dir, file)
            if os.path.isdir(path):
                continue
            hit = match(path)
            if reverse:
                hit = not hit
            if hit:
                ignore_files.add(file)
        return ignore_files

    @staticmethod
    def walk_remove(fp, hit, __):
        if hit:
            remove_path(fp)

    @staticmethod
    def walk_remove_reversed(fp, hit, __):
        if not hit:
            remove_path(fp)

    def walk(self, func, lines=None):
        def wrapper(path):
            for fn in os.listdir(path):
                fp = os.path.join(path, fn)
                func(fp, match(fp), fp[len(path_root) + 1:])
                if os.path.isdir(fp):
                    wrapper(fp)

        path_root = self.base_path
        match = self.new_match(lines)
        if os.path.exists(path_root):
            wrapper(path_root)

    def merge_dir(self, dest, lines=None, reverse=False):
        dp = new_empty_path(dest)
        self.write_dir(dp, lines, reverse)
        merge_move(dest, dp)
        remove_path(dp)

    def write_dir(self, dest=None, lines=None, reverse=False):
        if dest is None:
            dest = tempfile.mkdtemp()
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        match = self.new_match(lines)
        shutil.copytree(self.base_path, dest, ignore=lambda x, y: self.shutil_ignore(x, y, match, reverse))
        remove_empty_dir(dest)
        return dest


def copy_recurse_ignore(src, dest=None, ignores=None, fhc=FileHitChecker):
    def walk(root):
        for ignore in ignores:
            if os.path.isfile(os.path.join(root, ignore)):
                fhc(root, ignore).write_dir(dest + root[len(src):])
                break
        else:
            for pa in list_dir(root):
                if os.path.isdir(pa):
                    walk(pa)
                else:
                    write_file(dest + pa[len(src):], c=pa)

    if not dest:
        dest = tempfile.mkdtemp()
    walk(src)
    return dest
