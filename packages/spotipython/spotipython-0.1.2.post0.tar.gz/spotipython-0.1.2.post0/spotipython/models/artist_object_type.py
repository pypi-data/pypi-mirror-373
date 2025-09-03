from enum import Enum


class ArtistObjectType(str, Enum):
    ARTIST = "artist"

    def __str__(self) -> str:
        return str(self.value)
