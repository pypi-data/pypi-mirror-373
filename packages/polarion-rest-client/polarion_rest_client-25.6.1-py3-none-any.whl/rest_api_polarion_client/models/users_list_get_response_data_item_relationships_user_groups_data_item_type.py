from enum import Enum


class UsersListGetResponseDataItemRelationshipsUserGroupsDataItemType(str, Enum):
    USERGROUPS = "usergroups"

    def __str__(self) -> str:
        return str(self.value)
