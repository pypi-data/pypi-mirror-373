import typer
from typer.models import ArgumentInfo, OptionInfo

default_argument = typer.Argument().__dict__.copy()
default_option = typer.Option().__dict__.copy()


class ReprArgumentInfo(ArgumentInfo):
    def __repr__(self):
        kwargs = []
        for k, v in self.__dict__.items():
            if v != default_argument[k]:
                kwargs.append(f"{k}={repr(v)}")
        return f"typer.Argument({', '.join(kwargs)})"


class ReprOptionInfo(OptionInfo):
    def __repr__(self):
        kwargs = []
        for k, v in self.__dict__.items():
            if v != default_option[k]:
                kwargs.append(f"{k}={repr(v)}")
        return f"typer.Option({', '.join(kwargs)})"


def Argument(*args, **kwargs):  # noqa
    return ReprArgumentInfo(**typer.Argument(*args, **kwargs).__dict__.copy())


def Option(*args, **kwargs):  # noqa
    return ReprOptionInfo(**typer.Option(*args, **kwargs).__dict__.copy())
