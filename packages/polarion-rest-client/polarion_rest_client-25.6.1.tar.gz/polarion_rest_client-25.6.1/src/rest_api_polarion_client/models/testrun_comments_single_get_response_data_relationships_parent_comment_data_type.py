from enum import Enum


class TestrunCommentsSingleGetResponseDataRelationshipsParentCommentDataType(str, Enum):
    TESTRUN_COMMENTS = "testrun_comments"

    def __str__(self) -> str:
        return str(self.value)
