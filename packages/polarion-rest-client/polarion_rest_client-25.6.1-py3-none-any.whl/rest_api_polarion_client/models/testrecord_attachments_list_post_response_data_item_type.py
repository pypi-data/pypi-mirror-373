from enum import Enum


class TestrecordAttachmentsListPostResponseDataItemType(str, Enum):
    TESTRECORD_ATTACHMENTS = "testrecord_attachments"

    def __str__(self) -> str:
        return str(self.value)
