import string

default_digs = string.digits + string.ascii_uppercase

near_zero = 0.0000001


def int2base(x, base, digs=None):
    digs = digs or default_digs
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


class AlignNum:
    char = '0'

    @staticmethod
    def get_digit(value):
        return len(str(value))

    @classmethod
    def from_max(cls, value):
        return cls(cls.get_digit(value))

    def __init__(self, digit):
        self.digit = digit

    def align(self, value):
        sv = str(value)
        return self.char * (self.digit - len(sv)) + sv
