from enum import Enum


class UsersSingleGetResponseDataRelationshipsProjectRolesDataItemType(str, Enum):
    PROJECTROLES = "projectroles"

    def __str__(self) -> str:
        return str(self.value)
