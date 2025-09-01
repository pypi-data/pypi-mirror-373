from enum import Enum


class WorkitemsListGetResponseDataItemRelationshipsPlannedInDataItemType(str, Enum):
    PLANS = "plans"

    def __str__(self) -> str:
        return str(self.value)
