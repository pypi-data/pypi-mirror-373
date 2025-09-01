from enum import Enum


class PlansSinglePatchRequestDataAttributesCalculationType(str, Enum):
    CUSTOMFIELDBASED = "customFieldBased"
    TIMEBASED = "timeBased"

    def __str__(self) -> str:
        return str(self.value)
