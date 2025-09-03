from enum import Enum


class ChapterBaseType(str, Enum):
    EPISODE = "episode"

    def __str__(self) -> str:
        return str(self.value)
