from enum import Enum


class DataClassificationDirection(str, Enum):
    BI_DIRECTIONAL = "BI_DIRECTIONAL"
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
