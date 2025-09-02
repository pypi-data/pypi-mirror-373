from enum import Enum


class AlbumBaseType(str, Enum):
    ALBUM = "album"

    def __str__(self) -> str:
        return str(self.value)
