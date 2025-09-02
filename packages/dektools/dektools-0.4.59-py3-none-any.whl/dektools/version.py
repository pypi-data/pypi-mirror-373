import re
import functools
import semver


def version_to_tuple(version):
    return semver.Version.parse(version, True).to_tuple()


def version_is_valid(version):
    return semver.Version.is_valid(version)


def version_is_release(version):
    try:
        ver = semver.Version.parse(version, True)
    except ValueError:
        return None
    else:
        return not ver.prerelease and not ver.build


def version_extract(s):
    rs = re.search('[0-9]+.', s)
    if rs:
        index = rs.span()[0]
        if index:
            s = s[index:]
    semver.Version.parse(s)
    return s


def version_cmp_raw(x, y, cache=None, trans=None):
    def sure(v):
        if isinstance(v, str):
            if cache:
                if v not in cache:
                    u = trans(v) if trans else v
                    cache[v] = semver.Version.parse(u, True)
                return cache[v]
            else:
                u = trans(v) if trans else v
                return semver.Version.parse(u, True)
        return v

    return sure(x).compare(sure(y))


def version_cmp(trans=None):
    def wrapper(x, y):
        return version_cmp_raw(x, y, cache, trans)

    cache = {}
    return wrapper


def version_cmp_key(trans=None):
    return functools.cmp_to_key(version_cmp(trans))
