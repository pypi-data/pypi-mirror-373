from enum import Enum


class PolicyViolationType(str, Enum):
    LICENSE = "LICENSE"
    OPERATIONAL = "OPERATIONAL"
    SECURITY = "SECURITY"

    def __str__(self) -> str:
        return str(self.value)
