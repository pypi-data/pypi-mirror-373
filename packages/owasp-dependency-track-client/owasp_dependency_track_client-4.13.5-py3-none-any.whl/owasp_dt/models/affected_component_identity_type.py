from enum import Enum


class AffectedComponentIdentityType(str, Enum):
    CPE = "CPE"
    PURL = "PURL"

    def __str__(self) -> str:
        return str(self.value)
