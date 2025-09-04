from enum import Enum


class ViolationAnalysisAnalysisState(str, Enum):
    APPROVED = "APPROVED"
    NOT_SET = "NOT_SET"
    REJECTED = "REJECTED"

    def __str__(self) -> str:
        return str(self.value)
