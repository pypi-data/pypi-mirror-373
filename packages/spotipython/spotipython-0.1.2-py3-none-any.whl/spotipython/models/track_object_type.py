from enum import Enum


class TrackObjectType(str, Enum):
    TRACK = "track"

    def __str__(self) -> str:
        return str(self.value)
