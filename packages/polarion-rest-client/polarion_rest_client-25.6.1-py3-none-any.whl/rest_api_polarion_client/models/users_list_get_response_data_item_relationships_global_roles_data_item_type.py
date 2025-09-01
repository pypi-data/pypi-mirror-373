from enum import Enum


class UsersListGetResponseDataItemRelationshipsGlobalRolesDataItemType(str, Enum):
    GLOBALROLES = "globalroles"

    def __str__(self) -> str:
        return str(self.value)
