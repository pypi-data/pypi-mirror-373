from enum import Enum


class AnalysisAnalysisResponse(str, Enum):
    CAN_NOT_FIX = "CAN_NOT_FIX"
    NOT_SET = "NOT_SET"
    ROLLBACK = "ROLLBACK"
    UPDATE = "UPDATE"
    WILL_NOT_FIX = "WILL_NOT_FIX"
    WORKAROUND_AVAILABLE = "WORKAROUND_AVAILABLE"

    def __str__(self) -> str:
        return str(self.value)
