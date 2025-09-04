from enum import Enum


class GetChildrenProjectsByClassifierSortOrder(str, Enum):
    ASC_DESC = "asc, desc"

    def __str__(self) -> str:
        return str(self.value)
