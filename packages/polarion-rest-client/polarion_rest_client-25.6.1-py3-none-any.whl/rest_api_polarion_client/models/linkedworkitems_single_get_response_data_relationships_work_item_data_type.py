from enum import Enum


class LinkedworkitemsSingleGetResponseDataRelationshipsWorkItemDataType(str, Enum):
    WORKITEMS = "workitems"

    def __str__(self) -> str:
        return str(self.value)
