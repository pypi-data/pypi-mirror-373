import json
import typing
import collections
from .simple import is_list, is_dict


def _flat(data, keys, sep, result):
    key = sep.join(keys)
    if isinstance(data, typing.Mapping):
        result[key] = json.dumps(data, ensure_ascii=False, indent=4)
        for k, v in data.items():
            _flat(v, [*keys, k], sep, result)
    elif isinstance(data, (list, tuple)):
        result[key] = json.dumps(data, ensure_ascii=False, indent=4)
        for i, x in enumerate(data):
            _flat(x, [*keys, str(i)], sep, result)
    else:
        result[key] = str(data)


def flat(data, sep='.'):
    result = collections.OrderedDict()
    _flat(data, [], sep, result)
    return result


def flat_to_list(data, check):
    if is_dict(data):
        if check(data):
            return [data]
        else:
            return flat_to_list(list(data.values()), check)
    elif is_list(data):
        result = []
        for d in data:
            result.extend(flat_to_list(d, check))
        return result
    else:
        raise TypeError(f'unknown type: {data}')
