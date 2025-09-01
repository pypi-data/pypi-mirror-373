from enum import Enum


class DocumentCommentsListPostRequestDataItemType(str, Enum):
    DOCUMENT_COMMENTS = "document_comments"

    def __str__(self) -> str:
        return str(self.value)
