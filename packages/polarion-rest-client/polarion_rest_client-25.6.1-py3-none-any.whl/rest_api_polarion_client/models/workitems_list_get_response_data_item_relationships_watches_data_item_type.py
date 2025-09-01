from enum import Enum


class WorkitemsListGetResponseDataItemRelationshipsWatchesDataItemType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
