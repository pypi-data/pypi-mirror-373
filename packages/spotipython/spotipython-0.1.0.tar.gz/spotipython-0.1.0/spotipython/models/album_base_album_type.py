from enum import Enum


class AlbumBaseAlbumType(str, Enum):
    ALBUM = "album"
    COMPILATION = "compilation"
    SINGLE = "single"

    def __str__(self) -> str:
        return str(self.value)
