from enum import Enum


class DocumentAttachmentsSingleGetResponseDataType(str, Enum):
    DOCUMENT_ATTACHMENTS = "document_attachments"

    def __str__(self) -> str:
        return str(self.value)
