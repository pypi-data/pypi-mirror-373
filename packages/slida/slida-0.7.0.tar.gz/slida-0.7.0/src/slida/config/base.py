import argparse
from pathlib import Path

import yaml

from slida.config.fields import (
    BaseConfigField,
    BooleanConfigField,
    FileOrderConfigField,
    FloatConfigField,
    IntConfigField,
    TransitionConfigField,
)
from slida.files.file_order import FileOrder


class Config:
    __current: "Config | None" = None
    source: str | None

    background = BaseConfigField("black", help="For valid values, see: https://doc.qt.io/qt-6/qcolor.html#fromString")
    interval = IntConfigField(20, help="Auto-advance interval, in seconds", short_name="i")
    max_file_size = IntConfigField(20_000_000, help="Maximum file size (set to 0 to disable)")
    order = FileOrderConfigField(FileOrder.RANDOM, short_name="o")
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

    def get_fields(self) -> dict[str, BaseConfigField]:
        fields = {}
        for attrname in dir(self):
            attr = getattr(self, attrname)
            if isinstance(attr, BaseConfigField):
                fields[attrname] = attr
        return fields

    @classmethod
    def current(cls) -> "Config":
        if Config.__current is None:
            Config.__current = Config()
        return Config.__current

    @classmethod
    def default(cls) -> "Config":
        config = Config("DEFAULT")
        for field in config.get_fields().values():
            field.value = field.default
        return config

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

    @classmethod
    def set_current(cls, value: "Config"):
        cls.__current = value
