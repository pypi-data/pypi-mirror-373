from enum import Enum


class UsersListPostRequestDataItemRelationshipsProjectRolesDataItemType(str, Enum):
    PROJECTROLES = "projectroles"

    def __str__(self) -> str:
        return str(self.value)
