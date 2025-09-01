from enum import Enum


class UsersSingleGetResponseDataRelationshipsGlobalRolesDataItemType(str, Enum):
    GLOBALROLES = "globalroles"

    def __str__(self) -> str:
        return str(self.value)
