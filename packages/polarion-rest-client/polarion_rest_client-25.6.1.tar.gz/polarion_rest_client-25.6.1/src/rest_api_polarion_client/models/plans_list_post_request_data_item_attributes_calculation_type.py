from enum import Enum


class PlansListPostRequestDataItemAttributesCalculationType(str, Enum):
    CUSTOMFIELDBASED = "customFieldBased"
    TIMEBASED = "timeBased"

    def __str__(self) -> str:
        return str(self.value)
