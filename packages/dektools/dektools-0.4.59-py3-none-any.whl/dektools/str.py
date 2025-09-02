import re
import string
import random
import hashlib
import unicodedata
from collections.abc import Mapping


def is_wide_char(c):
    return "\u2E80" <= c <= "\u9FFF"


class Unicode:
    def __init__(self, s):
        self.value = s

    def __len__(self):
        result = 0
        for c in self.value:
            if is_wide_char(c):
                result += 1
            result += 1
        return result

    def __getitem__(self, item):
        if isinstance(item, int):
            start = item
            stop = item + 1
            step = 1
        else:
            start = item.start or 0
            stop = len(self.value) if item.stop is None else item.stop
            if stop < 0:
                stop = len(self.value) + stop
            step = item.step or 1
        result = ''
        cursor = 0
        for c in self.value:
            if cursor >= stop:
                break
            elif cursor >= start:
                result += c
            if is_wide_char(c):
                cursor += 1
            cursor += step
        return result


class FormatDict(Mapping):
    empty = type('empty', (), {})

    def __init__(self, kwargs, missing=None):
        self.kwargs = kwargs
        self.missing = missing

    @staticmethod
    def __missing(key):
        return f'{{{key}}}'

    def __getitem__(self, item):
        value = self.kwargs.get(item, self.empty)
        if value is self.empty:
            return (self.missing or self.__missing)(item)
        else:
            return value

    def __iter__(self):
        return iter(self.kwargs)

    def __len__(self):
        return len(self.kwargs)


formatter = string.Formatter()


def to_slice(s):
    items = s.split(':')
    args = []
    for x in items:
        x = x.strip()
        if x:
            args.append(int(x))
        else:
            args.append(None)
    if len(args) == 1:
        return args[0]
    return slice(*args)


def str_format_partial(s, kwargs, missing=None):
    return formatter.vformat(s, (), FormatDict(kwargs, missing))


def str_align_number(index, total):
    lt = len(str(total))
    li = len(str(index))
    return max(0, lt - li) * '0' + str(index)


def str_split(s, sep=None):
    result = []
    for x in s.split(' ' if sep is None else sep):
        x = x.strip()
        if x:
            result.append(x)
    return result


_var_marker_ld = set(string.ascii_lowercase + string.digits)
_var_marker_u = set(string.ascii_uppercase)
_var_marker_d = set(string.digits)


def to_var_format(*str_list):
    r = []
    for x in str_list:
        s = ""
        for i in range(len(x)):
            if x[i] in _var_marker_ld:
                s += x[i]
            else:
                if s:
                    r.append(s)
                    s = ""
                if x[i] in _var_marker_u:
                    s += x[i].lower()
        if s:
            r.append(s)
    if r and r[0][0] in _var_marker_d:
        r[0] = '_' + r[0]
    return r


def to_var_format_classname(r):
    return ''.join(x.capitalize() for i, x in enumerate(r))


def to_var_format_camel(r):
    return ''.join(x if i == 0 else x.capitalize() for i, x in enumerate(r))


def to_var_format_pascal(r):
    return ''.join(x.capitalize() for x in r)


def to_var_format_hungarian(r):
    return '_'.join(r)


def to_var_format_py(r):
    return ''.join(r)


# shlex.split need to always use quote at path on Windows
def shlex_split(s):
    s, indexes_list = deep_format_indexes(s, r'[ \t\f\r]+"|^"', r'"', nest=False)
    if not indexes_list:
        return split_table_line(s)
    result = []
    last_index = 0
    for indexes_range in indexes_list:
        left = indexes_range[0][0]
        if left > last_index:
            result.extend(split_table_line(s[last_index:left]))
        result.append(s[indexes_range[0][-1]:indexes_range[-1][0]])
        last_index = indexes_range[-1][-1]
    if len(s) - 1 > last_index:
        items = split_table_line(s[last_index:])
        if len(items) != 1 or items[0]:
            result.extend(items)
    return result


def shlex_join(xx):
    return ' '.join(shlex_quote(x) for x in xx)


def shlex_quote(s, wrap=False):
    escape = '\\'
    target = '"'
    targets = escape + target
    result = ""
    for x in s:
        if x in targets:
            x = escape + x
            wrap = True
        elif x in ' \t\f\r':
            wrap = True
        result += x
    if wrap:
        result = f"{target}{result}{target}"
    return result


def deep_format(s, left, right, handler, escape='\\', escape_set=None, nest=True):
    s, indexes_list = deep_format_indexes(s, left, right, escape, escape_set, nest)
    return deep_format_items(s, indexes_list, handler)


