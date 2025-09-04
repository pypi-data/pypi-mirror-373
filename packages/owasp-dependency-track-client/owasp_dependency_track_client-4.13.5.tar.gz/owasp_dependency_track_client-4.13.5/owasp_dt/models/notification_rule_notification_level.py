from enum import Enum


class NotificationRuleNotificationLevel(str, Enum):
    ERROR = "ERROR"
    INFORMATIONAL = "INFORMATIONAL"
    WARNING = "WARNING"

    def __str__(self) -> str:
        return str(self.value)
