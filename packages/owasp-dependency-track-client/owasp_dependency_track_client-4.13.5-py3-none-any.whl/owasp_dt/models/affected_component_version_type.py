from enum import Enum


class AffectedComponentVersionType(str, Enum):
    EXACT = "EXACT"
    RANGE = "RANGE"

    def __str__(self) -> str:
        return str(self.value)
