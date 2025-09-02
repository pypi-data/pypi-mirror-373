from dektools.str import Fragment
from dektools.file import read_text


def find_dyna_prefix_from_str(context):
    try:
        frag = Fragment(context, 'ENVVAR_PREFIX_FOR_DYNACONF', ',', sep=True)
    except IndexError:
        return None
    return frag[2].strip('="\' ')


def find_dyna_prefix(filepath):
    return find_dyna_prefix_from_str(read_text(filepath))
