from enum import Enum


class PlansListPostRequestDataItemType(str, Enum):
    PLANS = "plans"

    def __str__(self) -> str:
        return str(self.value)
