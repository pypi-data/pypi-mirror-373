from enum import Enum


class AnalysisAnalysisState(str, Enum):
    EXPLOITABLE = "EXPLOITABLE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    IN_TRIAGE = "IN_TRIAGE"
    NOT_AFFECTED = "NOT_AFFECTED"
    NOT_SET = "NOT_SET"
    RESOLVED = "RESOLVED"

    def __str__(self) -> str:
        return str(self.value)
