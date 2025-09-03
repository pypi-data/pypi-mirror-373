from enum import Enum


class GetUsersTopArtistsAndTracksType(str, Enum):
    ARTISTS = "artists"
    TRACKS = "tracks"

    def __str__(self) -> str:
        return str(self.value)
