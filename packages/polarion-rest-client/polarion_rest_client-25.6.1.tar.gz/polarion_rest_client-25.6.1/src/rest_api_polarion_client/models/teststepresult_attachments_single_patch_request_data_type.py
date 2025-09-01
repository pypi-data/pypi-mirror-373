from enum import Enum


class TeststepresultAttachmentsSinglePatchRequestDataType(str, Enum):
    TESTSTEPRESULT_ATTACHMENTS = "teststepresult_attachments"

    def __str__(self) -> str:
        return str(self.value)
