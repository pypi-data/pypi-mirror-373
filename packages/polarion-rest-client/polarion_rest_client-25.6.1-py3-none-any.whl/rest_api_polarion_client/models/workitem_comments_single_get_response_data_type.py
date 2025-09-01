from enum import Enum


class WorkitemCommentsSingleGetResponseDataType(str, Enum):
    WORKITEM_COMMENTS = "workitem_comments"

    def __str__(self) -> str:
        return str(self.value)
