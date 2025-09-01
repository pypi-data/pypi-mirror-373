from enum import Enum


class TestrunAttachmentsListDeleteRequestDataItemType(str, Enum):
    TESTRUN_ATTACHMENTS = "testrun_attachments"

    def __str__(self) -> str:
        return str(self.value)
