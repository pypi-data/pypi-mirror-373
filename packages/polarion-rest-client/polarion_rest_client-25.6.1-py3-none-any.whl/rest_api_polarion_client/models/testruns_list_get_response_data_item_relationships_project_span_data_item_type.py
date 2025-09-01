from enum import Enum


class TestrunsListGetResponseDataItemRelationshipsProjectSpanDataItemType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
