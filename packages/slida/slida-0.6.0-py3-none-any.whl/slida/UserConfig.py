import argparse
import warnings
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    NotRequired,
    Sequence,
    TypedDict,
    TypeVar,
)

import platformdirs
import yaml
from klaatu_python.utils import nonulls

from slida.DirScanner import FileOrder
from slida.utils import first_not_null, first_not_null_or_null


_T = TypeVar("_T")


class TransitionConfig(TypedDict):
    exclude: NotRequired[list[str]]
    include: NotRequired[list[str]]


class UserConfigField(Generic[_T]):
    factory: Callable[[Any], _T] | None = None
    _type: type[_T] | None = None
    _default: _T

    def __init__(
        self,
        default: _T | Callable[[], _T],
        value: _T | None = None,
        help: str | None = None,
        short_name: str | None = None,
        extend_argparse: bool = True,
        choices: Iterable[_T] | None = None,
    ):
        if isinstance(default, Callable):
            self._default = default()
        else:
            self._default = default
        self._explicit_value = value
        self._help = help
        self._short_name = short_name
        self._extend_argparse = extend_argparse
        self._choices = choices

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.copy(value=other.explicit_value)
        return NotImplemented

    def __repr__(self):
        return str(self.value)

    @property
    def default(self) -> _T:
        return self._default

    @property
    def explicit_value(self) -> _T | None:
        return self._explicit_value

    @property
    def value(self) -> _T:
        return self._explicit_value if self._explicit_value is not None else self._default

    @value.setter
    def value(self, v: Any):
        if self.factory:
            self._explicit_value = self.factory(v)
        else:
            self._explicit_value = v

    def copy(
        self,
        default: _T | Callable[[], _T] | None = None,
        value: _T | None = None,
        help: str | None = None,
        short_name: str | None = None,
        extend_argparse: bool | None = None,
    ):
        return self.__class__(
            default=first_not_null(default, self._default),
            value=first_not_null_or_null(value, self._explicit_value),
            help=first_not_null_or_null(help, self._help),
            short_name=first_not_null_or_null(short_name, self._short_name),
            extend_argparse=first_not_null(extend_argparse, self._extend_argparse),
        )

    def extend_argument_parser(self, parser: argparse.ArgumentParser, name: str):
        if self._extend_argparse:
            hyphenated_name = name.replace("_", "-")
            parser.add_argument(
                *nonulls([f"--{hyphenated_name}", f"-{self._short_name}" if self._short_name else None]),
                help=(self._help + f" (default: {self.value})") if self._help else f"Default: {self.value}",
                choices=self._choices,
            )


class BooleanConfigField(UserConfigField[bool]):
    factory = bool

    def extend_argument_parser(self, parser: argparse.ArgumentParser, name: str):
        if self._extend_argparse:
            hyphenated_name = name.replace("_", "-")
            mutex = parser.add_mutually_exclusive_group()
            mutex.add_argument(
                *nonulls([f"--{hyphenated_name}", f"-{self._short_name}" if self._short_name else None]),
                action="store_const",
                const=True,
                help=(self._help + (" (default)" if self.value else "")) if self._help else None,
            )
            mutex.add_argument(
                f"--no-{hyphenated_name}",
                action="store_const",
                const=False,
                dest=name,
                help=f"Negates --{hyphenated_name}" + (" (default)" if not self.value else ""),
            )


class TransitionConfigField(UserConfigField[TransitionConfig | dict]):
    def extend_argument_parser(self, parser: argparse.ArgumentParser, name: str):
        if self._extend_argparse:
            parser.add_argument(
                "--transition",
                "-t",
                dest="transitions",
                action="append",
                help="Transitions to use. Repeat the argument for multiple transitions. Default: use them all",
            )
            parser.add_argument(
                "--exclude-transition",
                "-et",
                dest="exclude_transitions",
                action="append",
                help="Transition NOT to use. Repeat the argument for multiple transitions",
            )


class IntConfigField(UserConfigField[int]):
    factory = int


class FloatConfigField(UserConfigField[float]):
    factory = float


