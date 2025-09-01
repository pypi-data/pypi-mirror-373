from enum import Enum


class PlansSinglePatchRequestDataRelationshipsParentDataType(str, Enum):
    PLANS = "plans"

    def __str__(self) -> str:
        return str(self.value)
