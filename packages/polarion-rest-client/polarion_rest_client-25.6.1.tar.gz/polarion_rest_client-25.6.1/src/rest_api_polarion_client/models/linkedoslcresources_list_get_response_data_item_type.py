from enum import Enum


class LinkedoslcresourcesListGetResponseDataItemType(str, Enum):
    LINKEDOSLCRESOURCES = "linkedoslcresources"

    def __str__(self) -> str:
        return str(self.value)