class UserConfig:
    source: str | None

    interval = IntConfigField(20, help="Auto-advance interval, in seconds", short_name="i")
    order = UserConfigField(FileOrder.RANDOM, short_name="o", choices=FileOrder)
    transition_duration = FloatConfigField(0.3, short_name="td", help="In seconds; 0 = no transitions")
    transitions = TransitionConfigField(dict)
    auto = BooleanConfigField(True, help="Enable auto-advance")
    debug = BooleanConfigField(False, help="Output various debug stuff to console")
    hidden = BooleanConfigField(False, help="Include hidden files and directories")
    recursive = BooleanConfigField(False, help="Iterate through subdirectories", short_name="R")
    reverse = BooleanConfigField(False, help="Reverse the image order", short_name="r")
    symlinks = BooleanConfigField(True, help="Follow symlinks")
    tiling = BooleanConfigField(True, help="Tile images horizontally")

    def __init__(self, source: str | None = None):
        self.source = source
        for fieldname, field in self.get_fields().items():
            setattr(self, fieldname, field.copy())

    def __repr__(self):
        return self.repr()

    def repr(self, indent: int = 0, prefix: str = ""):
        if len(prefix) < indent:
            prefix = f"{prefix:{indent}s}"
        changed = {k.replace("_", "-"): v for k, v in self.get_fields().items() if v.explicit_value is not None}
        result = [f"{prefix}{self.__class__.__name__}(" + (self.source or "") + ")"]
        for k, v in changed.items():
            result.append((" " * indent) + f"  {k}: {v}")
        return "\n".join(result)

    def check(self):
        if self.interval.value < 1:
            raise ValueError("Minimum interval is 1 s.")
        if self.interval.value < self.transition_duration.value:
            raise ValueError("Interval cannot be less than transition duration.")

    def correct_invalid(self):
        if self.interval.value < self.transition_duration.value:
            self.interval.value = self.interval.default
            self.transition_duration.value = self.transition_duration.default
        if self.interval.value < 1:
            self.interval.value = self.interval.default

    def extend_argument_parser(self, parser: argparse.ArgumentParser):
        for field_name, field in self.get_fields().items():
            field.extend_argument_parser(parser, field_name)

    def get_fields(self) -> dict[str, UserConfigField]:
        fields = {}
        for attrname in dir(self):
            attr = getattr(self, attrname)
            if isinstance(attr, UserConfigField):
                fields[attrname] = attr
        return fields

    @classmethod
    def from_cli_args(cls, args: argparse.Namespace):
        config_dict = {}
        cli_dict = {k.replace("_", "-"): v for k, v in args.__dict__.items() if v is not None}

        if "transitions" in cli_dict:
            config_dict["transitions"] = {"include": cli_dict["transitions"]}
            del cli_dict["transitions"]

        if "exclude-transitions" in cli_dict:
            config_dict["transitions"] = config_dict.get("transitions", {})
            config_dict["transitions"]["exclude"] = cli_dict["exclude-transitions"]
            del cli_dict["exclude-transitions"]

        config_dict.update(cli_dict)
        return cls.from_dict(config_dict, "CLI")

    @classmethod
    def from_dict(cls, d: dict, source: str | None = None):
        config = cls(source=source)

        for field_name, field in config.get_fields().items():
            arg_name = field_name.replace("_", "-")
            if arg_name in d:
                field.value = d[arg_name]
            elif isinstance(field, BooleanConfigField):
                no_arg_name = "no-" + arg_name
                if no_arg_name in d:
                    field.value = not d[no_arg_name]

        return config

    @classmethod
    def from_file(cls, path: Path):
        with path.open("rt", encoding="utf8") as f:
            config_dict: dict = yaml.safe_load(f)
            return cls.from_dict(config_dict, str(path))


class DefaultUserConfig(UserConfig):
    def __init__(self, source: str | None = None):
        super().__init__(source)
        for field in self.get_fields().values():
            field.value = field.default


class CombinedUserConfig(UserConfig):
    subconfigs: Sequence["UserConfig"]

    def __init__(self, source: str | None = None):
        super().__init__(source)
        self.subconfigs = []

    def __repr__(self):
        result = self.repr()
        for index, sub in enumerate(self.subconfigs):
            result += "\n" + sub.repr(indent=2, prefix="=" if index == 0 else "+")
        return result

    def update(self, other: "UserConfig"):
        # RHS (other) takes precedence
        self_fields = self.get_fields()
        other_fields = other.get_fields()
        for fieldname, field in self_fields.items():
            setattr(self, fieldname, field + other_fields[fieldname])
        self.subconfigs = list(self.subconfigs) + [other]

    @classmethod
    def read(cls, cli_args: argparse.Namespace | None = None, custom_dirs: list[Path] | None = None):
        config = cls("FINAL")
        paths: list[Path] = [
            platformdirs.user_config_path("slida") / "slida.yaml",
            Path("slida.yaml"),
        ]

        config.update(DefaultUserConfig())

        for custom_dir in custom_dirs or []:
            paths.append(custom_dir / "slida.yaml")

        for path in paths:
            if path.is_file():
                try:
                    config.update(UserConfig.from_file(path))
                except Exception as e:
                    warnings.warn(f"Could not read YAML from {path}: {e}")

        if cli_args:
            config.update(UserConfig.from_cli_args(cli_args))

        return config
