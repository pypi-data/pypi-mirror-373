from enum import Enum


class NotificationRuleScope(str, Enum):
    PORTFOLIO = "PORTFOLIO"
    SYSTEM = "SYSTEM"

    def __str__(self) -> str:
        return str(self.value)
