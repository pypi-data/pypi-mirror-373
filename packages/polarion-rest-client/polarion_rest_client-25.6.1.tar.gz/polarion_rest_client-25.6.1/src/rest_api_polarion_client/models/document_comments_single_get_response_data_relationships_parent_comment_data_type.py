from enum import Enum


class DocumentCommentsSingleGetResponseDataRelationshipsParentCommentDataType(
    str, Enum
):
    DOCUMENT_COMMENTS = "document_comments"

    def __str__(self) -> str:
        return str(self.value)
