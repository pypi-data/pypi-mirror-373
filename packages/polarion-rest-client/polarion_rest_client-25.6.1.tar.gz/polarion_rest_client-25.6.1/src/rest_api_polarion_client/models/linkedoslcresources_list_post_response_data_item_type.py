from enum import Enum


class LinkedoslcresourcesListPostResponseDataItemType(str, Enum):
    LINKEDOSLCRESOURCES = "linkedoslcresources"

    def __str__(self) -> str:
        return str(self.value)
