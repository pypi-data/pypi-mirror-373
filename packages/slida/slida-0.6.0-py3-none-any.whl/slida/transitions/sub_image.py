import math
from abc import abstractmethod
from math import ceil, floor

import numpy as np
from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QObject,
    QRect,
    QRectF,
    QSequentialAnimationGroup,
    QSize,
)
from PySide6.QtGui import QImage, QPainter, QPixmap, qRgba

from slida.debug import add_live_object, remove_live_object
from slida.transitions.base import Transition
from slida.utils import get_subsquare_count


class SubImage(QObject):
    column: int
    filled: bool = False
    row: int

    def __init__(self, parent: QObject, row: int, column: int, filled: bool = False):
        super().__init__(parent)
        self.row = row
        self.column = column
        self.filled = filled
        add_live_object(id(self), self.__class__.__name__)

    def deleteLater(self):
        remove_live_object(id(self))
        super().deleteLater()

    def toggle_filled(self):
        self.filled = not self.filled


class SubImageTransition(Transition):
    __subs: list[list[SubImage]] | None = None
    columns: int = 0
    parent_z = 1.0
    rows: int = 0
    min_sub_width: int = 50

    def deleteLater(self):
        for subsubs in self.__subs or []:
            for sub in subsubs:
                sub.deleteLater()
        super().deleteLater()

    @abstractmethod
    def fill_subs(self, size: QSize, progress: float):
        ...

    def get_filled_subs(self, size: QSize) -> list[SubImage]:
        return [s for s in self.get_subs_flattened(size) if s.filled]

    def get_sub_geometry(self, size: QSize, sub: SubImage, offset: int = 0) -> QRect:
        column = (sub.column + offset) % self.columns
        row = sub.row + math.floor((sub.column + offset) / self.columns)
        sub_width = size.width() / self.columns
        sub_height = size.height() / self.rows
        return QRect(floor(column * sub_width), floor(row * sub_height), ceil(sub_width), ceil(sub_height))

    def get_subs(self, size: QSize) -> list[list[SubImage]]:
        if self.__subs is None:
            if size.width() > 0:
                self.__subs = []
                self.rows, self.columns = get_subsquare_count(size, self.min_sub_width)

                for y in range(self.rows):
                    y_subs: list[SubImage] = []
                    for x in range(self.columns):
                        y_subs.append(SubImage(parent=self, row=y, column=x))
                    self.__subs.append(y_subs)

        return self.__subs or []

    def get_subs_flattened(self, size: QSize) -> list[SubImage]:
        subs = self.get_subs(size)
        return [s for subsubs in subs for s in subsubs]

    def on_progress(self, value: float):
        super().on_progress(value)
        if self.__diff():
            self.parent().update(self.parent().rect())

    def paint(self, painter: QPainter, image: QImage, image_rect: QRectF):
        self.fill_subs(image.size(), self._progress)
        for sub in self.get_filled_subs(image.size()):
            geometry = self.get_sub_geometry(image.size(), sub)
            painter.drawImage(geometry, image.copy(geometry))

    def __diff(self) -> int:
        if self.__subs:
            filled_before = len([s for subsubs in self.__subs for s in subsubs if s.filled])
            filled_after = round(self.rows * self.columns * self._progress)
            return filled_after - filled_before
        return 0


class RandomSubImageTransition(SubImageTransition):
    def fill_subs(self, size: QSize, progress: float):
        subs = self.get_subs_flattened(size)

        if progress in (0.0, 1.0):
            for sub in subs:
                sub.filled = bool(progress)
        else:
            filled_subs = [s for s in subs if s.filled]
            filled_before = len(filled_subs)
            filled_after = round(len(subs) * progress)
            diff = filled_after - filled_before

            if diff != 0:
                unfilled_subs = [s for s in subs if not s.filled]
                weights = None
                probabilities = None
                subs = unfilled_subs if diff > 0 else filled_subs
                weights = np.array([self.get_sub_image_weight(s) for s in subs])
                if diff < 0:
                    weights = 1 / weights
                weight_sum = weights.sum()
                probabilities = weights / weight_sum

                try:
                    for index in np.random.choice(range(len(subs)), size=abs(diff), replace=False, p=probabilities):
                        subs[index].toggle_filled()
                except Exception as e:
                    print(e)
                    print(probabilities)

    def get_sub_image_weight(self, s: SubImage) -> float:
        return 1.0