def deep_format_indexes(s, left, right, escape='\\', escape_set=None, nest=True):
    def is_match(x, y):
        if isinstance(x, str):
            return x == y
        else:
            return x.match(y)

    rcl = re.compile(left)
    rcr = re.compile(right)
    escape_set = {rcl, rcr, escape, *(escape_set or ())}
    cursor = 0
    escape_str = ''
    escape_marker = set()
    while True:
        index = s.find(escape, cursor)
        if index == -1:
            if cursor != 0:
                escape_str += s[cursor:]
            break
        index_escape = index + len(escape)
        retain = all(
            not is_match(x, s[index_escape:index_escape + len(x if isinstance(x, str) else x.pattern)])
            for x in escape_set)
        escape_str = f'{escape_str}{s[cursor:index]}{escape if retain else ""}{s[index_escape:index_escape + 1]}'
        if not retain:
            escape_marker.add(len(escape_str) - 1)
        cursor = index_escape + 1
    if cursor != 0:
        s = escape_str

    rc = re.compile(f'({left})|{right}')
    cursor = s
    pos_list = []
    while True:
        if not nest and pos_list and pos_list[-1][0]:
            m = rcr.search(cursor)
            force_right = True
        else:
            m = rc.search(cursor)
            force_right = False
        if m:
            span = m.span()
            index = len(s) - len(cursor) + span[0]
            if set(range(index, index + span[1] - span[0])).isdisjoint(escape_marker):
                pos_list.append((
                    False if force_right else m.groups()[0] is not None,
                    [len(s) - len(cursor) + x for x in span]
                ))
            cursor = cursor[span[1]:]
        else:
            break

    indexes_list = []
    pos_stack = []
    for pos in pos_list:
        if pos[0]:
            pos_stack.append(pos)
        else:
            if pos_stack and pos_stack[-1][0]:
                indexes_list.append((pos_stack[-1][1], pos[1]))
                pos_stack.pop()
    return s, indexes_list


def deep_format_items(s, indexes_list, handler):
    def format_items(_range, _items):
        if not _items:
            return s
        _result = ''
        _index = _range[0][1]
        for _item in _items:
            _result += s[_index: _item[0][0][0]] + str(_item[1])
            _index = _item[0][1][1]
        _result += s[_index: _range[1][0]]
        return _result

    items_stack = []
    for indexes_range in indexes_list:
        index_sub = None
        for i in reversed(range(len(items_stack))):
            item = items_stack[i]
            if indexes_range[0][1] < item[0][0][1] and item[0][1][0] < indexes_range[1][0]:
                index_sub = i
            else:
                break
        if index_sub is None:
            expression = s[indexes_range[0][1]: indexes_range[1][0]]
        else:
            expression = format_items(indexes_range, items_stack[index_sub:])
            items_stack = items_stack[:index_sub]

        value = handler(expression, s[slice(*indexes_range[0])], s[slice(*indexes_range[1])])
        items_stack.append([indexes_range, value])

    return format_items([[0, 0], [len(s), len(s)]], items_stack)


def str_format_var(s, begin='{', end='}', escape='\\'):
    fmt = ['']
    args = []
    arg = None
    escaping = False
    same = begin == end
    swap = False
    for x in s:
        if not escaping and x == escape:
            escaping = True
        else:
            if escaping:
                if arg is None:
                    fmt[-1] += x
                else:
                    arg += x
            else:
                if x == begin and (not same or not swap):
                    swap = True
                    if arg is None:
                        arg = ""
                    else:
                        arg += x
                else:
                    if x == end:
                        swap = False
                        if arg is None:
                            fmt[-1] += x
                        else:
                            args.append(arg)
                            arg = None
                            fmt.append('')
                    else:
                        if arg is None:
                            fmt[-1] += x
                        else:
                            arg += x
            escaping = False
    return lambda xx, ma=None, mi=None: _str_format_var_final(fmt, xx, ma, mi), args


def _str_format_var_final(fmt, args, mapping=None, missing=None):
    s = ""
    cursor = 0
    while True:
        s += fmt[cursor]
        if cursor == len(fmt) - 1:
            break
        arg = args[cursor]
        if mapping and arg in mapping:
            arg = mapping[arg]
        elif missing:
            arg = missing(arg)
        s += str(arg)
        cursor += 1
    return s


def decimal_to_short_str(num, sequence):
    lst = []
    sequence_length = len(sequence)
    num = num - 1
    if num > sequence_length - 1:
        while True:
            d = int(num / sequence_length)
            remainder = num % sequence_length
            if d <= sequence_length - 1:
                lst.insert(0, sequence[remainder])
                lst.insert(0, sequence[d - 1])
                break
            else:
                lst.insert(0, sequence[remainder])
                num = d - 1
    else:
        lst.append(sequence[num])
    return "".join(lst)


