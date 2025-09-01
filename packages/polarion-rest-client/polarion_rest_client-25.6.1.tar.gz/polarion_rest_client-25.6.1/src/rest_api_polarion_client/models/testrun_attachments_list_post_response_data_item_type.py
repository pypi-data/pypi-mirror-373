from enum import Enum


class TestrunAttachmentsListPostResponseDataItemType(str, Enum):
    TESTRUN_ATTACHMENTS = "testrun_attachments"

    def __str__(self) -> str:
        return str(self.value)
