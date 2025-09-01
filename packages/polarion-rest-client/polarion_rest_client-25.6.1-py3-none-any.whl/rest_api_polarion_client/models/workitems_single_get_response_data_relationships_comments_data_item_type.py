from enum import Enum


class WorkitemsSingleGetResponseDataRelationshipsCommentsDataItemType(str, Enum):
    WORKITEM_COMMENTS = "workitem_comments"

    def __str__(self) -> str:
        return str(self.value)
