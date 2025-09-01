from enum import Enum


class DocumentsSinglePostResponseDataRelationshipsAttachmentsDataItemType(str, Enum):
    DOCUMENT_ATTACHMENTS = "document_attachments"

    def __str__(self) -> str:
        return str(self.value)
