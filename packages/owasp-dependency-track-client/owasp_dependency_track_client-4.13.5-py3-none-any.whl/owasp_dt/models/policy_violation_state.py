from enum import Enum


class PolicyViolationState(str, Enum):
    FAIL = "FAIL"
    INFO = "INFO"
    WARN = "WARN"

    def __str__(self) -> str:
        return str(self.value)
