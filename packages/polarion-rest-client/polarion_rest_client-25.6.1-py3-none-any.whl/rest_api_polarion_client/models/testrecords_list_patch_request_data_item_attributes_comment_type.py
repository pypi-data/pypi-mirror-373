from enum import Enum


class TestrecordsListPatchRequestDataItemAttributesCommentType(str, Enum):
    TEXTHTML = "text/html"
    TEXTPLAIN = "text/plain"

    def __str__(self) -> str:
        return str(self.value)
