import datetime

try:
    import zoneinfo
except ImportError as e:
    if "'zoneinfo'" in e.args[0]:
        pass
    else:
        raise
    from backports import zoneinfo

TZ_CURRENT = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
TZ_UTC = zoneinfo.ZoneInfo('UTC')


def get_tz(tz=None):
    if not tz:
        tz = TZ_CURRENT
    if isinstance(tz, str):
        tz = zoneinfo.ZoneInfo(tz)
    return tz


def now(delta=None, tz=None):
    dt = datetime.datetime.now(tz=tz or TZ_CURRENT)
    if delta:
        dt += datetime.timedelta(microseconds=delta)
    return dt


def get_day_index():
    return (datetime.datetime.now(tz=TZ_UTC) - datetime.datetime.fromtimestamp(0, tz=TZ_UTC)).days


class DateTime:
    empty = type('empty', (), {})
    """
        %Y Year with century as a decimal number(2015)

        %m Month

        %d Day of the month as a zero-padded decimal number(1)

        %I Hour (12-hour clock) as a zero-padded decimal number(01)

        %H Hour (24-hour clock)

        %M Minute as a zero-padded decimal number(33)

        %S Second

        %f microseconds

        %p Locale’s equivalent of either AM or PM(PM)

        %b Month as locale’s abbreviated name(Jun)
    """

    def __init__(self, tz=None):
        self.tz = None if tz is self.empty else get_tz(tz)

    def from_x(self, s, *f_list):
        if not s:
            return None
        if s == "now":
            return datetime.datetime.now(self.tz)
        if f_list:
            date = None
            for f in f_list:
                try:
                    date = datetime.datetime.strptime(s, f).replace(tzinfo=self.tz)
                except ValueError:
                    pass
            return date
        elif isinstance(s, list):
            return datetime.datetime(*s, tzinfo=self.tz)
        else:
            s = float(s)
            if s < 0:
                try:
                    return datetime.datetime.fromtimestamp(0, tz=self.tz) + datetime.timedelta(seconds=s)
                except OverflowError:
                    return None
            else:
                return datetime.datetime.fromtimestamp(s, tz=self.tz)

    def from_str(self, s, fmt=None):
        if fmt is None:
            r = datetime.datetime.fromisoformat(s)
        else:
            r = datetime.datetime.strptime(s, fmt)
        if self.tz:
            r = r.astimezone(self.tz)
        return r

    def to_str(self, obj=None, fmt=None):
        if obj is None:
            obj = datetime.datetime.now(self.tz)
        if self.tz:
            obj = obj.astimezone(self.tz)
        if fmt is None:
            return obj.isoformat()
        else:
            return obj.strftime(fmt)

    @staticmethod
    def reformat(value, a, b):
        return datetime.datetime.strptime(value, a).strftime(b)
