from enum import Enum


class UsersListPostRequestDataItemRelationshipsGlobalRolesDataItemType(str, Enum):
    GLOBALROLES = "globalroles"

    def __str__(self) -> str:
        return str(self.value)
