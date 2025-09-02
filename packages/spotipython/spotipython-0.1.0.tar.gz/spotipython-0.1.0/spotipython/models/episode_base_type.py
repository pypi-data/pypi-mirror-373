from enum import Enum


class EpisodeBaseType(str, Enum):
    EPISODE = "episode"

    def __str__(self) -> str:
        return str(self.value)
