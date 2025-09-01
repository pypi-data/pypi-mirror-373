from enum import Enum


class ExternallylinkedworkitemsListDeleteRequestDataItemType(str, Enum):
    EXTERNALLYLINKEDWORKITEMS = "externallylinkedworkitems"

    def __str__(self) -> str:
        return str(self.value)
