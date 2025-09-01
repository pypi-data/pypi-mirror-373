from enum import Enum


class WorkitemsSingleGetResponseDataRelationshipsLinkedOslcResourcesDataItemType(
    str, Enum
):
    LINKEDOSLCRESOURCES = "linkedoslcresources"

    def __str__(self) -> str:
        return str(self.value)
