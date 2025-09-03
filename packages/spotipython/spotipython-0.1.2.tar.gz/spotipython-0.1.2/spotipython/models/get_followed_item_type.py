from enum import Enum


class GetFollowedItemType(str, Enum):
    ARTIST = "artist"

    def __str__(self) -> str:
        return str(self.value)
