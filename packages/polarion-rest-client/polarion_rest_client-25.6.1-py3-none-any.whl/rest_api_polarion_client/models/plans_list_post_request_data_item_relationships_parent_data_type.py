from enum import Enum


class PlansListPostRequestDataItemRelationshipsParentDataType(str, Enum):
    PLANS = "plans"

    def __str__(self) -> str:
        return str(self.value)
