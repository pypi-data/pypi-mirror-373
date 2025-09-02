import math
from .simple import is_dict


def diff_dict_weight(a, b):
    weight = 0
    aa, bb = set(a), set(b)
    same = aa & bb
    for k in same:
        ax, bx = a[k], b[k]
        if is_dict(ax):
            if is_dict(bx):
                weight += diff_dict_weight(ax, bx)
            else:
                weight += 1 + diff_dict_weight(ax, {})
        elif ax != bx:
            weight += 1
    for k in aa - same:
        ax = a[k]
        weight += 1
        if is_dict(ax):
            weight += diff_dict_weight(ax, {})
    weight += len(bb) - len(same)
    return weight


def diff_min_items(array, data, item=None):
    tm = {}
    min_w = math.inf
    for i, x in enumerate(array):
        w = diff_dict_weight(data, x if item is None else item(x, i, array))
        if w not in tm:
            tm[w] = []
        tm[w].append(i)
        if w < min_w:
            min_w = w
    return tm[min_w] if tm else []
