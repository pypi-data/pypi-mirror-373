import re
from itertools import chain
from collections import OrderedDict
from gitignore_parser import rule_from_pattern, handle_negation, fnmatch_pathname_to_regex


class Matcher:
    def __init__(self, lines=None, kwargs=None):
        self.lines = lines
        self.kwargs = {} if kwargs is None else kwargs

    @staticmethod
    def calc_negation(rules):
        return any(r.negation for r in rules)

    @staticmethod
    def check_match(full_path, rules, negation):
        if negation:
            return handle_negation(full_path, rules)
        else:
            return any(r.match(full_path) for r in rules)

    @staticmethod
    def trace_line(line):
        if isinstance(line, tuple):
            filepath, lineno, line = line
        else:
            filepath = None
            lineno = None
        return filepath, lineno, line

    def generate_rules(self, lines):
        append_prefix = '/**/'
        append_suffix = '/**/*'
        result = OrderedDict()
        for filepath, lineno, pattern in lines:
            negation = pattern.startswith('!')
            extra = None
            if negation:
                pattern = pattern[1:]
            if not pattern.startswith('/'):
                pattern = append_prefix + pattern
            if pattern.endswith('/'):
                pattern = pattern[:-1] + append_suffix + '/'
            else:
                extra = pattern
                pattern += append_suffix
            if negation:
                pattern = '!' + pattern
                if extra:
                    extra = '!' + extra
            for p in [pattern, extra]:
                if p and p not in result:
                    result[p] = rule_from_pattern(p, source=(filepath, lineno) if filepath else None, **self.kwargs)
        return list(result.values())

    @classmethod
    def trans_lines(cls, lines=None):
        result = []
        if not lines:
            return result
        for line in lines:
            filepath, lineno, line = cls.trace_line(line)
            line = line.strip()
            if line == '' or line[0] == '#' or line == '/':
                continue
            result.append((filepath, lineno, line))
        return result

    def match(self, full_path):
        if not self.lines:
            return False
        rules = self.generate_rules(self.trans_lines(self.lines))
        return self.check_match(full_path, rules, self.calc_negation(rules))

    def new_match(self, lines=None):
        lines = chain(*(x for x in (self.lines, lines) if x))
        rules = self.generate_rules(self.trans_lines(lines))
        return lambda full_path: self.check_match(full_path, rules, self.calc_negation(rules))


class GeneralMatcher:
    matcher_cls = Matcher

    def __init__(self, sep='/', lines=None):
        self._sep = sep
        self._matcher = self.matcher_cls(self._trans_lines(lines))

    def _trans_base(self, line):
        return line.replace(self._sep, '/')

    def _trans_lines(self, lines):
        if not lines:
            return lines
        result = []
        for line in lines:
            filepath, lineno, line = self.matcher_cls.trace_line(line)
            result.append((filepath, lineno, self._trans_base(line)))
        return result

    def match(self, s):
        return self._matcher.match(self._trans_base(s))

    def new_match(self, lines=None):
        def wrapper(s):
            return match(self._trans_base(s))

        match = self._matcher.new_match(self._trans_lines(lines))
        return wrapper


def glob2re(pattern):
    return fnmatch_pathname_to_regex(pattern, False, False)


def glob_compile(pattern, flags=0):
    return re.compile(glob2re(pattern), flags)


def glob_match(pattern, s, flags=0):
    return bool(re.match(glob2re(pattern), s, flags))
