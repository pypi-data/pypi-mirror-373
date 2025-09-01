from enum import Enum


class PlansSinglePatchRequestDataRelationshipsWorkItemsDataItemType(str, Enum):
    WORKITEMS = "workitems"

    def __str__(self) -> str:
        return str(self.value)
