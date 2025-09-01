from enum import Enum


class PlansListPostRequestDataItemRelationshipsTemplateDataType(str, Enum):
    PLANS = "plans"

    def __str__(self) -> str:
        return str(self.value)
