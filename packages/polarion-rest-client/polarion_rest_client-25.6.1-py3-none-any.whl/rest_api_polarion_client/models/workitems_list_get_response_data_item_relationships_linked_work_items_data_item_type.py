from enum import Enum


class WorkitemsListGetResponseDataItemRelationshipsLinkedWorkItemsDataItemType(
    str, Enum
):
    LINKEDWORKITEMS = "linkedworkitems"

    def __str__(self) -> str:
        return str(self.value)
