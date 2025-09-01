from typing import TypeVar


_T = TypeVar("_T")


class NoImagesFound(Exception):
    ...


def first_not_null(*values: _T | None) -> _T:
    for value in values:
        if value is not None:
            return value
    raise TypeError("All values are None")


def first_not_null_or_null(*values: _T | None) -> _T | None:
    for value in values:
        if value is not None:
            return value
    return None
