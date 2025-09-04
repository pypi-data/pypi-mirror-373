from enum import Enum


class NotificationRuleTriggerType(str, Enum):
    EVENT = "EVENT"
    SCHEDULE = "SCHEDULE"

    def __str__(self) -> str:
        return str(self.value)
