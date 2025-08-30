import dataclasses
import enum
import mimetypes
import os
from typing import TYPE_CHECKING, Generator


if TYPE_CHECKING:
    from slida.UserConfig import UserConfig


class FileOrder(enum.StrEnum):
    NAME = "name"
    CREATED = "created"
    MODIFIED = "modified"
    RANDOM = "random"


@dataclasses.dataclass
class File:
    path: str
    stat: dataclasses.InitVar[os.stat_result]
    ctime: float = dataclasses.field(init=False)
    mtime: float = dataclasses.field(init=False)
    ino: int = dataclasses.field(init=False)
    is_valid: bool | None = dataclasses.field(init=False, default=None)

    def __post_init__(self, stat: os.stat_result):
        self.ctime = stat.st_ctime
        self.mtime = stat.st_mtime
        self.ino = stat.st_ino


class DirScanner:
    is_finished: bool = False

    def __init__(self, root_paths: str | list[str], config: "UserConfig | None" = None):
        from slida.UserConfig import UserConfig

        self.root_paths = root_paths if isinstance(root_paths, list) else [root_paths]
        self.config = config or UserConfig()
        self.visited_inodes: list[int] = []

    def scandir(self) -> "Generator[File]":
        for path in self.root_paths:
            yield from self.__scandir(path, is_root=True)
        self.is_finished = True

    def __inode(self, entry: os.DirEntry | str):
        if isinstance(entry, os.DirEntry):
            return entry.inode() if not self.__is_symlink(entry) else os.stat(entry.path).st_ino
        return os.stat(entry).st_ino

    def __is_dir(self, entry: os.DirEntry | str):
        return entry.is_dir() if isinstance(entry, os.DirEntry) else os.path.isdir(entry)

    def __is_file(self, entry: os.DirEntry | str):
        return entry.is_file() if isinstance(entry, os.DirEntry) else os.path.isfile(entry)

    def __is_symlink(self, entry: os.DirEntry | str):
        return entry.is_symlink() if isinstance(entry, os.DirEntry) else os.path.islink(entry)

    def __name(self, entry: os.DirEntry | str) -> str:
        return entry.name if isinstance(entry, os.DirEntry) else entry.split("/")[-1]

    def __path(self, entry: os.DirEntry | str) -> str:
        return entry.path if isinstance(entry, os.DirEntry) else entry

    def __scandir(self, entry: os.DirEntry | str, is_root: bool = False) -> "Generator[File]":
        if not is_root:
            if not self.config.hidden.value and self.__name(entry).startswith("."):
                return
            if not self.config.symlinks.value and self.__is_symlink(entry):
                return

        if self.__is_dir(entry):
            if is_root or self.config.recursive.value:
                inode = self.__inode(entry)
                if inode not in self.visited_inodes:
                    self.visited_inodes.append(inode)
                    with os.scandir(entry) as dir:
                        for subentry in dir:
                            yield from self.__scandir(subentry)

        elif self.__is_file(entry):
            mimetype = mimetypes.guess_file_type(self.__path(entry))
            if mimetype[0] is not None and mimetype[0].startswith("image/"):
                inode = self.__inode(entry)
                if inode not in self.visited_inodes:
                    self.visited_inodes.append(inode)
                    yield File(path=self.__path(entry), stat=self.__stat(entry))

    def __stat(self, entry: os.DirEntry | str) -> os.stat_result:
        return entry.stat() if isinstance(entry, os.DirEntry) else os.stat(entry)
