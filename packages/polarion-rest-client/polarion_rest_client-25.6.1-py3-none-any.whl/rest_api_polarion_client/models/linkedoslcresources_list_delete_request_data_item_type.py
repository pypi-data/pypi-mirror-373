from enum import Enum


class LinkedoslcresourcesListDeleteRequestDataItemType(str, Enum):
    LINKEDOSLCRESOURCES = "linkedoslcresources"

    def __str__(self) -> str:
        return str(self.value)
