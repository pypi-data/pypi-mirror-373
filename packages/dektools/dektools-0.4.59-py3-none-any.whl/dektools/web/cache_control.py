SUPPORTED_DIRECTIVES_NUMBER = {
    "max-age",
    "s-maxage",
    "stale-while-revalidate",
    "stale-if-error"
}

SUPPORTED_DIRECTIVES_BOOL = {
    "public",
    "private",
    "no-store",
    "no-cache",
    "must-revalidate",
    "proxy-revalidate",
    "immutable",
    "no-transform"
}


def number(v):
    try:
        n = int(v)
    except ValueError:
        return None
    else:
        if n < 0:
            return None
        return n


def parse(s: str):
    result = {}
    directives = [[y.strip() for y in x.strip().split('=')] for x in s.lower().split(',')]
    for unpack in directives:
        if len(unpack) == 2:
            directive, v = unpack
        else:
            directive, v = unpack[0], None
        if directive in SUPPORTED_DIRECTIVES_NUMBER:
            n = number(v)
            if n is None:
                continue
            result[directive] = n
        elif directive in SUPPORTED_DIRECTIVES_BOOL:
            result[directive] = True
    return result


def stringify(obj: dict):
    result = []
    for k, v in obj.items():
        if isinstance(v, bool):
            if v:
                result.append(k)
        elif isinstance(v, int):
            result.append(f'{k}={v}')
    return ', '.join(result)


def value(obj: dict):
    if "no-cache" in obj or "no-store" in obj:
        return None
    v = obj.get("max-age")
    if v is not None:
        return v
    return obj.get("s-maxage")
