def _parseparam(s):
    while s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        while end > 0 and (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        if end < 0:
            end = len(s)
        f = s[:end]
        yield f.strip()
        s = s[end:]


def _parse_header(line):  # source:cgi.parse_header, https://github.com/python/cpython/issues/91217
    """Parse a Content-type like header.

    Return the main content-type and a dictionary of options.

    """
    parts = _parseparam(';' + line)
    key = parts.__next__()
    pdict = {}
    for p in parts:
        i = p.find('=')
        if i >= 0:
            name = p[:i].strip().lower()
            value = p[i + 1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    return key, pdict


default_ct_encoding = 'latin-1'


def get_content_type_key(line, encoding=None):
    if isinstance(line, bytes):
        return line.partition(b';')[0].strip().decode(encoding or default_ct_encoding)
    return line.partition(';')[0].strip()


def parse_content_type(line, encoding=None):
    if isinstance(line, bytes):
        line = line.decode(encoding or default_ct_encoding)
    return _parse_header(line)


def join_content_type(key, pdict):
    return '; '.join((key, *(f'{k}={v}' for k, v in pdict.items())))


def quick_split_ct(line):
    sl = line.split(';', 1)
    if len(sl) == 1:
        return sl[0].strip(), ''
    return tuple(x.strip() for x in sl)


def quick_join_ct(key: str, params: str):
    if params:
        return f"{key}; {params}"
    return key


if __name__ == '__main__':
    _s = b'text/html; charset=utf-8'
    _x = parse_content_type(_s)
    print(_x, join_content_type(*_x) == _s)
    print(get_content_type_key(_s))
