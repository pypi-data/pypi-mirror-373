from enum import Enum


class AudiobookBaseType(str, Enum):
    AUDIOBOOK = "audiobook"

    def __str__(self) -> str:
        return str(self.value)
