import mimetypes
import os
from typing import Generator

from slida.config import Config
from slida.files.image_file import ImageFile


class DirScanner:
    is_finished: bool = False

    def __init__(self, root_paths: str | list[str]):
        self.root_paths = root_paths if isinstance(root_paths, list) else [root_paths]
        self.visited_inodes: list[int] = []

    def scandir(self, max_size: int = 0) -> "Generator[ImageFile]":
        for path in self.root_paths:
            yield from self.__scandir(path, is_root=True, max_size=max_size)
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

    def __scandir(self, entry: os.DirEntry | str, is_root: bool = False, max_size: int = 0) -> "Generator[ImageFile]":
        config = Config.current()

        if not is_root:
            if not config.hidden.value and self.__name(entry).startswith("."):
                return
            if not config.symlinks.value and self.__is_symlink(entry):
                return

        if self.__is_dir(entry):
            if is_root or config.recursive.value:
                inode = self.__inode(entry)
                if inode not in self.visited_inodes:
                    self.visited_inodes.append(inode)
                    with os.scandir(entry) as dir:
                        for subentry in dir:
                            yield from self.__scandir(subentry, max_size=max_size)

        elif self.__is_file(entry):
            mimetype = mimetypes.guess_file_type(self.__path(entry))
            if mimetype[0] is not None and mimetype[0].startswith("image/"):
                inode = self.__inode(entry)
                if inode not in self.visited_inodes:
                    stat = self.__stat(entry)
                    self.visited_inodes.append(inode)
                    if max_size == 0 or stat.st_size <= max_size:
                        yield ImageFile(path=self.__path(entry), stat=stat)

    def __stat(self, entry: os.DirEntry | str) -> os.stat_result:
        return entry.stat() if isinstance(entry, os.DirEntry) else os.stat(entry)
