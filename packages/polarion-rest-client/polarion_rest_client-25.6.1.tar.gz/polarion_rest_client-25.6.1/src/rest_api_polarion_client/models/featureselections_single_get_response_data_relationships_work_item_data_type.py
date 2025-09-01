from enum import Enum


class FeatureselectionsSingleGetResponseDataRelationshipsWorkItemDataType(str, Enum):
    WORKITEMS = "workitems"

    def __str__(self) -> str:
        return str(self.value)
