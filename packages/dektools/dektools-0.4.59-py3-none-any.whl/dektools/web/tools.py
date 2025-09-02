from .mimetypes import mimetypes
from .headers import get_content_type_key


def get_ct_ext(ct):
    ext = ''
    if ct:
        ext = mimetypes.guess_extension(get_content_type_key(ct)) or ext
    return ext
