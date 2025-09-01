from enum import Enum


class TestrecordAttachmentsSingleGetResponseDataRelationshipsAuthorDataType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
