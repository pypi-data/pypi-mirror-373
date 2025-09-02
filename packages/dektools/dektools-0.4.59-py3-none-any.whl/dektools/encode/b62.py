import random
import base62
from ..common import cached_property


class Base62Int:
    charset_default = base62.CHARSET_DEFAULT

    def __init__(self, max_value, charset=None):
        self.max_value = max_value
        self.charset = charset or self.charset_default

    def to_str(self, value):
        return base62.encode(value, charset=self.charset)

    def to_str_extend(self, value, total=None):
        max_length = self.get_max_length(total)
        extend = max(max_length - self.max_length_int, 0)
        s = self.to_str(value)
        s += ''.join(
            [random.choice(self.charset_list) for _ in range(extend)])
        return s

    def get_max_length(self, total=None):
        fn = (lambda x: x * 2) if total is None else ((lambda _: total) if isinstance(total, int) else total)
        return fn(self.max_length_int)

    @cached_property
    def max_length_int(self):
        return len(self.to_str(self.max_value))

    @cached_property
    def charset_list(self):
        return list(self.charset)


class Base62Bytes:
    charset_default = base62.CHARSET_DEFAULT

    def __init__(self, charset=None):
        self.charset = charset or self.charset_default

    def to_str(self, value):
        if isinstance(value, str):
            value = value.encode('utf-8')
        elif isinstance(value, int):
            value = value.to_bytes(8, byteorder='big')
        return base62.encodebytes(value, charset=self.charset)
