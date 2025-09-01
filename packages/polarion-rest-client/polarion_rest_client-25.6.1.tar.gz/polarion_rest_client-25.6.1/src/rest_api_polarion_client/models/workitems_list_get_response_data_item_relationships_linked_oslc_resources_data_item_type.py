from enum import Enum


class WorkitemsListGetResponseDataItemRelationshipsLinkedOslcResourcesDataItemType(
    str, Enum
):
    LINKEDOSLCRESOURCES = "linkedoslcresources"

    def __str__(self) -> str:
        return str(self.value)
