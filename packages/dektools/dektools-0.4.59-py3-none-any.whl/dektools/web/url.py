import os
import sys
import re
import json
from copy import copy, deepcopy
from collections import OrderedDict
from base64 import b64encode, b64decode
from urllib.parse import urlparse, urlunparse, parse_qsl, quote_plus, urljoin, unquote, quote


class Url:
    default_kwargs = dict(
        username=None,
        password=None,
        port=None,
        path='',
        params={},
        query={},
        fragment=''
    )

    @classmethod
    def new(cls, url):
        pt = urlparse(url)
        kwargs = dict(
            scheme=pt.scheme,  # need
            username=pt.username,
            password=pt.password,
            hostname=pt.hostname,  # need
            port=pt.port,
            path=pt.path,
            params=cls.params_to_dict(pt.params),
            query=cls.query_to_dict(pt.query),
            fragment=pt.fragment
        )
        return cls(**kwargs)

    def __init__(self, **kwargs):
        if 'scheme' not in kwargs or 'hostname' not in kwargs:
            raise KeyError('Url kwargs cannot find needed keys')
        self._kwargs = self.new_default_kwargs() | kwargs

    def __getattr__(self, item):
        return self._kwargs[item]

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self._kwargs == other.kwargs

    def copy(self):
        return self.replace()

    def replace(self, **kwargs):
        return self.__class__(**deepcopy({**self._kwargs, **kwargs}))

    def discard(self, *args):
        return self.replace(**self.new_default_kwargs(*args))

    def only(self, *args):
        return self.discard(*set(self.default_kwargs) - set(args))

    def update(self, **kwargs):
        self._kwargs.update(kwargs)
        return self

    def update_query(self, query):
        self._kwargs['query'].update(query)
        return self

    def update_params(self, params):
        self._kwargs['params'].update(params)
        return self

    @property
    def netloc(self):
        result = ''
        if self.username:
            result += self.username
        if self.password:
            result += f':{self.password}'
        if result:
            result += '@'
        result += self.hostname or ''
        if self.port is not None and self.port != 80:
            result += f':{self.port}'
        return result

    @property
    def origin(self):
        # https://stackoverflow.com/questions/48313084
        # The same-origin policy for file:/// URIs is implementation-dependent.
        return self.only('hostname', 'port')

    @property
    def value(self):
        return urlunparse((
            self._kwargs['scheme'],
            self.netloc,
            self._kwargs['path'],
            self.dict_to_params(self._kwargs['params']),
            self.dict_to_query(self._kwargs['query']),
            self._kwargs['fragment']
        ))

    @staticmethod
    def to_order_dict(d):
        return OrderedDict((k, d[k]) for k in sorted(d))

    @property
    def fixed(self):
        return urlunparse((
            self._kwargs['scheme'],
            self.netloc,
            self._kwargs['path'],
            self.dict_to_params(self.to_order_dict(self._kwargs['params'])),
            self.dict_to_query(self.to_order_dict(self._kwargs['query'])),
            self._kwargs['fragment']
        ))

    @property
    def attrs(self):
        return deepcopy(self._kwargs)

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def home(self):
        return self.discard('path', 'params', 'query', 'fragment')

    @property
    def uncertified(self):
        return self.discard('username', 'password')

    @property
    def filename(self):
        path = self.path
        while path:
            path, file = path.rsplit('/', 1)
            if file:
                file = unquote(file).strip()
                if file:
                    return file
        return self.hostname + '.html'

    @property
    def dirname(self):
        return os.path.splitext(self.filename)[0]

    def join(self, sub, allow_fragments=True):
        return join_url(self.value, sub, allow_fragments)

    @classmethod
    def new_default_kwargs(cls, *args):
        if not args:
            args = cls.default_kwargs.keys()
        return {k: copy(cls.default_kwargs[k]) for k in args}

    @staticmethod
    def params_to_dict(params):
        return dict(parse_qsl(params, True, separator=';'))

    @staticmethod
    def dict_to_params(params):
        return urlencode(params, separator=';')

    @staticmethod
    def query_to_dict(query):
        return dict(parse_qsl(query, True))

    @staticmethod
    def dict_to_query(query):
        return urlencode(query)


def get_url_scheme(url):
    m = re.match('^([a-z0-9-]+):', url)
    if m:
        groups = m.groups()
        if groups:
            return groups[0]


def is_data_url(url):
    return url.startswith('data:')


def join_data_url(url):
    if isinstance(url, str):
        mt = "text/plain"
        data = b64encode(url.encode('utf-8')).decode('latin-1')
    elif isinstance(url, bytes):
        mt = "application/octet-stream"
        data = b64encode(url).decode('latin-1')
    elif isinstance(url, (dict, list)):
        mt = "application/json"
        data = b64encode(json.dumps(url).encode('utf-8')).decode('latin-1')
    else:
        raise TypeError(f'Unknown type: {url}')
    return f"data:{mt};base64,{data}"


