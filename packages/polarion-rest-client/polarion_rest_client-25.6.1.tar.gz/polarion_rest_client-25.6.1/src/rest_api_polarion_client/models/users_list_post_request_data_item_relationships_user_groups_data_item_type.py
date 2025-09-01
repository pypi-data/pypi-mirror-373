from enum import Enum


class UsersListPostRequestDataItemRelationshipsUserGroupsDataItemType(str, Enum):
    USERGROUPS = "usergroups"

    def __str__(self) -> str:
        return str(self.value)
