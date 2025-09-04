from enum import Enum


class CreateScheduledNotificationRuleRequestScope(str, Enum):
    PORTFOLIO = "PORTFOLIO"
    SYSTEM = "SYSTEM"

    def __str__(self) -> str:
        return str(self.value)
