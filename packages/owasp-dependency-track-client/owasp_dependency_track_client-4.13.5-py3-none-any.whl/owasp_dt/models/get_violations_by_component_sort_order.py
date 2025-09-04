from enum import Enum


class GetViolationsByComponentSortOrder(str, Enum):
    ASC_DESC = "asc, desc"

    def __str__(self) -> str:
        return str(self.value)
