from enum import Enum


class CollectionsListPostRequestDataItemType(str, Enum):
    COLLECTIONS = "collections"

    def __str__(self) -> str:
        return str(self.value)
