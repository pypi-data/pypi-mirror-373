from enum import Enum


class ShowBaseType(str, Enum):
    SHOW = "show"

    def __str__(self) -> str:
        return str(self.value)
