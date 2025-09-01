from enum import Enum


class WorkitemApprovalsListPostRequestDataItemRelationshipsUserDataType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
