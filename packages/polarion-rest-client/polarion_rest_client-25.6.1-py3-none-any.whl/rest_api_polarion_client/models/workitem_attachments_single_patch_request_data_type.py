from enum import Enum


class WorkitemAttachmentsSinglePatchRequestDataType(str, Enum):
    WORKITEM_ATTACHMENTS = "workitem_attachments"

    def __str__(self) -> str:
        return str(self.value)
