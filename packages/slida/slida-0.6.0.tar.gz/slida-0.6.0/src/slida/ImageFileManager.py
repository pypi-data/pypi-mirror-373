import itertools
import random
from typing import TYPE_CHECKING

from PySide6.QtCore import QSizeF

from slida.DirScanner import DirScanner, FileOrder
from slida.ImageFile import ImageFile
from slida.ImageScreen import ImageScreen
from slida.UserConfig import DefaultUserConfig
from slida.utils import NoImagesFound


if TYPE_CHECKING:
    from slida.UserConfig import UserConfig


class ImageFileManager:
    __config: "UserConfig"
    __dir_scanner: DirScanner
    __image_files: list[ImageFile]
    __screen_file_indices: list[list[int]]

    def __init__(self, path: str | list[str], config: "UserConfig | None" = None):
        self.__config = config or DefaultUserConfig()
        self.__screen_file_indices = []
        self.set_path(path)

    def get_image_screen(self, screen_idx: int, bounds: QSizeF):
        image_screen = ImageScreen(bounds)

        for file_idx, image in self.iter_image_files(screen_idx):
            new_image_screen = ImageScreen(bounds, *image_screen.images, image)
            if new_image_screen.area > image_screen.area:
                image_screen = new_image_screen
                self.__screen_file_indices[screen_idx].append(file_idx)
            if not image_screen.can_fit_more:
                break

        if not image_screen.images:
            raise NoImagesFound()

        return image_screen

    def iter_image_files(self, screen_idx: int):
        self.__align_screen_file_indices(screen_idx + 1)
        self.__screen_file_indices[screen_idx] = []
        used_indices = self.__get_used_file_indices(screen_idx)

        for file_idx in range(len(self.__image_files)):
            if file_idx not in used_indices and self.__image_files[file_idx].is_valid:
                yield file_idx, self.__image_files[file_idx]

    def set_path(self, path: str | list[str]):
        image_files: list[ImageFile] = []
        self.__dir_scanner = DirScanner(path, config=self.__config)
        reverse = self.__config.reverse.value

        for file_batch in itertools.batched(self.__dir_scanner.scandir(), n=1000):
            image_files.extend(ImageFile(file) for file in file_batch)
            print(f"Indexed {len(image_files)} files ...")

        if self.__config.order.value == FileOrder.NAME:
            self.__image_files = sorted(image_files, key=lambda e: e.file.path.lower(), reverse=reverse)
        if self.__config.order.value == FileOrder.CREATED:
            self.__image_files = sorted(image_files, key=lambda e: e.file.ctime, reverse=reverse)
        if self.__config.order.value == FileOrder.MODIFIED:
            self.__image_files = sorted(image_files, key=lambda e: e.file.mtime, reverse=reverse)
        if self.__config.order.value == FileOrder.RANDOM:
            random.shuffle(image_files)
            self.__image_files = image_files

    def __align_screen_file_indices(self, new_length: int):
        self.__screen_file_indices = self.__screen_file_indices[:new_length]
        while len(self.__screen_file_indices) < new_length:
            self.__screen_file_indices.append([])

    def __get_used_file_indices(self, last_screen_idx: int) -> list[int]:
        return list(itertools.chain(*self.__screen_file_indices[:last_screen_idx]))
