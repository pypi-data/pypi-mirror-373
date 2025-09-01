from enum import Enum


class WorkitemsSingleGetResponseDataRelationshipsWatchesDataItemType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
