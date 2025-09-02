def get_bases_reduce(bases):
    bases_reduce = [1]
    for x in reversed(bases):
        bases_reduce.insert(0, bases_reduce[0] * x)
    return bases_reduce


def format_bases(x, bases_reduce, trans):
    result = ''
    for index, base in enumerate(bases_reduce):
        value = x // base
        x -= value * base
        r = trans(value, index, x, bases_reduce, result)
        if r is None:
            break
        else:
            result += r
    return result


def format_duration(x, names=None, bases=None, trans=None):
    def trans_default(v, i, *_):
        return f'{v}{names[i]}' if v else ''

    names = names or ['d ', 'h ', 'm ', 's ', 'ms']
    return format_bases(x, get_bases_reduce(bases or [24, 60, 60, 1000]), trans or trans_default)


def format_duration_hms(x, fmt=None):
    def trans(v, i, *_):
        return (fmt or '%02d%s') % (v, ":" if i < 2 else "") if i < 3 else None

    return format_duration(x // 1000 * 1000, bases=[60, 60, 1000], trans=trans)


def _format_file_size(x, bases, names, fmt=None):
    def trans(v, i, r, br, ret):
        return None if ret else ((fmt[1] if i == len(names) - 1 else fmt[0]) % (v + r / br[i], names[i]) if v else '')

    default_fmt_list = '%.2f %s', '%d %s'
    if fmt is None:
        fmt = default_fmt_list
    elif isinstance(fmt, str):
        fmt = fmt, default_fmt_list[1]
    return format_bases(x, get_bases_reduce(bases), trans)


def format_file_size(x, names=None, fmt=None):
    names = names or ['TB', 'GB', 'MB', 'KB', 'B']
    return _format_file_size(x, [1000] * 4, names, fmt)


def format_file_size_iec(x, names=None, fmt=None):
    names = names or ['Tib', 'Gib', 'Mib', 'Kib', 'B']
    return _format_file_size(x, [1024] * 4, names, fmt)
