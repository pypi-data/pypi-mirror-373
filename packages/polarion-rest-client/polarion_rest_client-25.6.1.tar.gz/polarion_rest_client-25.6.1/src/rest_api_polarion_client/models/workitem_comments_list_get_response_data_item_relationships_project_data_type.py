from enum import Enum


class WorkitemCommentsListGetResponseDataItemRelationshipsProjectDataType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
