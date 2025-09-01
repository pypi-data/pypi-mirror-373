from enum import Enum


class UsergroupsSingleGetResponseDataRelationshipsGlobalRolesDataItemType(str, Enum):
    GLOBALROLES = "globalroles"

    def __str__(self) -> str:
        return str(self.value)
