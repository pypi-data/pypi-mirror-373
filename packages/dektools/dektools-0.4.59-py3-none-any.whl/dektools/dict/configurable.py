import functools
from ..common import cached_property


class Assignment:
    def __init__(self, schema, default_do='y'):
        self.schema = schema
        self.default_do = default_do

    @cached_property
    def schema_flat(self):
        def walk(d, p):
            r = {}
            for k, v in d.items():
                pp = (*p, k)
                if isinstance(v, str):
                    r[pp] = v
                elif isinstance(v, list):
                    r[pp] = v[0]
                    if isinstance(v[1], dict):
                        r.update(walk(v[1], pp))
                else:
                    r.update(walk(v, pp))
            return r

        return walk(self.schema, ())

    def merge(self, *args):
        return functools.reduce(lambda x, y: self._merge_dict(x, y, ()), args)

    def _merge_dict(self, m, n, p):
        result = {}
        empty = object()
        keys = {*m, *n}
        for k in keys:
            pp = (*p, k)
            x = m.get(k, empty)
            y = n.get(k, empty)
            r = empty
            if x is empty:
                if y is not empty:
                    r = y
            else:
                if y is empty:
                    r = x
                else:
                    if isinstance(x, dict):
                        r = self._merge_dict(x, y, pp)
                    elif isinstance(x, list):
                        r = self._merge_list(x, y, pp)
                    else:
                        r = self.execute(pp, x, y)
            if r is not empty:
                result[k] = r
        return result

    def _merge_list(self, m, n, p):
        return self.execute(p, m, n)

    def execute(self, p, x, y):
        do = self.schema_flat.get(p) or self.default_do
        return getattr(self, f'do_{do}')(x, y, p)

    def do_x(self, x, y, p):
        return x

    def do_y(self, x, y, p):
        return y

    def do_xy(self, x, y, p):
        return [*x, *y]

    def do_yx(self, x, y, p):
        return [*y, *x]

    def do_m(self, x, y, p):
        xl = len(x)
        yl = len(y)
        length = max(xl, yl)
        result = []
        empty = object()
        for i in range(length):
            if i < xl:
                a = x[i]
            else:
                a = empty
            if i < yl:
                b = y[i]
            else:
                b = empty
            if a is empty:
                r = b
            else:
                if b is empty:
                    r = a
                else:
                    if isinstance(a, dict):
                        r = self._merge_dict(a, b, p)
                    else:
                        r = self.execute(p, a, b)
            result.append(r)
        return result


if __name__ == '__main__':
    print(Assignment({
        'a': 'x',
        'b': {
            'c': {
                'd': 'xy'
            }
        },
        'e': [
            'm',
            {
                'f': 'y'
            }
        ]
    }
    ).merge(
        {'a':
             [1, 2, 3],
         'b':
             {'c':
                  {'d':
                       [4, 5, 6]
                   }
              },
         'e': [
             {
                 'r': 123
             }
         ]
         },
        {'a':
             [7, 8, 9],
         'b':
             {'c':
                  {'d':
                       [1, 3, 7]
                   }
              },
         'e': [
             {
                 'p': 2
             },
             {
                 'm': 3
             }
         ],
         'f': [2]
         }
    ))
