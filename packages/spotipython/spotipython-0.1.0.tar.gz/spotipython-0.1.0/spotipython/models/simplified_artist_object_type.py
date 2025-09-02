from enum import Enum


class SimplifiedArtistObjectType(str, Enum):
    ARTIST = "artist"

    def __str__(self) -> str:
        return str(self.value)
