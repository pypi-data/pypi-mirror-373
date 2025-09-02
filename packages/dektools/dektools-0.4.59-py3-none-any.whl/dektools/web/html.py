import sys

str_html_ignore_begin = {' ', '\n', '\r', '\t'}
str_html_marker = '<!DOCTYPE '

bytes_html_ignore_begin = {x.encode('utf-8') for x in str_html_ignore_begin}
bytes_html_marker = str_html_marker.encode('utf-8')


def is_html(s):
    if isinstance(s, bytes):
        html_ignore_begin = bytes_html_ignore_begin
        html_marker = bytes_html_marker
        ss = (x.to_bytes(1, sys.byteorder) for x in s)
    else:
        html_ignore_begin = str_html_ignore_begin
        html_marker = str_html_marker
        ss = s
    begin = None
    for i, x in enumerate(ss):
        if x not in html_ignore_begin:
            begin = i
            break
    if begin is not None:
        return s[begin:begin + len(html_marker)] == html_marker
    return False


_redirect_html_format = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta content="always" name="referrer">
    <script>
    var timeout = 0;
    ;setTimeout(function () {
        window.location.replace("%s")
    }, timeout);
    window.opener = null;</script>
    <noscript>
        <META http-equiv="refresh" content="0;URL='%s'">
    </noscript>
""".replace('\n', '')


def get_redirect_html(url):
    return _redirect_html_format % (url, url)
