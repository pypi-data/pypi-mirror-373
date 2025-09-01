from enum import Enum


class DocumentCommentsListPostRequestDataItemRelationshipsAuthorDataType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
