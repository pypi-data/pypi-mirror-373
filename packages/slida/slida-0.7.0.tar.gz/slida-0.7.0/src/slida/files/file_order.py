import enum


class FileOrder(enum.StrEnum):
    NAME = "name"
    CREATED = "created"
    MODIFIED = "modified"
    RANDOM = "random"
    SIZE = "size"
