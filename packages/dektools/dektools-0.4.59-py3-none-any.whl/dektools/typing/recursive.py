import typing

if typing.TYPE_CHECKING:
    from argparse import Action


def func(arg: 'Action'):
    print(arg.default)
