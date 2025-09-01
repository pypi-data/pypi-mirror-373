from enum import Enum


class CollectionsListGetResponseDataItemRelationshipsProjectDataType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
