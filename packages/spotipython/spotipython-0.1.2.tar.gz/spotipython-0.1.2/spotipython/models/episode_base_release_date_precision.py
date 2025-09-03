from enum import Enum


class EpisodeBaseReleaseDatePrecision(str, Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"

    def __str__(self) -> str:
        return str(self.value)
