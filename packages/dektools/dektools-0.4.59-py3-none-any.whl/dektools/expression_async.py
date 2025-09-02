from async_eval import eval


def eval_await(func, *args, **kwargs):
    return eval(f"await func(*args, **kwargs)", dict(func=func, args=args, kwargs=kwargs))


def eval_for(func, *args, **kwargs):
    return eval('[item async for item in func(*args, **kwargs)]', dict(func=func, args=args, kwargs=kwargs))
