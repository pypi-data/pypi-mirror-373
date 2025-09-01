from enum import Enum


class WorkitemsListPatchRequestDataItemRelationshipsLinkedRevisionsDataItemType(
    str, Enum
):
    REVISIONS = "revisions"

    def __str__(self) -> str:
        return str(self.value)
