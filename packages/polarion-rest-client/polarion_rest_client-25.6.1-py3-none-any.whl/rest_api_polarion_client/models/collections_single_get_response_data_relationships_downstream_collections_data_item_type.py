from enum import Enum


class CollectionsSingleGetResponseDataRelationshipsDownstreamCollectionsDataItemType(
    str, Enum
):
    COLLECTIONS = "collections"

    def __str__(self) -> str:
        return str(self.value)
