from enum import Enum


class WorkitemsListGetResponseDataItemRelationshipsExternallyLinkedWorkItemsDataItemType(
    str, Enum
):
    EXTERNALLYLINKEDWORKITEMS = "externallylinkedworkitems"

    def __str__(self) -> str:
        return str(self.value)
