from enum import Enum


class LinkedworkitemsListDeleteRequestDataItemType(str, Enum):
    LINKEDWORKITEMS = "linkedworkitems"

    def __str__(self) -> str:
        return str(self.value)
