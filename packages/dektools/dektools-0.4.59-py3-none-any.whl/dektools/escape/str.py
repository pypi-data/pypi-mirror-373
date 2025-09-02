import re
import codecs


def str_escape_wrap(s, escape='\\'):
    count = 0
    for x in reversed(s):
        if x != escape:
            break
        count += 1
    if count:
        wrap = not count % 2
        return s[:-((count + 1) // 2)], wrap
    return s, True


def str_escape_one_type(s, prefix, suffix, escape='\\'):
    return re.sub(
        f'{re.escape(prefix)}(({re.escape(escape)})+){re.escape(suffix)}',
        lambda x: prefix + len(x.group(1)) // len(escape) // 2 * escape + suffix, s
    )


def str_escape_unicode(s):
    return codecs.getdecoder("unicode_escape")(s.encode('utf-8'))[0]


def str_escape_split(s, delim, escaped='\\'):
    ret = []
    current = []
    itr = iter(s)
    for ch in itr:
        if ch == escaped:
            try:
                # skip the next character; it has been escaped!
                current.append(escaped)
                current.append(next(itr))
            except StopIteration:
                pass
        elif ch == delim:
            # split! (add current to the list and reset it)
            ret.append(''.join(current))
            current = []
        else:
            current.append(ch)
    ret.append(''.join(current))
    return ret


def str_escape_custom(s, mapping=None, escaped='\\', keep=False, process=None, skip=None):
    def _process(x, y=False):
        if process:
            process(mapping, cursor, x, y)

    def get_target(index):
        for k in mapping.keys():
            if k == s[index: index + len(k)]:
                return k

    if mapping is None:
        mapping = {}
    elif isinstance(mapping, (tuple, list, set)):
        mapping = {x: x for x in mapping}
    elif not isinstance(mapping, dict):
        mapping = {mapping: mapping}
    r = ""
    cursor = 0
    length = len(s)
    while cursor < length:
        c = s[cursor]
        if c == escaped:
            cursor += len(escaped)
            c = get_target(cursor)
            if c is None:
                c = s[cursor]
            if skip and skip(c, cursor) or keep and c not in mapping and c != escaped:
                r += escaped + c
                _process(c, True)
            else:
                r += mapping.get(c, c)
                _process(c)
        else:
            r += c
            _process(None)
        cursor += len(c)
    return r


def str_escape_special(s, escape='\\'):
    r = ""
    escaping = False
    for x in s:
        if not escaping and x == escape:
            escaping = True
        else:
            r += x
            escaping = False
    return r
