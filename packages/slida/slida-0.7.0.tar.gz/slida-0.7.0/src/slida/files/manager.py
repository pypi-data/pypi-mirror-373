import dataclasses
import itertools
import random

from PySide6.QtCore import QSizeF

from slida.config import Config
from slida.files.dir_scanner import DirScanner
from slida.files.file_order import FileOrder
from slida.files.image_file import ImageFile
from slida.qt.image_screen import ImageScreen
from slida.utils import NoImagesFound


@dataclasses.dataclass
class Screen:
    iteration: int
    file_indices: list[int] = dataclasses.field(default_factory=list)


class ImageFileManager:
    __dir_scanner: DirScanner
    __image_files: list[ImageFile]
    __screens: list[Screen]

    def __init__(self, path: str | list[str]):
        self.__screens = []
        self.set_path(path)

    def get_image_screen(self, screen_idx: int, bounds: QSizeF):
        image_screen = ImageScreen(bounds)

        for file_idx, image in self.iter_image_files(screen_idx):
            new_image_screen = ImageScreen(bounds, *image_screen.images, image)
            if new_image_screen.area > image_screen.area:
                image_screen = new_image_screen
                self.__screens[screen_idx].file_indices.append(file_idx)
            if not image_screen.can_fit_more:
                break

        if not image_screen.images:
            raise NoImagesFound()

        return image_screen

    def iter_image_files(self, screen_idx: int):
        self.__align_screen_file_indices(screen_idx + 1)
        iteration = self.__get_iteration(screen_idx)
        self.__screens[screen_idx] = Screen(iteration)

        for iteration in (iteration, iteration + 1):
            self.__screens[screen_idx].iteration = iteration
            used_indices = self.__get_iteration_used_file_indices(iteration, screen_idx)

            for file_idx in range(len(self.__image_files)):
                if file_idx not in used_indices and self.__image_files[file_idx].is_valid:
                    yield file_idx, self.__image_files[file_idx]

    def set_path(self, path: str | list[str]):
        image_files: list[ImageFile] = []
        self.__dir_scanner = DirScanner(path)
        config = Config.current()
        reverse = config.reverse.value
        file_order = config.order.value
        max_file_size = config.max_file_size.value

        for file_batch in itertools.batched(self.__dir_scanner.scandir(max_size=max_file_size), n=1000):
            image_files.extend(file_batch)
            print(f"Indexed {len(image_files)} files ...")

        if file_order == FileOrder.NAME:
            self.__image_files = sorted(image_files, key=lambda f: f.path.lower(), reverse=reverse)
        if file_order == FileOrder.CREATED:
            self.__image_files = sorted(image_files, key=lambda f: f.stat.st_ctime, reverse=reverse)
        if file_order == FileOrder.MODIFIED:
            self.__image_files = sorted(image_files, key=lambda f: f.stat.st_mtime, reverse=reverse)
        if file_order == FileOrder.RANDOM:
            random.shuffle(image_files)
            self.__image_files = image_files
        if file_order == FileOrder.SIZE:
            self.__image_files = sorted(image_files, key=lambda f: f.stat.st_size, reverse=reverse)

    def __align_screen_file_indices(self, new_length: int):
        self.__screens = self.__screens[:new_length]
        iteration = self.__get_iteration()
        while len(self.__screens) < new_length:
            self.__screens.append(Screen(iteration))

    def __get_iteration(self, last_screen_idx: int | None = None) -> int:
        screens = self.__screens[:last_screen_idx] if last_screen_idx is not None else self.__screens
        return screens[-1].iteration if screens else 0

    def __get_iteration_used_file_indices(self, iteration: int, last_screen_idx: int) -> list[int]:
        file_indices = [s.file_indices for s in self.__screens[:last_screen_idx] if s.iteration == iteration]
        return list(itertools.chain(*file_indices))
