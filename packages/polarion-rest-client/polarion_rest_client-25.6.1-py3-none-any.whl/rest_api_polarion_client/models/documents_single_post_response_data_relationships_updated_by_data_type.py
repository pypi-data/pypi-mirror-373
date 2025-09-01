from enum import Enum


class DocumentsSinglePostResponseDataRelationshipsUpdatedByDataType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
