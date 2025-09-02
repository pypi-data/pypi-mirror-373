import gc
from .func import FuncAnyArgs


def get_referrers_base(target, drop, depth, default):
    if target is not default:
        if drop:
            drop = FuncAnyArgs(drop)
        for i in range(depth):
            result = []
            for x in gc.get_referrers(target):
                if not drop(x, result):
                    result.append(x)
            if not result:
                return default
            target = result[0]
    return target
