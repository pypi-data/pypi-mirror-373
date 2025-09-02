from pympler import summary, muppy


def objects(*args, **kwargs):
    return muppy.get_objects(*args, **kwargs)


def summ(o=None):
    o = o or objects()
    return summary.summarize(o)


def prints(s=None, *args, **kwargs):
    s = s or summ()
    summary.print_(s, *args, **kwargs)