class RandomSquaresIn(RandomSubImageTransition):
    easing = QEasingCurve.Type.InCubic


class TopLeftSquaresIn(RandomSubImageTransition):
    def get_sub_image_weight(self, s: SubImage) -> float:
        return pow(2, (self.rows + self.columns - s.row - s.column - 2) / (self.rows + self.columns - 2) * 50)


class TopSquaresIn(RandomSubImageTransition):
    def get_sub_image_weight(self, s: SubImage) -> float:
        return pow(2, (self.rows - s.row - 1) / (self.rows - 1) * 50)


class Fucker(SubImageTransition):
    def create_animation(self, duration: int) -> QAbstractAnimation:
        group = QSequentialAnimationGroup(self)
        taken = np.zeros((10, 8), dtype=np.int_)
        valid_targets = np.append(taken, np.ones((1, 8), dtype=np.int_), axis=0)
        valid_targets = np.roll(valid_targets, -1, 0)[:10, :]
        return super().create_animation(duration)


class SnakeTransition(Transition):
    """
    These are probably not useful since they just look chaotic except at low
    speeds. But the algorithms may come in handy somehow.
    """
    min_sub_width: int = 50
    __columns: int | None = None
    __rows: int | None = None
    __offset: int | None = None
    __last_offset: int | None = None

    def get_sub_filled(self, rows: int, columns: int, offset: int):
        sub_filled = np.zeros(rows * columns, dtype=np.int_)
        sub_filled[offset:] = 1
        sub_filled = sub_filled.reshape((rows, columns))
        sub_filled[1::2] = sub_filled[1::2][:, ::-1]
        return sub_filled.flatten()

    def get_sub_mirrored(self, rows: int, columns: int, offset: int):
        row_arr = np.array([[row] * columns for row in range(rows)])
        row_arr_rolled = np.roll(row_arr.flatten(), offset, 0).reshape(row_arr.shape)
        row_arr_rolled[1::2] = row_arr_rolled[1::2][:, ::-1]
        row_diffs = row_arr - row_arr_rolled
        sub_mirrored = row_diffs % 2
        return sub_mirrored.flatten()

    def get_sub_image_map(self, rows: int, columns: int, offset: int):
        """
        Array of [a, b, c, d] arrays where:
            a = subimage index in painter
            b = subimage index in image
            c = whether subimage should be filled
            d = whether subimage should be mirrored
        """
        sub_image_map = np.arange(rows * columns, dtype=np.int_).reshape((rows, columns)) # 2-d matrix
        sub_image_map[1::2] = sub_image_map[1::2][:, ::-1] # reverse odd rows
        sub_image_map = np.roll(sub_image_map.flatten(), offset, 0).reshape(sub_image_map.shape)
        sub_image_map[1::2] = sub_image_map[1::2][:, ::-1] # reverse odd rows back

        painter_indices = np.arange(rows * columns, dtype=np.int_)
        sub_filled = self.get_sub_filled(rows, columns, offset)
        sub_mirrored = self.get_sub_mirrored(rows, columns, offset)

        return np.stack((painter_indices, sub_image_map.flatten(), sub_filled, sub_mirrored), axis=1)

    def index_to_geometry(self, rows: int, columns: int, index: int, sub_width: float, sub_height: float):
        row, col = np.unravel_index(index, (rows, columns))
        return QRectF(col * sub_width, row * sub_height, sub_width, sub_height)

    def on_progress(self, value: float):
        super().on_progress(value)
        if self.__columns and self.__rows:
            self.__offset = self.progress_to_offset(value, self.__rows, self.__columns)
        if self.__offset is None or self.__offset != self.__last_offset:
            self.__last_offset = self.__offset
            self.parent().update(self.parent().rect())

    def paint(self, painter: QPainter, image: QImage, image_rect: QRectF):
        size = image_rect.size()
        rows, columns = get_subsquare_count(size, self.min_sub_width)
        self.__rows, self.__columns = rows, columns
        offset = self.progress_to_offset(self._progress, rows, columns)
        sub_image_map = self.get_sub_image_map(rows, columns, offset)
        sub_width = size.width() / columns
        sub_height = size.height() / rows

        for painter_idx, image_idx, filled, mirrored in sub_image_map:
            if filled:
                translate_by = image_rect.topLeft()
                painter_geo = self.index_to_geometry(rows, columns, painter_idx, sub_width, sub_height).translated(translate_by)
                image_geo = self.index_to_geometry(rows, columns, image_idx, sub_width, sub_height).translated(translate_by)
                painter.drawImage(painter_geo, image.copy(image_geo.toRect()).mirrored(bool(mirrored), False))

    def progress_to_offset(self, progress: float, rows: int, columns: int):
        return round(rows * columns * progress)


