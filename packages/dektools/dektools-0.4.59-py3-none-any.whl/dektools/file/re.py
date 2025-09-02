import re
from .operation import read_lines


class ReHitChecker:
    @classmethod
    def form_file(cls, *filepaths):
        lines = []
        for filepath in filepaths:
            for x in read_lines(filepath, skip_empty=True):
                if not x.startswith('#'):
                    lines.append(x)
        return cls(lines)

    def __init__(self, lines):
        self.lines = lines

    def test(self, test):
        for item in self.lines:
            r = re.search(item, test)
            if r:
                return item
        return None

    def includes(self, array):
        for item in array:
            if self.test(item) is not None:
                yield item

    def excludes(self, array):
        for item in array:
            if self.test(item) is None:
                yield item
