from enum import Enum


class CollectionsListPostRequestDataItemRelationshipsUpstreamCollectionsDataItemType(
    str, Enum
):
    COLLECTIONS = "collections"

    def __str__(self) -> str:
        return str(self.value)