def split_data_url(url: str):
    index = url.find(':')
    url = url[index + 1:]
    index = url.find(',')
    meta = url[:index]
    data = url[index + 1:]
    if meta:
        ml = meta.split(';')
        if len(ml) == 1:
            if ml[0] == 'base64':
                mt = None
                data = b64decode(data)
            else:
                mt = ml[0]
                data = unquote(data)
        else:
            mt = ml[0]
            data = b64decode(data)
    else:
        mt = None
        data = unquote(data)
    return mt, data


def is_abs_url(url):
    return bool(get_url_scheme(url))


def get_url_ext(url):
    index = url.find('//')
    index = url.find('/', index + 2)
    if index == -1:
        return None
    index_start = index + 1
    index_end = len(url) - 1
    for i in range(index_start, index_end + 1):
        c = url[i]
        if c == '/':
            index_start = i + 1
        if c in {'?', '#'}:
            index_end = i
    index = url.rfind('.', index_start + 1, index_end)
    if index != -1:
        return url[index: index_end]
    return None


def join_url(base, url, allow_fragments=True):
    return urljoin(base, url, allow_fragments)


def guess_sub_site(url):
    def is_number(x):
        return re.match("^[0-9]+$", x)

    url = Url.new(url)
    paths = url.path.split('/')
    for path in paths:
        if is_number(path):
            return True
    if paths and is_number(paths[-1].split('.', 1)[0]):
        return True
    for value in url.query.values():
        if is_number(value):
            return True
    return False


def encode_uri_component(s):
    return quote(s, safe="!~*'()")


def urlencode(query, doseq=False, safe='', encoding=None, errors=None,
              quote_via=quote_plus, separator='&'):
    """Encode a dict or sequence of two-element tuples into a URL query string.

    If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.

    If the query arg is a sequence of two-element tuples, the order of the
    parameters in the output will match the order of parameters in the
    input.

    The components of a query arg may each be either a string or a bytes type.

    The safe, encoding, and errors parameters are passed down to the function
    specified by quote_via (encoding and errors only if a component is a str).
    """

    if hasattr(query, "items"):
        query = query.items()
    else:
        # It's a bother at times that strings and string-like objects are
        # sequences.
        try:
            # non-sequence items should not work with len()
            # non-empty strings will fail this
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # Zero-length sequences of all types will get here and succeed,
            # but that's a minor nit.  Since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved for consistency
        except TypeError:
            ty, va, tb = sys.exc_info()
            raise TypeError("not a valid non-string sequence "
                            "or mapping object").with_traceback(tb)

    l = []
    if not doseq:
        for k, v in query:
            if isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errors)

            if isinstance(v, bytes):
                v = quote_via(v, safe)
            else:
                v = quote_via(str(v), safe, encoding, errors)
            l.append(k + '=' + v)
    else:
        for k, v in query:
            if isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errors)

            if isinstance(v, bytes):
                v = quote_via(v, safe)
                l.append(k + '=' + v)
            elif isinstance(v, str):
                v = quote_via(v, safe, encoding, errors)
                l.append(k + '=' + v)
            else:
                try:
                    # Is this a sufficient test for sequence-ness?
                    x = len(v)
                except TypeError:
                    # not a sequence
                    v = quote_via(str(v), safe, encoding, errors)
                    l.append(k + '=' + v)
                else:
                    # loop over the sequence
                    for elt in v:
                        if isinstance(elt, bytes):
                            elt = quote_via(elt, safe)
                        else:
                            elt = quote_via(str(elt), safe, encoding, errors)
                        l.append(k + '=' + elt)
    return separator.join(l)


if __name__ == '__main__':
    url__ = "http://username:password@www.domain.com:8080/nothing;param1=some;param2=other?query1=val1&query2=val2#frag"
    pt__ = urlparse(url__)

    print(pt__.scheme)

    print(pt__.netloc)
    print(pt__.username)  # None
    print(pt__.password)  # None
    print(pt__.hostname)
    print(pt__.port)  # None

    print(pt__.path)  # ''
    print(pt__.params)  # ''
    print(pt__.query)  # ''
    print(pt__.fragment)  # ''

    url_ = Url.new(url__)
    print(url_.attrs)
    print(url_.value == url__)
    print(url_.home.value)
    print(url_.uncertified.value)
    print(url_.origin.value)
    print(url_.join('/sub?q=test'))

    print(get_url_scheme('about:blank'))
    print(get_url_scheme('chrome-extension:'))
    print(is_abs_url('about:blank'))
    print(is_abs_url('none'))

    print(Url.new('data:,').value)
