from copy import deepcopy


def partial_sorted(s, b, h):
    """
    samples:
        s ->  {a, b, c, d} # total set
        b ->  {a:{b}, c:{d}, b: {c}} # a > b, c > d, b > c
        h -> if relation not in b, func h give the relation
    """
    b = deepcopy(b)

    rb = {}  # reverse set of b
    for k, vs in b.items():
        for x in vs:
            rb.setdefault(x, set()).add(k)

    bs = set()  # all elements in b
    for k, vs in b.items():
        bs.add(k)
        bs.update(vs)

    rest = s - bs  # rest of s

    result = []

    while bs:
        for x in sorted(bs, key=h, reverse=True):
            t = rb.get(x)
            if not t:
                result.insert(0, x)
                bs.remove(x)
                rb.pop(x, None)
                for y in b.get(x) or []:
                    z = rb.get(y)
                    if z:
                        z.discard(x)

    return list(sorted(rest, key=h)) + result


def sub_sorted(array, sub, insert_head=False):
    def get_item(item):
        try:
            return sub.index(item)
        except ValueError:
            return -1 if insert_head else len(sub)

    return sorted(array, key=lambda x: (get_item(x), x))


if __name__ == '__main__':
    print(partial_sorted({'a', 'b', 'c', 'd', 'z', 'x'}, {'a': {'b'}, 'd': {'c'}, 'b': {'d', 'x'}}, lambda x: x))
    print(sub_sorted(['a', 'b', 'c'], ['c','b']))
