import argparse
import locale
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    NotRequired,
    TypedDict,
    TypeVar,
)

from klaatu_python.utils import nonulls

from slida.files.file_order import FileOrder
from slida.utils import first_not_null, first_not_null_or_null


_T = TypeVar("_T")


class TransitionConfig(TypedDict):
    exclude: NotRequired[list[str]]
    include: NotRequired[list[str]]


class BaseConfigField(Generic[_T]):
    default: _T

    choices: Iterable[_T] | None = None
    explicit_value: _T | None = None
    extend_argparse: bool = True
    factory: Callable[[Any], _T] | None = None
    help: str | None = None
    short_name: str | None = None

    def __init__(
        self,
        default: _T | Callable[[], _T],
        value: _T | None = None,
        help: str | None = None,
        short_name: str | None = None,
        extend_argparse: bool | None = None,
        choices: Iterable[_T] | None = None,
    ):
        if isinstance(default, Callable):
            self.default = default()
        else:
            self.default = default
        if value is not None:
            self.explicit_value = value
        if help is not None:
            self.help = help
        if short_name is not None:
            self.short_name = short_name
        if extend_argparse is not None:
            self.extend_argparse = extend_argparse
        if choices is not None:
            self.choices = choices

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.copy(value=other.explicit_value)
        return NotImplemented

    def __repr__(self):
        return str(self.value)

    @property
    def value(self) -> _T:
        return self.explicit_value if self.explicit_value is not None else self.default

    @value.setter
    def value(self, v: Any):
        if self.factory:
            self.explicit_value = self.factory(v)
        else:
            self.explicit_value = v

    @property
    def value_as_string(self) -> str:
        return str(self.value)

    def copy(
        self,
        default: _T | Callable[[], _T] | None = None,
        value: _T | None = None,
        help: str | None = None,
        short_name: str | None = None,
        extend_argparse: bool | None = None,
    ):
        return self.__class__(
            default=first_not_null(default, self.default),
            value=first_not_null_or_null(value, self.explicit_value),
            help=first_not_null_or_null(help, self.help),
            short_name=first_not_null_or_null(short_name, self.short_name),
            extend_argparse=first_not_null(extend_argparse, self.extend_argparse),
        )

    def extend_argument_parser(self, parser: argparse.ArgumentParser, name: str):
        if self.extend_argparse:
            hyphenated_name = name.replace("_", "-")
            parser.add_argument(
                *nonulls([f"--{hyphenated_name}", f"-{self.short_name}" if self.short_name else None]),
                help=(
                    (self.help + f" (default: {self.value_as_string})") if self.help
                    else f"Default: {self.value_as_string}"
                ),
                choices=self.choices,
            )


class BooleanConfigField(BaseConfigField[bool]):
    factory = bool

    def extend_argument_parser(self, parser: argparse.ArgumentParser, name: str):
        if self.extend_argparse:
            hyphenated_name = name.replace("_", "-")
            mutex = parser.add_mutually_exclusive_group()
            mutex.add_argument(
                *nonulls([f"--{hyphenated_name}", f"-{self.short_name}" if self.short_name else None]),
                action="store_const",
                const=True,
                help=(self.help + (" (default)" if self.value else "")) if self.help else None,
            )
            mutex.add_argument(
                f"--no-{hyphenated_name}",
                action="store_const",
                const=False,
                dest=name,
                help=f"Negates --{hyphenated_name}" + (" (default)" if not self.value else ""),
            )


class TransitionConfigField(BaseConfigField[TransitionConfig | dict]):
    def extend_argument_parser(self, parser: argparse.ArgumentParser, name: str):
        if self.extend_argparse:
            parser.add_argument(
                "--transition",
                "-t",
                dest="transitions",
                action="append",
                help="Transition to use. Repeat the argument for multiple transitions. Default: use them all",
            )
            parser.add_argument(
                "--exclude-transition",
                "-et",
                dest="exclude_transitions",
                action="append",
                help="Transition NOT to use. Repeat the argument for multiple transitions",
            )


class IntConfigField(BaseConfigField[int]):
    factory = int

    @property
    def value_as_string(self) -> str:
        return locale.format_string("%d", self.value, grouping=True)


class FloatConfigField(BaseConfigField[float]):
    factory = float


class FileOrderConfigField(BaseConfigField[FileOrder]):
    factory = FileOrder
    choices = FileOrder
