import argparse
import warnings
from pathlib import Path
from typing import Sequence

import platformdirs

from slida.config.base import Config


class CombinedConfig(Config):
    subconfigs: Sequence["Config"]

    def __init__(self, source: str | None = None):
        super().__init__(source)
        self.subconfigs = []

    def __repr__(self):
        result = self.repr()
        for index, sub in enumerate(self.subconfigs):
            result += "\n" + sub.repr(indent=2, prefix="=" if index == 0 else "+")
        return result

    def update(self, other: "Config"):
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

        config.update(Config.default())

        for custom_dir in custom_dirs or []:
            paths.append(custom_dir / "slida.yaml")

        for path in paths:
            if path.is_file():
                try:
                    config.update(Config.from_file(path))
                except Exception as e:
                    warnings.warn(f"Could not read YAML from {path}: {e}")

        if cli_args:
            config.update(Config.from_cli_args(cli_args))

        return config
