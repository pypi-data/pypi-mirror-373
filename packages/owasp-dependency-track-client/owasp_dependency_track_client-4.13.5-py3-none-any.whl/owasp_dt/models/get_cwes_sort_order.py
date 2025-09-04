from enum import Enum


class GetCwesSortOrder(str, Enum):
    ASC_DESC = "asc, desc"

    def __str__(self) -> str:
        return str(self.value)
