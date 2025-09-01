from enum import Enum


class PlansSingleGetResponseDataRelationshipsParentDataType(str, Enum):
    PLANS = "plans"

    def __str__(self) -> str:
        return str(self.value)
