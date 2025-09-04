from enum import Enum


class CreateScheduledNotificationRuleRequestNotificationLevel(str, Enum):
    ERROR = "ERROR"
    INFORMATIONAL = "INFORMATIONAL"
    WARNING = "WARNING"

    def __str__(self) -> str:
        return str(self.value)
