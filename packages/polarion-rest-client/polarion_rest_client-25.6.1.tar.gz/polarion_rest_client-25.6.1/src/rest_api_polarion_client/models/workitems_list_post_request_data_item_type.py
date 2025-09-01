from enum import Enum


class WorkitemsListPostRequestDataItemType(str, Enum):
    WORKITEMS = "workitems"

    def __str__(self) -> str:
        return str(self.value)
