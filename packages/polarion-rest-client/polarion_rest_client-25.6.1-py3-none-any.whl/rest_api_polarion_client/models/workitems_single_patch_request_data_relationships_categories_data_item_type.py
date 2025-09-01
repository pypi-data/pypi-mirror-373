from enum import Enum


class WorkitemsSinglePatchRequestDataRelationshipsCategoriesDataItemType(str, Enum):
    CATEGORIES = "categories"

    def __str__(self) -> str:
        return str(self.value)
