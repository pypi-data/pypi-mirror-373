from enum import Enum


class TestrunAttachmentsSingleGetResponseDataRelationshipsAuthorDataType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
