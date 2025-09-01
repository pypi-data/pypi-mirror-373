from enum import Enum


class WorkitemsSingleGetResponseDataRelationshipsLinkedRevisionsDataItemType(str, Enum):
    REVISIONS = "revisions"

    def __str__(self) -> str:
        return str(self.value)