def tab_str(s, n, p=4, sl=False):  # s: list of str or str
    if isinstance(s, str):
        s = [s]
    r = []
    for x in s:
        if sl:
            x = x.strip()
            if x:
                r.append(x)
        else:
            r.append(x)
    r = '\n'.join(r).split('\n')
    return '\n'.join([' ' * n * p + x for x in r])


def startswith(s, *items, reverse=False):
    for item in items:
        if reverse:
            yield item.startswith(s)
        else:
            yield s.startswith(item)


def endswith(s, *items, reverse=False):
    for item in items:
        if reverse:
            yield item.endswith(s)
        else:
            yield s.endswith(item)


def slugify(value, allow_unicode=False, sep='', case=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    if case is True:
        value = value.upper()
    elif case is False:
        value = value.lower()
    value = re.sub(r'[^\w\s-]', sep, value.lower())
    return re.sub(rf'[{sep}\s]+', sep, value).strip(f'-_{sep}')


def shorted(s, limit, count, offset=-1):
    if len(s) <= limit:
        return s
    count = min(limit, count)
    length = len(s) - limit + count
    if count % 2:
        hl = count // 2 + 1
        end = -1
    else:
        hl = count // 2
        end = None
    replaced = hashlib.shake_256(s.encode('utf-8')).hexdigest(hl)
    if end is not None:
        replaced = replaced[:end]
    if offset >= 0:
        offset = min(offset, limit - len(replaced))
        return s[:offset] + replaced + s[offset + length:]
    else:
        offset = max(offset, len(replaced) - limit - 1)
        return s[:offset + 1 - length] + replaced + ("" if offset == -1 else s[offset + 1:])


def triple_find(s, first, left, right):  # s: str | bytes
    i = s.find(first)
    if i == -1:
        return None
    il = s.rfind(left, 0, i)
    if il == -1:
        return None
    ir = s.find(right, i + len(first))
    if ir == -1:
        return None
    return s[il + len(left):ir]


def replace(s, d):
    return re.sub("|".join(d.keys()), lambda x: d[x.group(0)], s)


def number_tuple(s):
    return tuple(int(x) for x in re.findall(r'\d+', s))


def hex_random(length):
    ss = string.digits + 'abcdef'
    return ''.join(random.choice(ss) for _ in range(length))


def split_table_line(s, maxsplit=None, sep=None, strip=True):
    if sep is None:
        return re.split(r'[ \t\f\r]+', s.strip(), maxsplit or 0)
    else:
        if strip:
            s = s.strip()
        return [x.strip() if strip else x for x in s.split(sep, -1 if maxsplit is None else maxsplit)]


def comment_code(code, comment, reverse=False, again=False):
    def do_comment(s):
        if reverse:
            result.append(s[len(comment[0]):(- len(comment[1])) if comment[1] else None])
        else:
            result.append(comment[0])
            result.append(s)
            if comment[1]:
                result.append(comment[1])

    if isinstance(comment, str):
        comment = [comment, '']
    elif len(comment) == 1:
        comment = [comment[0], '']
    result = []
    cursor = 0
    index = 0
    while True:
        try:
            x = code[index]
        except IndexError:
            break
        if x == '\r':
            do_comment(code[cursor:index])
            if index < len(code) - 1 and code[index + 1] == '\n':
                result.append('\r\n')
                index += 1
            else:
                result.append('\r')
            cursor = index + 1
        elif x == '\n':
            do_comment(code[cursor:index])
            result.append('\n')
            cursor = index + 1
        index += 1
    if cursor < len(code):
        do_comment(code[cursor:])
    if again:
        append = ' '
        if reverse:
            if len(result) < 2 or len(result) == 2 and result[-1].startswith('\r'):
                item = result.pop(0)
                result.insert(0, item[1 + len(append):])
                result.insert(0, item[0])
        else:
            if len(result) < 4:
                item = result.pop(1)
                result.insert(1, item[1:])
                result.insert(1, append)
                result.insert(1, item[0])
    return ''.join(result)


class Fragment:
    @classmethod
    def format(cls, content, amap):
        if not amap:
            return content
        fragment = cls(content, *amap)
        from_list = iter(amap.keys())
        to_list = iter(amap.values())
        result = fragment[0]
        for i in range(1, len(fragment)):
            f, t = next(from_list), next(to_list)
            if i < len(fragment) - 1:
                x = fragment.content[fragment.indexes[i - 1] + len(f):fragment.indexes[i]]
            else:
                x = fragment.content[fragment.indexes[i - 1] + len(f):]
            result += t + x
        return result

    @classmethod
    def replace(cls, content, list_of_pairs, reverse=False):
        if not list_of_pairs:
            return content
        indexes = [1, 0] if reverse else [0, 1]
        fragment = cls(content, *(pairs[indexes[0]] for pairs in list_of_pairs), sep=True)
        result = ''
        for i, pairs in enumerate(list_of_pairs):
            result += fragment[2 * i] + pairs[indexes[1]]
        tail = fragment[2 * len(list_of_pairs):]
        if tail:
            result += tail
        return result

    @classmethod
    def replace_safe_again(cls, content, list_of_pairs, reverse=False):
        # For each pair, k,v should not contain each other
        try:
            content = cls.replace(content, list_of_pairs, reverse)
        except IndexError as e:
            # if running not at first time, check those reversed strings
            try:
                cls(content, *(pairs[0 if reverse else 1] for pairs in list_of_pairs))
            except IndexError:
                raise e
        else:
            return content

    def __init__(self, content, *separators, sep=False):  # content: str | bytes
        self.content = content
        indexes = self.split(content, separators)
        if sep:
            self.indexes = [indexes[i // 2] + len(separators[i // 2]) if i % 2 else indexes[i // 2]
                            for i in range(2 * len(separators))]
        else:
            self.indexes = indexes

    def __len__(self):
        return len(self.indexes) + 1

    def __getitem__(self, item):
        ii = list(range(len(self.indexes) + 1))[item]
        if not isinstance(ii, list):
            ii = [ii]
        result = self.type()
        for i in ii:
            if i == 0:
                result += self.content[:self.indexes[i]]
            elif i == len(self.indexes):
                result += self.content[self.indexes[i - 1]:]
            else:
                result += self.content[self.indexes[i - 1]:self.indexes[i]]
        return result

    def sub(self, begin, end=None):  # begin: tuple | int, end: tuple | int | None
        if isinstance(begin, int):
            index, offset = 0, begin
        else:
            index, offset = begin
        _begin = self.indexes[index] + offset
        if isinstance(end, int):  # length
            _end = _begin + end
        elif isinstance(end, tuple):  # to index
            index, offset = end
            _end = self.indexes[index] + offset
        else:  # to end
            _end = None
        return self.content[_begin:_end]

    @property
    def type(self):
        return self.content.__class__

    @staticmethod
    def split(content, separators):
        indexes = []
        cursor = 0
        for separator in separators:
            index = content.find(separator, cursor)
            if index == -1:
                raise IndexError(f"Cannot find {separator} from {cursor}")
            indexes.append(index)
            cursor = index + len(separator)
        return indexes


if __name__ == '__main__':
    fx, a = str_format_var('aaa{bbb}ccc{ddd}')
    print(fx([x.upper() for x in a]))

    fx, a = str_format_var('aaa$bbb$ccc$ddd$', '$', '$')
    print(fx([x.upper() for x in a]))

    print(decimal_to_short_str(
        int(hashlib.md5('test'.encode("ascii")).hexdigest(), 16),
        string.digits + string.ascii_letters + '_')
    )

    print(replace("I have a dog but not a cat.", {"dog": "cat", "cat": "dog"}))

    print(Fragment(string.ascii_uppercase.encode(), b'EF', b'OP', b'UV')[::2])
    print(Fragment(string.ascii_uppercase.encode(), b'EF', b'OP', b'UV', sep=True)[::2])

    print(Fragment.format(string.ascii_uppercase, {'EF': 'ef', 'OP': 'op', 'UV': 'uv'}))

    print(triple_find(string.ascii_uppercase.encode(), b'OP', b'EF', b'UV'))

    _s = 'ab\r\n'
    c = ['#', ]
    print(comment_code(_s, c, again=True))
    print(comment_code(comment_code(_s, c, again=True), c, reverse=True, again=True) == _s)

    print(deep_format(
        "-\\n\\\\{abc{de}f{123}}g\\h{ijk}lmn{>>abc}x{//abc}xx{a\\}\\", r"\{(>>|>|=|$|\*|//|/)?", r"\}",
        lambda x, aa, bb: ' [--->' + aa + '<--->' + x + '<--->' + bb + '<---] ', escape='\\'
    ))

    print(shlex_split(r'  "abc\defg\"hijk "lmn"  '))
    _s = ''' ab\\cd" e'fg" hi '''
    print(shlex_split(shlex_quote(_s))[0] == _s)
