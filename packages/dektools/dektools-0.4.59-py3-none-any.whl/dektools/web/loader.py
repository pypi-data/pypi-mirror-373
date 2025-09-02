import os
from uuid import uuid4
from hashlib import sha256
from dektools.file import read_text
from ..common import classproperty
from .url import encode_uri_component


class WebLoader:
    replaced_with_random = '__webloader_replaced_with_random__'
    replaced_with = '_' + uuid4().hex

    def __init__(self, html=None, js=None, css=None, once=True, html_append='document.body.appendChild'):
        self._html = html or []
        self._js = js or []
        self._css = css or []
        self._once = once
        self._html_append = html_append

    @classproperty
    def replaced_init_js(self):
        if self.replaced_with == 'window':
            return ''
        return 'let %s = {};\n' % self.replaced_with

    @classmethod
    def replaced_var(cls, name):
        return f'{cls.replaced_with}.{name}'

    @classmethod
    def new_var(cls):
        return '_' + sha256(f"{cls.__name__}:{uuid4().hex}".encode('utf-8')).hexdigest()

    @classmethod
    def from_path(cls, src, replace=False, **kwargs):
        def handle_file(p):
            ext = os.path.splitext(p)[-1]
            if ext == '.html':
                html.append(read_text(p))
            elif ext == '.js':
                text = read_text(p)
                if replace:
                    text = text.replace(cls.replaced_with_random, cls.replaced_with)
                js.append(text)
            elif ext == '.css':
                css.append(read_text(p))

        html = []
        js = []
        css = []
        if os.path.isdir(src):
            for base, _, files in os.walk(src):
                for file in files:
                    handle_file(os.path.join(base, file))
        elif os.path.isfile(src):
            handle_file(src)
        html = (kwargs.pop('html', None) or []) + html
        js = (kwargs.pop('js', None) or []) + js
        css = (kwargs.pop('css', None) or []) + css
        return cls(html=html, js=js, css=css, **kwargs)

    @staticmethod
    def new_str(s):
        return f'decodeURIComponent("{encode_uri_component(s)}")'

    def _append_not_once(self, s, var):
        if not self._once:
            return s + f"""
        setInterval(function () {{
            if (!{var}.parentElement)
                {self._html_append}({var})
        }}, 500);\n
            """
        return s

    def css(self):
        if not self._css:
            return ''
        _content = '\n'.join(self._css)
        _var = self.new_var()
        return self._append_not_once(f"""
var {_var} = document.createElement('style');
{_var}.type = 'text/css';
{_var}.innerHTML = {self.new_str(_content)}
{self._html_append}({_var})
        """, _var)

    def html(self):
        if not self._html:
            return ''
        _content = '\n'.join(self._html)
        _var = self.new_var()
        return self._append_not_once(f"""
var {_var} = document.createElement('div');
{_var}.innerHTML = {self.new_str(_content)}
{self._html_append}({_var})
        """, _var)

    def js(self):
        return '\n'.join(self._js)

    def result(self):
        return '\n'.join([self.css(), self.html(), self.js()])


class WindowWebLoader(WebLoader):
    replaced_with = 'window'