class SnakeIn(SnakeTransition):
    parent_z = 1.0

    def get_sub_filled(self, rows: int, columns: int, offset: int):
        sub_filled = np.zeros(rows * columns, dtype=np.int_)
        sub_filled[:offset] = 1
        sub_filled = sub_filled.reshape((rows, columns))
        sub_filled[1::2] = sub_filled[1::2][:, ::-1]
        return sub_filled.flatten()


class SnakeOut(SnakeTransition):
    ...


class PixelateTransition(Transition):
    max_sub_width = 100
    __sub_width: int | None = None

    def get_sub_images(self, image: QImage, sub_width: int):
        height_mod = image.height() % sub_width
        heights = [sub_width] * int(image.height() / sub_width)
        if height_mod:
            heights = [math.ceil(height_mod / 2)] + heights + [math.floor(height_mod / 2)]
            heights = [h for h in heights if h > 0]

        width_mod = image.width() % sub_width
        widths = [sub_width] * int(image.width() / sub_width)
        if width_mod:
            widths = [math.ceil(width_mod / 2)] + widths + [math.floor(width_mod / 2)]
            widths = [w for w in widths if w > 0]

        y = 0

        for h in heights:
            x = 0
            for w in widths:
                rect = QRect(x, y, w, h)
                sub = image.copy(rect).convertToFormat(QImage.Format.Format_RGBA8888)
                rgba_arr = np.mean(np.array(sub.constBits()).reshape((-1, 4)), axis=0, dtype=np.int_)

                assert isinstance(rgba_arr, np.ndarray)

                rgba = qRgba(rgba_arr[0], rgba_arr[1], rgba_arr[2], rgba_arr[3])
                pixmap = QPixmap(w, h)
                pixmap.fill(rgba)

                yield pixmap, rect
                x += w
            y += h

    def on_progress(self, value: float):
        super().on_progress(value)
        sub_width = round(self.max_sub_width * value)
        if sub_width != self.__sub_width:
            self.__sub_width = sub_width
            self.parent().update(self.parent().rect())

    def paint(self, painter: QPainter, image: QImage, image_rect: QRectF):
        if self.__sub_width and self.__sub_width > 10:
            for sub, rect in self.get_sub_images(image, min(self.__sub_width, min(image.width(), image.height()))):
                painter.drawPixmap(rect, sub)
        else:
            painter.drawImage(self.parent().rect(), image)


class PixelateOut(PixelateTransition):
    start_value = 0.1
    easing = QEasingCurve.Type.OutSine


class PixelateIn(PixelateTransition):
    start_value = 1.0
    end_value = 0.0
    easing = QEasingCurve.Type.InSine
