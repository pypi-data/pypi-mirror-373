from enum import Enum


class TestrunsListPostRequestDataItemRelationshipsProjectSpanDataItemType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
