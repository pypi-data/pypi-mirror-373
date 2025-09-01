from enum import Enum


class CollectionsSingleGetResponseDataRelationshipsReusedFromDataType(str, Enum):
    COLLECTIONS = "collections"

    def __str__(self) -> str:
        return str(self.value)
